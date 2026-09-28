---
title: Adapters
slug: files-adapters
section: Files
order: 40
summary: The agent adapters: the LangChain adapter that calls the model and its search tool, the provider registry, and the fixture adapter used by tests.
---

`adapters/` is where an agent is actually called. Every adapter satisfies one contract,
`core.contracts.AgentAdapter`: a callable `(subject, context, directive) -> AgentResponse` that
either returns a structurally valid response or raises `core.parsing.StructuralParseError`. The
validation loop in [[pipeline/middleware.py]] calls adapters through that contract and nothing
else, so it never knows which model it is talking to. A second contract, `core.contracts.ModelCall`
(`(system, user) -> str`), covers the one plain model call the system makes outside the agent
loop: the assessment extraction.

**Dependency rule.** `adapters/` may import only from `core/`. This is enforced by
`tests/test_layering.py` (`_ALLOWED["adapters"] = {"core"}`), which reads imports from the syntax
tree rather than by importing. Adapters are one of the two packages allowed to reach the network
(the other is `datasources/`): the LangChain adapter talks to the model server and to the Tavily
search API.

**How the files fit together.**

- [[adapters/langchain_adapter.py]] is the only real adapter. It drives a local Ollama model or a
  Gemini model through LangChain, optionally with a Tavily search tool, and also builds the plain
  model call used for assessment extraction.
- [[adapters/registry.py]] maps a provider name to a factory. There is one provider,
  `"langchain"`; the registry is kept as a seam so callers never import the adapter module
  directly. [[web/server.py]] builds every adapter and model call through it.
- [[adapters/fixture_adapter.py]] is a deterministic stand-in used only by tests. It is never
  registered.
- [[adapters/__init__.py]] holds only the package docstring.

The adapters that used to sit beside these (`gemini_adapter.py`, `ollama_adapter.py`,
`mock_adapter.py`) are archived under `archive/adapters/`, not deleted, and are no longer
reachable (`logs/RUN_LOG.md`, 2026-09-23, "Make LangChain the sole agent framework; replace the
MCP fetch tool with Tavily search; frontend drops all model/provider selection").

## `adapters/__init__.py`

**Role:** package marker; its docstring states the adapter contract and points to the registry.

The file has no code. The docstring records that the contract used to be described only in a
comment here, which meant nothing could be annotated against it; it is now the named `Protocol`
`core.contracts.AgentAdapter`, and every factory in the package declares it as its return type.
That move happened in the 2026-09-04 restructure (`logs/RUN_LOG.md`, 2026-09-04, "SOLID
restructure: layered packages, no loose root modules, three duplications removed").

Related: [[core/contracts.py]], [[adapters/registry.py]]

## `adapters/fixture_adapter.py`

**Role:** a deterministic, test-only agent whose conclusion is chosen by the caller, for testing
code that consumes a conclusion (the cross-agent comparison, fact extraction).

`make_fixture_adapter(conclusion, thought_log=None)` returns an `AgentAdapter` that ignores its
subject, context and directive and always returns the same response. The text is wrapped in the
two required blocks (`<thought_log>` and `<conclusion>`) and passed through the real parser,
`core.parsing._parse_response`, so a fixture response is structurally the same as a live response
that passed validation. Because the correct answer is fixed before the test runs, a test can assert
exactly what the comparator should conclude.

### Key functions
- `make_fixture_adapter(conclusion, thought_log=None)`: raises `ValueError` at construction, not at
  call time, when `conclusion` is empty or blank, when an explicitly given `thought_log` is blank, or
  when either text contains any of the four block tags (`_FORBIDDEN`). The docstring and comment give
  the reason: a closing tag inside the text would end its block early and leave stray text outside
  the blocks, which the parser rejects, and a clear error at construction is easier to diagnose than
  a parse failure later. When `thought_log` is omitted, a fixed placeholder says the reasoning is not
  generated and carries no evidence.

### Design notes
- It is distinct from `tests/support.py`'s `make_scripted_adapter`. That one exercises the ADR-07
  retry-then-halt guardrail (parse failure, retry, halt), where the caller does not control the
  conclusion; this one fixes the conclusion (module docstring).
- It stays in `adapters/` rather than `tests/` because it satisfies the same contract as the real
  adapter and existed here before `tests/support.py` did (module docstring). The 2026-09-22 entry
  "Remove all mock/scripted features from the running app; convert remaining test doubles to
  explicit dependency-injection, not simulated LLM answers" in `logs/RUN_LOG.md` records the decision
  to leave it in place and that its relocation into `tests/` was not done.
- It parses with the parser's default, `allow_assessment=False`, so a fixture cannot carry an
  `<assessment>` block.

### Limits and open issues
- Test-only by convention: nothing stops production code importing it, and no test asserts that it
  stays out of [[adapters/registry.py]]. Today it is imported only from `tests/` (for example
  `tests/test_cross_validation.py`, `tests/test_concurrency_and_stream.py`,
  `tests/test_real_run_corpus.py`, `tests/test_facts.py`).

Related: [[core/parsing.py]], [[tests/support.py]], [[validation/cross_validation.py]]

## `adapters/langchain_adapter.py`

**Role:** the one real agent adapter. It calls a local Ollama model or a Gemini model through
LangChain, gives the agent a Tavily search tool when a key is configured, reports every tool call
to the caller, bounds each model call with a stall timeout, and parses the reply against the
structural contract. It also builds the plain model call used for assessment extraction.

This module is a deliberate exception to the subsystem's stdlib-only rule. It depends on
`langchain-core`, `langchain-ollama`, `langchain-google-genai` and `langchain-tavily`, and imports
them inside functions so that nothing else needs them unless the adapter is used (module
docstring). There is no scripted or simulated mode: if the model is unreachable or errors, the
adapter raises rather than returning a canned response.

### How a call works

`make_langchain_adapter(model="llama3.2", temperature=0.0, seed=42, use_tools=True,
on_tool_event=None)` returns the adapter. Each call:

1. Decides whether tools are active: `use_tools` and `TAVILY_API_KEY` set in the environment. The
   key is read on every call, not at construction.
2. Builds the user prompt: `Subject: ...`, then, if the context is not blank, `Context:` followed by
   the first `CONTEXT_CHAR_LIMIT` (6,000) characters of the context. When tools are active it
   appends a paragraph telling the model it has a search tool, that it must search before answering
   "insufficient context", that a search result counts as a source of fact and is cited like the
   context (`[SOURCE: <label>, <url>]`), that it must invoke the tool rather than write the call out
   as text, and that only its final response needs to be the two XML blocks.
3. Sends two messages: the directive's text as the system message, and the prompt as the user
   message.
4. Builds a chat model with `_build_chat` and either calls it once (no tools) or runs the tool
   loop, `_invoke_with_tools`.
5. Parses the reply with `core.parsing._parse_response`. The `allow_assessment` flag comes from
   `core.assessment.expects_assessment(directive.version)`, so the optional `<assessment>` block is
   accepted only under a directive that asks for it. With tools active, parsing goes through
   `_parse_across_turns` (below).

Errors: a missing `GEMINI_API_KEY` raises `EnvironmentError` unchanged ("a config problem, not a
connection failure", inline comment). Any other exception from building or calling the model, or
from the tool loop, is wrapped by `_connection_error` into `LangchainConnectionError`, or
`LangchainTimeoutError` if the cause was a timeout. A reply that fails the structural contract
raises `StructuralParseError`, which is the signal the ADR-07 loop in [[pipeline/middleware.py]]
retries on. [[web/server.py]] catches `LangchainConnectionError` and records the run as halted with
the error.

### Model family inference

There is no provider choice. `_build_chat(model, temperature, seed)` is the one place the family is
decided: a model name containing "gemini" (case-insensitive) builds `ChatGoogleGenerativeAI` with
`GEMINI_API_KEY`; any other name builds `ChatOllama` at `OLLAMA_HOST` (default
`http://localhost:11434`). The Gemini class has no seed parameter, so on that path the seed is not
applied; the inline comment explains that the caller passes it anyway because the shared seed control
does not know which family a name maps to. The default model name for the web app comes from
`LANGCHAIN_MODEL` (read in [[web/server.py]]), with `llama3.2` as the fallback.

The decision to make LangChain the only framework, keep Gemini only as a model LangChain drives, and
reuse `GEMINI_API_KEY` rather than add a second key is recorded in `logs/RUN_LOG.md`, 2026-09-23,
"Make LangChain the sole agent framework; replace the MCP fetch tool with Tavily search; frontend
drops all model/provider selection".

### The Tavily tool loop

`_invoke_with_tools(chat, messages, on_tool_event)` binds one tool, `TavilySearch(max_results=5)`,
to the chat model and loops at most `_MAX_TOOL_ITERATIONS` (4) times:

1. Call the model with the message history and append its reply.
2. If the reply has no tool calls, return it.
3. For each tool call: emit a `started` event, run the tool through `_call_tool`, emit a
   `finished` event, and append a `ToolMessage` holding the result as text.

If the fourth reply still asks for tools, those tools are run and their results appended, but the
model is not called again; the loop returns that fourth reply as it is ("ran out of iterations;
return the last response anyway"). The cap exists so "a confused model can't loop forever" (comment
on the constant). A tool name other than Tavily's produces an `Unknown tool` error result rather than
an exception.

`_call_tool(tool, args, query)` handles the ways a search can fail:

- `_sanitize_tool_args` first drops any argument whose value is a placeholder string such as "None"
  or "N/A" (`_NULL_STRINGS`, compared case-insensitively). llama3.2 was seen sending these for
  optional list arguments, which Tavily's argument schema rejects. The set is "an observed set, not
  an exhaustive enum" (comment).
- If the call raises, or returns an error, it is retried once with only `{"query": query}`. The
  docstring's reason: the model can send other arguments the API rejects, and one bounded retry with
  the one required argument covers those cases "without growing a blocklist forever".
- `_returned_error` treats a returned `{"error": ...}` dict with no results as a failure. Tavily
  reports some failures, including an HTTP 400, by returning such a dict instead of raising; before
  this check every such call was recorded as `ok` and the error text was handed to the model as a
  search result.
- If the retry fails too, the result is the text `Tool error: ...` with status `error`. It is handed
  to the model as the tool's result; it does not raise.

Returns `(result, status, retried)`. The placeholder fix and the query-only retry are recorded in
`logs/RUN_LOG.md`, 2026-09-23, "Configure TAVILY_API_KEY; find and fix two real tool-call bugs the
key finally let us see"; the returned-error fix in 2026-09-24, "B0: period- and unit-aware facts; a
retired revenue tag; tool errors recorded as "ok"". Both were found on live runs.

### Tool events

When `on_tool_event` is given, it receives two dictionaries per tool call, in the order the calls
happened. Both carry `seq` (numbered from 1 within one tool loop), `tool`, `url` (always `None`: a
search has a query, not a URL; the key is kept from the earlier fetch tool so the step-trace wiring
did not change), `query` and `args`.

- `phase: "started"`: `status` is always `"ok"`, and `result_preview` and `duration_ms` are `None`.
  It is sent before the search runs, so a slow or hung search shows in the live trace while it is
  happening.
- `phase: "finished"`: adds `status` (`ok` or `error`), `retried_query_only`, `result_preview` (the
  first 300 characters of the result text), `urls` (from `_result_urls`, in rank order), `results`
  (from `_result_snippets`: per result, its URL, title and the first 600 characters of its content)
  and `duration_ms`.

The callback is called synchronously from whichever thread runs the loop. [[web/server.py]] passes
it by putting a private `_on_tool_event` key into a per-call copy of the config (see
[[adapters/registry.py]]) and records each event as a step in [[web/step_trace.py]]. The per-result
snippets exist so a citation to a web page can later be shown beside the text the agent actually
read, without re-fetching a page that may have changed (`_result_snippets` docstring; added in
`logs/RUN_LOG.md`, 2026-09-25, "BP + U4: figures located in the filing, and live compare runs in
/app"). The accountability layer never takes the agent's own account of its searches on trust:
[[validation/verification.py]] still checks every citation independently afterwards (module
docstring).

### Parsing replies that span tool turns

`_parse_across_turns(contents, allow_assessment=False)` receives the text of every assistant
message in the loop. It parses the final message first, which is the old behaviour. If that fails,
it parses all the model's non-empty messages joined in order; nothing is added. If that fails too,
the `StructuralParseError` carries the joined text as the raw output, so the audit trail shows
everything the model wrote. The reason, from its docstring: llama3.2 sometimes opened
`<thought_log>` in the same message that called the search tool and finished it after the results
came back, and parsing only the final message recorded a complete response as "missing
`<thought_log>`" (`logs/RUN_LOG.md`, 2026-09-24, "B1 + U2: figure-by-figure comparison (metric,
period, derivations) and the matrix UI").

### The stall timeout

`MODEL_TIMEOUT_S` (environment variable, default 120, read once at import) is how many seconds a
model call may go without receiving anything before it is abandoned. It is passed to ChatOllama's
httpx client (`client_kwargs={"timeout": ...}`) and as Gemini's `timeout`. ChatOllama always
streams, so for Ollama this is a stall limit, not a cap on the call's total length; for Gemini it is
the request timeout (comment on the constant).

- `_is_timeout(exc)` walks the exception's `__cause__` and `__context__` chain, so a timeout wrapped
  in another exception is still recognised.
- `_connection_error` turns a timeout into `LangchainTimeoutError`, whose message says how long it
  waited, and anything else into `LangchainConnectionError` ("Cannot reach model ...").
  `LangchainTimeoutError` subclasses `LangchainConnectionError`, so existing handlers in
  [[web/server.py]] record a timed-out run as halted without any change.

Why it exists and why 120 s: Ollama stopped responding during compare runs four times with no limit
at all (Honest Ledger `ollama-hangs-under-compare`), and 120 s is above the slowest successful LLM
attempt stored as of 2026-09-27, 85.3 s over 56 attempts (comment on the constant, and
`logs/RUN_LOG.md`, 2026-09-27, "A model-call timeout, and a ledger refresh that found two wrong
claims"). `tests/test_model_timeout.py` runs the real ChatOllama and httpx client against a stub
server on 127.0.0.1: a server that never answers ends both the agent call and the extraction call
with `LangchainTimeoutError`; a slow but steady stream longer than the limit in total still
succeeds; a refused connection is reported as unreachable, not as a timeout; a wrapped timeout is
recognised; and the limit reaches the Ollama client.

### The plain model call for assessment extraction

`make_langchain_model_call(model="llama3.2", temperature=0.0, seed=42)` returns a
`core.contracts.ModelCall`: `(system, user) -> str`. It uses the same `_build_chat`, so the same
model family and timeout, but no tools, no directive and no structural parsing. A non-string reply
content is converted with `str()`. It raises `LangchainConnectionError` (or the timeout subclass)
when the model cannot be reached; the caller in [[core/assessment.py]] records that as
`extraction_failed` rather than failing the run (docstring). It is built through
`adapters.registry.build_model_call` and used in ticker-mode compare runs, one call per agent. The
human's choice of a separate extraction call is recorded in `logs/RUN_LOG.md`, 2026-09-26, "Option 1
(assessment extraction) + B5 + U8: grades, why they differ, and who sets them".

### Running inside an event loop

`_run_async(coro)` runs the async tool loop from the adapter's synchronous call. When no event loop
is running in the thread it uses `asyncio.run`; when one is (the FastAPI route handlers in
[[web/server.py]] call the validation loop synchronously from inside `async def`), it runs
`asyncio.run` on a fresh single-worker thread, because `asyncio.run` raises inside a running loop
(docstring).

### Design notes
- Tavily replaced an earlier tool that fetched a known URL over MCP: a search finds information
  about a subject without the caller knowing the exact URL (module docstring; `logs/RUN_LOG.md`,
  2026-09-23 entry named above).
- `TavilySearch` validates its key in its constructor and raises at once if it is missing. The key
  check sits in the adapter call so that a missing key degrades that call to no tools instead of
  failing every request. This is a visible gap, not a silent success:
  `ProviderSpec.supports_tools()` in [[adapters/registry.py]] and `_tool_capability_warning` in
  [[web/server.py]] tell the user (module docstring and inline comment).
- The search-first paragraph lives in the adapter, not in the shared directive, because tool
  availability is specific to this adapter. It amends the directive's grounding rule for this call
  because models were seen answering "insufficient context" after a search had returned a correct
  result (inline comment; `logs/RUN_LOG.md`, 2026-09-23, "Make the agent search first instead of
  defaulting to "insufficient context"").
- Failure types were collapsed on purpose: rate limits, missing models and refused connections all
  surface as `LangchainConnectionError` with one wording (2026-09-23 LangChain entry, open issues).
  Timeouts were split back out on 2026-09-27.

### Limits and open issues
- `ollama-hangs-under-compare` (OPEN): the timeout ends a hung call; it does not fix the hang, whose
  cause is unconfirmed, and whether Ollama stays wedged after a timeout has not been tested.
- `gemini-key-unconfirmed` (OPEN): the Gemini path is wired and was seen making a real API call,
  which returned a suspended-key error; no successful Gemini reply is recorded.
- `ollama-determinism` (OPEN): seed plus temperature 0 did not give reproducible output in live
  tests. The ledger entry names the archived `ollama_adapter.py`; this adapter passes the same two
  settings, and nothing records a separate determinism test of it.
- The context is cut to 6,000 characters without a marker in the prompt; the model is not told it
  was truncated. The constant was carried over from the archived Ollama adapter (comment).
- `_parse_across_turns` looks only at messages whose content is a string; the no-tools path passes
  `result.content` to the parser as it is. Whether any model family used here returns non-string
  content was not checked for this page.
- Finding: in Python 3, `EnvironmentError` is another name for `OSError`. The `except
  EnvironmentError: raise` clauses meant for a missing `GEMINI_API_KEY` therefore also pass through,
  unwrapped, any `OSError` subclass raised by the model client, including the built-in
  `ConnectionError` and `TimeoutError`. Such an error would not become `LangchainConnectionError` or
  `LangchainTimeoutError`. The timeout tests pass because httpx's own timeout errors are not
  `OSError`. The refused-connection test in [[tests/test_model_timeout.py]] builds the httpx error
  directly rather than opening a real socket.
  - **Checked 2026-09-27, by hand (not in the suite):** a real refused socket on Windows, through
    the real ChatOllama streaming path, came back as `LangchainConnectionError` ("Cannot reach
    model ... [WinError 10061]") from both the plain model call and the adapter. The raw error was
    httpx's, not an `OSError`.
  - **Still possible:** the `ollama` client does convert `httpx.ConnectError` to the built-in
    `ConnectionError` in some of its request paths (`ollama/_client.py`). A path that did so would
    reach `except EnvironmentError: raise` and be reported as a configuration error. Gemini's
    client was not checked.
- Each call builds a new chat model (the 2026-09-27 entry measured about 0.5 s of client setup in the
  stub test and left it unchanged).
- Tool-event `seq` restarts at 1 in each tool loop, so it orders events within one agent attempt,
  not across attempts.
- `use_tools` is not reachable through [[adapters/registry.py]], which never passes it, so every
  registry-built adapter uses tools whenever the key is set.
- The model does not always use a successful search result (recorded live with llama3.2 in the
  2026-09-23 Tavily entry); that is model behaviour the adapter cannot correct.
- Documentation disagreement: `README.md`'s row for this file says it has a scripted, network-free
  mode driven by `failure_mode` and LangChain's `GenericFakeChatModel`, and that its only extra
  dependencies are `langchain-core` and `langchain-ollama`. The code has no `failure_mode` and no
  fake model, and imports four LangChain packages.

Related: [[adapters/registry.py]], [[core/contracts.py]], [[core/parsing.py]],
[[core/assessment.py]], [[pipeline/middleware.py]], [[web/step_trace.py]],
[[tests/test_model_timeout.py]], [[tests/test_concurrency_and_stream.py]]

## `adapters/registry.py`

**Role:** the provider registry: maps a provider name to the factory that builds its adapter, the
config key it reads its model from, and its display label. Every adapter and model call in the web
app is built through it.

There is one entry, `"langchain"`. The module is kept as a single-entry seam rather than inlined
into [[web/server.py]], so that a second framework, if one is ever added, costs one `ProviderSpec`
entry instead of a rewrite of every caller (module docstring). Before the 2026-09-04 restructure,
adapter construction and provider labels were written separately in the web routes and the scripts
(`logs/RUN_LOG.md`, 2026-09-04, "SOLID restructure ..."); the registry replaced those copies, and on
2026-09-23 it was cut from three providers to one (the LangChain entry of that date).

### Key functions and classes
- `ProviderSpec`: a frozen dataclass with `name`, `model_key`, `default_model`, `build`, `describe`
  and `supports_tools`. `supports_tools` is a callable, not a fixed value. With one framework the
  question is no longer whether the provider can call tools (always yes) but whether that ability is
  usable right now, which depends on live environment state; for `langchain` it is
  `_tavily_configured()`, true when `TAVILY_API_KEY` is set (docstring).
- `PROVIDERS`: the dict of specs. `_build_langchain` passes `model` (default `llama3.2`),
  `temperature` (default 0.0), `seed` (default 42) and `_on_tool_event` to
  `make_langchain_adapter`. `_on_tool_event` is a private key a caller puts into a per-call copy of
  the config, never into the shared config dict, because that dict is serialised with `json.dumps`
  into the run's `config_snapshot` and a callable would break it (inline comment).
- `resolve(provider)`: returns the spec, or raises `ValueError` naming every valid provider; a bare
  `KeyError` would not be actionable (`tests/test_adapter_registry.py`).
- `build_adapter(config)`: `resolve(config["provider"]).build(config)`.
- `build_model_call(config)`: the plain model call for assessment extraction, on the same model,
  temperature and seed as the config's agent. It checks the provider name and then calls
  `make_langchain_model_call` directly.
- `model_label(config)`: `provider:model`, for example `langchain:llama3.2`, used in the step trace,
  the UI and each compare run's producer metadata (where [[web/server.py]] also sets `same_model`
  by comparing the two labels).
- `with_model_override(config, model=None)`: a shallow copy with a producer's model name written to
  the key the provider reads. With no model, or a provider whose `model_key` is `None`, the copy is
  unchanged; the test for this names the bug it prevents: a model written to a key nothing reads
  gives a config that looks overridden and behaves as if it was not. The original config is not
  changed.
- `provider_names()`: the valid names, so callers ask rather than assume.

### How other layers use it
[[web/server.py]] aliases `build_adapter`, `build_model_call`, `model_label` and
`with_model_override` and calls `resolve(...).supports_tools()` in `_tool_capability_warning`, which
warns when the input contains a URL and search is not configured. The web config fixes `provider` to
`"langchain"`; it stays in the config only because these functions read it.

### Tests
`tests/test_adapter_registry.py` checks that every registered provider builds without credentials
(construction does no key or connection check, so the suite stays network-free), that an unknown
provider's error names the valid set, that each spec's key matches its name and declares
`model_key` and `default_model` together, that `supports_tools` is a callable returning a bool,
labels and their defaults, the override behaviour, and that a provider added to `PROVIDERS` at run
time is immediately resolvable, buildable and labelled.

### Limits and open issues
- `build_model_call` does not go through `ProviderSpec`: it calls the LangChain factory directly. A
  second provider would need this function changed as well as a new entry, so the "one entry" claim
  in the module docstring holds for agents, not for the extraction call.
- `default_model` is declared on the spec but `_build_langchain`, the `describe` lambda and
  `build_model_call` each repeat the literal `"llama3.2"` rather than reading it.
- Finding: `scripts/run_cross_agent_live.py` and `scripts/run_overlap_concept_live.py` still import
  `adapters.gemini_adapter` and `adapters.ollama_adapter`, which are archived, so both scripts fail at
  import as the tree stands.
- `http-no-model-override` (OPEN) says per-producer model overrides are CLI-only and that
  `/api/compare` runs the same model twice. The code disagrees: the route's request model accepts
  `agent_a_model` and `agent_b_model`, and the route builds a separate config for each producer with
  `with_model_override`. The ledger entry looks stale; whether the review app offers the choice is
  not covered on this page.
- Documentation disagreement: `README.md` still lists `gemini_adapter.py` and `ollama_adapter.py` as
  live adapters in `adapters/`, and says `mock` and fixture adapters cover every test path.

Related: [[adapters/langchain_adapter.py]], [[core/contracts.py]], [[web/server.py]],
[[tests/test_adapter_registry.py]]

---
title: Agents and model calls
slug: f-agents
section: Features
order: 10
summary: How an agent is called — one LangChain adapter for Ollama or Gemini, a Tavily search tool, a plain model call for extraction, and a stall timeout.
---

An *agent* here is a model called through one contract: give it a subject, some context and a
directive, and get back a structurally valid response or an error. Everything above the adapters
is written against that contract, so the validation loop never knows which model it is talking
to.

## The two contracts

| Contract | Shape | Used for | Defined in |
|---|---|---|---|
| `AgentAdapter` | `(subject, context, directive) -> AgentResponse` | Every agent attempt in the validation loop. Raises `StructuralParseError` on a reply that breaks the output contract. | [[core/contracts.py]] |
| `ModelCall` | `(system, user) -> str` | The one plain model call outside the loop: reading an agent's finished answer for a grade. | [[core/contracts.py]] |

Both are `Protocol`s, not base classes: anything with the right call shape satisfies them, which
is what lets tests pass a scripted fake ([D-03](decisions.html#d-03)).

## One adapter, two model families

[[adapters/langchain_adapter.py]] is the only real adapter ([D-15](decisions.html#d-15)). The
model name alone picks the family:

- a name containing `gemini` builds `ChatGoogleGenerativeAI` (needs `GEMINI_API_KEY`; Gemini has
  no seed, so only temperature applies);
- anything else builds `ChatOllama` against `OLLAMA_HOST`, with the configured temperature and
  seed.

There is no scripted mode in the running application: if the model can't be reached, the call
raises rather than returning a canned answer ([D-17](decisions.html#d-17)). The earlier
per-provider adapters are archived ([Archive](files-archive.html)).

[[adapters/registry.py]] maps the provider name (only `langchain` now) to a factory, and is the
seam [[web/server.py]] builds every adapter and model call through. `with_model_override` lets a
compare give one agent a different model.

## The search tool

With `TAVILY_API_KEY` set, each agent call binds a Tavily search tool and runs a tool loop: the
model may call search, the result goes back as a tool message, and the loop repeats until the
model answers without a tool call or four round trips have been used
(`_MAX_TOOL_ITERATIONS`).

- **Every search is traced as it happens.** A `started` event when the call begins and a
  `finished` event with the query, status, duration, URLs and per-result snippets. The trace
  records what the agent did, independently of what its own text claims
  ([Live runs](f-live.html)).
- **A bad argument gets one retry.** Models sometimes send placeholder arguments (`"None"`,
  `"N/A"`); the tool is retried once with only the query. A second failure becomes a tool error
  the model sees, never a fake result.
- **Search results count as grounding.** The prompt tells the agent it must search before
  answering "insufficient context", and that a search result is a valid source, cited like the
  context. Both lines exist because of failure modes seen live (code comment).
- **Without a key, the call runs with no tools.** It degrades rather than failing every request;
  the server attaches a `tool_capability_warning` when a message contains a URL the agent then
  can't check. (`requirements.txt` and `.env.example` still say the tool binds and fails; the
  code does not do that.)

Search doesn't replace verification: [[validation/verification.py]] still fetches what the agent
cites, afterwards, in code the agent doesn't control ([D-16](decisions.html#d-16)).

## The plain model call

`make_langchain_model_call` returns a `ModelCall` on the same model, with no tools and no
directive. It is used for the assessment extraction ([Grades and synthesis](f-grades.html)). A
failure there is recorded as `extraction_failed` and never fails the run.

## The timeout

`MODEL_TIMEOUT_S` (default 120) is how long a model call may go without receiving anything.
ChatOllama always streams, so for Ollama it is a stall limit, not a cap on a call's length; for
Gemini it is the request timeout ([D-19](decisions.html#d-19)).

- **Why it exists.** Ollama stopped responding mid-compare four times, and the calls waited
  forever ([ollama-hangs-under-compare](ledger.html#ollama-hangs-under-compare)).
- **Why 120 s.** It is above the slowest successful LLM attempt stored as of 2026-09-27: 85.3 s
  over 56 attempts, search included (`logs/RUN_LOG.md`, 2026-09-27, the model-call timeout
  entry).
- **What happens.** The call raises `LangchainTimeoutError`, a `LangchainConnectionError`, and
  the route records the run as halted with an error saying how long it waited.
- **Tested** against a stub Ollama server in [[tests/test_model_timeout.py]]: a silent server
  ends at the limit; a slow but steady stream longer than the limit succeeds. **Not yet observed**
  on a real hang.

## Limits

- Each call builds a new chat model, about 0.5 s of client setup (measured in the stub test).
- `except EnvironmentError: raise` also passes through built-in `OSError` subclasses unwrapped;
  see the note in [[adapters/langchain_adapter.py]].
- Gemini is configured but has not been confirmed working
  ([gemini-key-unconfirmed](ledger.html#gemini-key-unconfirmed)).

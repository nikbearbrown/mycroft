"""
LangChain adapter — the sole agent framework this subsystem is built on.
Drives either a local Ollama model or a Gemini model through LangChain's
unified chat-model interface, to satisfy the accountability layer contract.

Deliberate exception to stdlib-only (see CLAUDE.md): adds `langchain-core`,
`langchain-ollama`, `langchain-google-genai`, and `langchain-tavily` as
dependencies. All are lazy-imported inside this module so nothing else in the
codebase needs them unless this adapter is actually used.

No scripted or simulated mode. If the underlying model is unreachable or
errors, this raises rather than returning a canned response.

Model family inference (there is no separate "provider" concept anymore)
    `model` alone decides which LangChain chat-model class gets built: a name
    containing "gemini" (case-insensitive) selects `ChatGoogleGenerativeAI`;
    anything else selects `ChatOllama`. One function, one adapter, two
    possible underlying model classes — a caller never chooses a provider,
    only a model name. `GEMINI_API_KEY` (already used by the archived
    `gemini_adapter.py`, reused rather than introducing a second key under a
    different name) is read for the Gemini-family path.

Tavily search tool (use_tools=True, the default)
    The agent is given a real search tool (Tavily, a search API built for
    LLM agents) it can call mid-reasoning to look up current or unfamiliar
    facts, instead of only ever reasoning from what's in its prompt or its
    own training data. This replaced an earlier MCP fetch-a-known-URL tool
    (see logs/RUN_LOG.md) — search finds relevant information about a
    subject; it does not require the caller to already know the exact URL.

    This does not replace validation/verification.py's independent, human-code
    fetch-and-check, which still runs unconditionally afterward on whatever the
    agent claims. The agent having used a tool is not taken on trust — the
    accountability layer never trusts a model's self-report of what it did.

    Every tool call the agent makes is reported through the optional
    `on_tool_event` callback (see make_langchain_adapter), not just described
    in the agent's own text — web/server.py wires this into web/step_trace.py
    so each search, its query, and its result appear in the run's
    chronological step trace alongside the LLM attempts themselves,
    independent of whatever the agent's own thought_log/conclusion says it did.

    Requires `TAVILY_API_KEY` (https://tavily.com — free tier available).
    Tavily's own constructor validates this key and raises immediately if
    it's missing — NOT deferred to the first search call — so each adapter
    call checks for the key itself before attempting to bind the tool: if
    unset, that call degrades to no-tools rather than crashing every single
    chat request until the key is configured. This is a real, visible
    capability gap, not a silent success — `adapters/registry.py`'s
    `ProviderSpec.supports_tools()` checks for this key's presence so
    web/server.py can warn before that happens rather than after.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import os
from typing import Any, Callable

from core.contracts import AgentAdapter
from core.assessment import expects_assessment
from core.parsing import AgentResponse, StructuralParseError, _parse_response
from core.directive import DirectiveVersion

ToolEventCallback = Callable[[dict[str, Any]], None]


OLLAMA_HOST        = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CONTEXT_CHAR_LIMIT = 6_000  # same conservative limit the old ollama_adapter.py used
_MAX_TOOL_ITERATIONS = 4  # caps tool-call round-trips so a confused model can't loop forever

# Seconds a model call may go without receiving anything before it is abandoned.
# ChatOllama always streams, so for Ollama this is a stall limit (no bytes for this
# long), not a cap on a call's total length; for Gemini it is the request timeout.
# Ollama stopped responding mid-compare four times with no limit at all (the Honest
# Ledger's ollama-hangs-under-compare). 120 s is above the slowest successful LLM
# attempt stored as of 2026-09-27 (85.3 s over 56 attempts, search calls included).
MODEL_TIMEOUT_S = float(os.environ.get("MODEL_TIMEOUT_S", "120"))


class LangchainConnectionError(Exception):
    """The underlying LangChain chat model (or its search tool) could not be reached."""


class LangchainTimeoutError(LangchainConnectionError):
    """The model sent nothing for MODEL_TIMEOUT_S seconds, so the call was abandoned."""


def _is_timeout(exc: BaseException) -> bool:
    """Whether exc, or anything it was raised from, is a timeout."""
    import httpx  # a dependency of the ollama client, so present whenever ChatOllama is

    seen: set[int] = set()
    cur: BaseException | None = exc
    while cur is not None and id(cur) not in seen:
        if isinstance(cur, (httpx.TimeoutException, TimeoutError)):
            return True
        seen.add(id(cur))
        cur = cur.__cause__ or cur.__context__
    return False


def _connection_error(model: str, exc: Exception, what: str = "") -> LangchainConnectionError:
    """The error to raise for a failed model call: a timeout says so, and how long it waited."""
    if _is_timeout(exc):
        return LangchainTimeoutError(
            f"Model {model!r} sent nothing for {MODEL_TIMEOUT_S:g} s, so the call was abandoned "
            f"(MODEL_TIMEOUT_S). Original error: {type(exc).__name__}: {exc}")
    return LangchainConnectionError(f"Cannot reach model {model!r} via LangChain{what}. Original error: {exc}")


def _is_gemini_model(model: str) -> bool:
    return "gemini" in model.lower()


def _build_chat(model: str, temperature: float, seed: int | None):
    """
    The one place model-family inference happens. A `model` name containing
    "gemini" gets ChatGoogleGenerativeAI; everything else gets ChatOllama.
    """
    if _is_gemini_model(model):
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set. "
                f"Required to use Gemini-family model {model!r} via LangChain."
            )
        # ChatGoogleGenerativeAI has no seed parameter (Gemini's API doesn't
        # expose one) — temperature is the only reproducibility knob available
        # on this path; seed is silently inapplicable here, not silently lost
        # (the caller passed it because the shared UI slider doesn't know
        # which family a model name maps to).
        return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key,
                                      timeout=MODEL_TIMEOUT_S)

    from langchain_ollama import ChatOllama

    options: dict = {"temperature": temperature}
    if seed is not None:
        options["seed"] = seed
    # client_kwargs go to the ollama client's httpx client, sync and async alike.
    return ChatOllama(model=model, base_url=OLLAMA_HOST, client_kwargs={"timeout": MODEL_TIMEOUT_S}, **options)


def _run_async(coro):
    """
    Run an async coroutine to completion from this module's sync AgentAdapter
    callables, whether or not a FastAPI/uvicorn event loop is already running
    in this thread (it is, when called from web/server.py's async route
    handlers, which call run_validation_loop synchronously from inside an
    `async def`) — asyncio.run() raises if called from inside a running loop,
    so this offloads to a fresh thread with its own loop in that case.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


# Not an exhaustive enum — an observed set, added to as new variants show up
# live (first "None", then "N/A" on a separate run). Deliberately loose
# rather than trying to anticipate every placeholder a model might invent.
_NULL_STRINGS = {"none", "null", "n/a", "na", "unspecified", "not specified", ""}


def _sanitize_tool_args(args: dict[str, Any]) -> dict[str, Any]:
    """
    Ollama-family tool-calling (observed live with llama3.2, across more than
    one run) sometimes emits a placeholder string like "None" or "N/A" for an
    optional argument it doesn't want to set, instead of omitting the key or
    using JSON null. Tavily's own arg schema (list[str] | None for
    include_domains/exclude_domains, etc.) then fails pydantic validation on a
    bare string where it expects a list or nothing — confirmed live twice:
    "input_value='None'" and, separately, "input_value='N/A'", both
    "Input should be a valid list [type=list_type]". Dropping any key whose
    value is one of these placeholder strings (case-insensitive) turns that
    into "argument omitted", which is what the model actually meant.
    """
    return {
        k: v for k, v in args.items()
        if not (isinstance(v, str) and v.strip().lower() in _NULL_STRINGS)
    }


def _result_urls(result: Any) -> list[str]:
    """
    The result URLs a Tavily search returned, in rank order. TavilySearch.ainvoke
    returns a dict ({"results": [{"url": ...}, ...]}); an error path returns a
    plain string, which has no URLs to report.
    """
    if not isinstance(result, dict):
        return []
    return [
        r["url"] for r in result.get("results", [])
        if isinstance(r, dict) and isinstance(r.get("url"), str)
    ]


_SNIPPET_CHARS = 600


def _result_snippets(result: Any) -> list[dict[str, str | None]]:
    """
    What the agent actually read for each result: url, title, and the start of the
    content Tavily returned (≤600 chars each). Recorded so a citation to a web page
    can later be shown beside the text the agent saw (BP), without re-fetching the
    page — which may have changed since, and would not be what the agent read.
    """
    if not isinstance(result, dict):
        return []
    out = []
    for r in result.get("results", []):
        if isinstance(r, dict) and isinstance(r.get("url"), str):
            content = r.get("content")
            out.append({
                "url": r["url"],
                "title": r.get("title") if isinstance(r.get("title"), str) else None,
                "snippet": content[:_SNIPPET_CHARS] if isinstance(content, str) else None,
            })
    return out


def _parse_across_turns(contents: list[str], *, allow_assessment: bool = False) -> Any:
    """
    Parse the agent's response from every assistant message in the tool loop.

    Found live on 2026-09-24: llama3.2 sometimes opens "<thought_log>" in the same
    message that calls the search tool, then finishes "…</thought_log><conclusion>…"
    after the results come back. Only the final message used to be parsed, so the
    opening was silently dropped and a complete two-block response was recorded as
    "missing <thought_log>". The final message alone is tried first (unchanged
    behaviour whenever it parses); otherwise the model's own messages, joined in
    order, are parsed — nothing is added, only nothing it wrote is lost. If that
    fails too, the joined text is what gets recorded as the raw output, so the
    audit trail shows everything the model wrote rather than its last fragment.
    """
    final = contents[-1] if contents else ""
    try:
        return _parse_response(final, allow_assessment=allow_assessment)
    except StructuralParseError:
        whole = "\n".join(c for c in contents if c.strip())
        if whole == final:
            raise
        try:
            return _parse_response(whole, allow_assessment=allow_assessment)
        except StructuralParseError as exc:
            raise StructuralParseError(str(exc), whole) from None


def _returned_error(result: Any) -> bool:
    """
    TavilySearch reports some failures — an HTTP 400 among them — by *returning*
    {"error": ...} rather than raising. Found live on 2026-09-24: every such call
    had been recorded as status "ok" and handed to the model as if it were a result.
    """
    return isinstance(result, dict) and "error" in result and not result.get("results")


async def _call_tool(tool: Any, args: dict[str, Any], query: str | None) -> tuple[Any, str, bool]:
    """
    Invoke `tool` once with the model's (sanitized) args; on failure — raised or
    returned — retry once with only "query". Returns (result, status, retried).

    _NULL_STRINGS is an observed set, not exhaustive, and the model can send other
    arguments the API rejects; one bounded retry with only the one required
    argument covers both without growing a blocklist forever. If the retry fails
    too, it is a genuine tool error and is surfaced as one, never as a result.
    """
    try:
        result = await tool.ainvoke(_sanitize_tool_args(args))
        if not _returned_error(result):
            return result, "ok", False
        first_error: Any = result["error"]
    except Exception as exc:
        first_error = exc
    try:
        result = await tool.ainvoke({"query": query})
    except Exception:
        return f"Tool error: {first_error}", "error", True
    if _returned_error(result):
        return f"Tool error: {result['error']}", "error", True
    return result, "ok", True


async def _invoke_with_tools(
    chat, messages: list, on_tool_event: ToolEventCallback | None = None
):
    """
    Bind the Tavily search tool to `chat` and run the tool-call loop to
    completion. Returns the final AIMessage (no more tool_calls, or
    _MAX_TOOL_ITERATIONS reached).

    Every tool call is reported through `on_tool_event`, in the order it
    actually happened — one event when the call starts (so a hang or a slow
    search is visible in the trace as it happens, not only after it resolves)
    and one when it finishes, each carrying a monotonic `seq` so ordering
    survives even if events from different attempts interleave in storage.
    """
    import itertools
    import time

    from langchain_tavily import TavilySearch
    from langchain_core.messages import ToolMessage

    def _emit(event: dict[str, Any]) -> None:
        if on_tool_event is not None:
            on_tool_event(event)

    seq_counter = itertools.count(1)

    tools = [TavilySearch(max_results=5)]
    bound = chat.bind_tools(tools)
    tools_by_name = {t.name: t for t in tools}

    ai_msg = None
    for _ in range(_MAX_TOOL_ITERATIONS):
        ai_msg = await bound.ainvoke(messages)
        messages.append(ai_msg)
        if not ai_msg.tool_calls:
            return ai_msg
        for call in ai_msg.tool_calls:
            seq = next(seq_counter)
            tool_name = call["name"]
            # Tavily is a search tool, not a fetch-a-known-URL tool — there is
            # no single "url" for a search call, only a query. Kept as the
            # same key MCP's fetch tool used (rather than renaming to
            # "query") so web/server.py's step-trace wiring needs no change;
            # None here is the correct, expected value for a search event.
            query = call.get("args", {}).get("query")
            started = time.monotonic()
            _emit({
                "seq": seq, "tool": tool_name, "url": None, "query": query,
                "args": call.get("args", {}), "phase": "started",
                "status": "ok", "result_preview": None, "duration_ms": None,
            })
            tool = tools_by_name.get(tool_name)
            retried = False
            if tool is None:
                result_text, status = f"Unknown tool: {tool_name!r}", "error"
            else:
                result_text, status, retried = await _call_tool(tool, call.get("args", {}), query)
            duration_ms = round((time.monotonic() - started) * 1000, 1)
            _emit({
                "seq": seq, "tool": tool_name, "url": None, "query": query,
                "args": call.get("args", {}), "phase": "finished",
                "status": status, "retried_query_only": retried,
                "result_preview": str(result_text)[:300],
                "urls": _result_urls(result_text),
                "results": _result_snippets(result_text),
                "duration_ms": duration_ms,
            })
            messages.append(ToolMessage(content=str(result_text), tool_call_id=call["id"]))
    return ai_msg  # ran out of iterations; return the last response anyway


def make_langchain_model_call(
    model: str = "llama3.2",
    temperature: float = 0.0,
    seed: int | None = 42,
):
    """
    A plain (system, user) -> reply call on the same model, no tools, no directive:
    core.contracts.ModelCall, used for the assessment extraction (B4, option 1).
    Raises LangchainConnectionError when the model is unreachable; the caller
    records that as extraction_failed rather than failing the run.
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    def call(system: str, user: str) -> str:
        try:
            reply = _build_chat(model, temperature, seed).invoke(
                [SystemMessage(content=system), HumanMessage(content=user)])
        except EnvironmentError:
            raise
        except Exception as exc:
            raise _connection_error(model, exc) from exc
        return reply.content if isinstance(reply.content, str) else str(reply.content)

    return call


def make_langchain_adapter(
    model: str = "llama3.2",
    temperature: float = 0.0,
    seed: int | None = 42,
    use_tools: bool = True,
    on_tool_event: ToolEventCallback | None = None,
) -> AgentAdapter:
    """
    Returns a call_agent_fn compatible with run_validation_loop.

    Always a real call — the model family (Ollama vs. Gemini) is inferred
    from `model`'s name (see _build_chat). use_tools=True (default) also
    gives the agent a real Tavily search tool it can call mid-reasoning (see
    module docstring). Raises LangchainConnectionError if the model or the
    search tool is unreachable — never substitutes a scripted response.

    on_tool_event, if given, is called synchronously (from whichever thread
    the tool loop actually runs on — see _run_async) once when each tool call
    starts and once when it finishes, so a caller can attach every search —
    query, result preview, status, duration — to its own chronological
    record (web/server.py wires this into web/step_trace.py's StepTrace).
    """
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    def adapter(subject: str, context: str, directive: DirectiveVersion) -> AgentResponse:
        # Tavily's own constructor validates TAVILY_API_KEY and raises
        # immediately if it's missing (not deferred to the first search call)
        # — checked here, once, rather than in _invoke_with_tools, so a
        # missing key degrades this one call to no-tools instead of crashing
        # every single chat request until the key is configured. This is a
        # real capability gap, not a silent success — adapters/registry.py's
        # ProviderSpec.supports_tools() and web/server.py's
        # _tool_capability_warning are what actually tell the user about it.
        tools_active = use_tools and bool(os.environ.get("TAVILY_API_KEY"))

        prompt = f"Subject: {subject}"
        if context and context.strip():
            prompt += f"\n\nContext:\n{context[:CONTEXT_CHAR_LIMIT]}"
        if tools_active:
            # Belongs here, not in the shared directive: tool availability is
            # specific to this adapter, not every model. Two failure modes
            # observed live, both worth naming:
            #   1. Some models write out what looks like an intended tool call
            #      as plain text instead of actually invoking it (seed-
            #      dependent, seen with the earlier fetch tool too) — the
            #      explicit "invoke it, don't describe it" line addresses this.
            #   2. Even when the search genuinely succeeds and returns a real
            #      result, the model can still answer "insufficient context"
            #      anyway (observed live: a search that returned a correct
            #      Wikipedia result, followed by a conclusion claiming the
            #      Context didn't support an answer) — because the shared
            #      GROUNDING RULE says "Context is your only source of fact"
            #      and never mentions the tool, so the model doesn't treat a
            #      search result as satisfying it. This is precisely the case
            #      the user reported: no Context/URL given should mean SEARCH,
            #      not an automatic "I don't know." The paragraph below
            #      explicitly amends the GROUNDING RULE for this call: a
            #      search result counts as grounding, same as Context.
            prompt += (
                "\n\nYou have a search tool available. If the Context above is "
                "empty, missing, or does not contain what you need to answer, "
                "and you do not already know the answer with high confidence, "
                "you MUST call the search tool BEFORE writing your response — "
                "do not default to \"insufficient context\" without searching "
                "first. A result returned by the search tool IS a valid source "
                "of fact for this response, exactly like the Context section: "
                "cite it the same way, [SOURCE: <label>, <url>]. Only conclude "
                "the information is unavailable if the search tool also fails "
                "to find it. Do not write out a tool call as text; actually "
                "invoke it. Only your final response (after any tool calls) "
                "needs to be the two XML blocks."
            )

        messages = [
            SystemMessage(content=directive.text),
            HumanMessage(content=prompt),
        ]

        try:
            chat = _build_chat(model, temperature, seed)
            if tools_active:
                result = _run_async(_invoke_with_tools(chat, messages, on_tool_event))
            else:
                result = chat.invoke(messages)
        except EnvironmentError:
            raise  # missing API key — a config problem, not a connection failure
        except Exception as exc:  # connection refused, model missing, search tool failure, etc.
            raise _connection_error(model, exc, " (or its Tavily search tool)" if tools_active else "") from exc

        if not tools_active:
            return _parse_response(result.content, allow_assessment=expects_assessment(directive.version))
        # _invoke_with_tools appended every assistant turn to `messages`.
        contents = [
            m.content for m in messages
            if isinstance(m, AIMessage) and isinstance(m.content, str)
        ]
        return _parse_across_turns(contents or [result.content],
                                   allow_assessment=expects_assessment(directive.version))

    return adapter

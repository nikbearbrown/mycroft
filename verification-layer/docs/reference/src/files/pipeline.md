---
title: Pipeline
slug: files-pipeline
section: Files
order: 30
summary: The execution machinery - the ADR-07 retry-then-halt validation loop that turns adapter calls into audit records, and the LangFuse tracing wrapper.
---

`pipeline/` runs an agent through the accountability layer's contract. It takes an adapter (any
`AgentAdapter` from [[core/contracts.py]]), calls it under a directive, checks the reply, retries
once on a structural failure, halts on a second, and writes one `ReasoningObject` per attempt.
It also holds the optional tracing wrapper that makes those adapter calls visible in LangFuse.

## Dependency rule

`pipeline/` may import only from `core/` (and the standard library and third-party packages).
[[tests/test_layering.py]] enforces this: its `_ALLOWED` table gives `pipeline` the set `{"core"}`,
with the comment "The validation loop and tracing operate on core types only". The layers further
out (`producers/`, `validation/`, `web/`, `scripts/`) may import `pipeline/`; `adapters/` and
`datasources/` may not, so an adapter never knows the loop exists. The loop receives the adapter
as a parameter instead.

The same rule explains a copy in [[core/assessment.py]]: the loop validates the assessment
block, so the metric-name list it validates against has to live in `core/`, not in
`validation/facts.py`.

## How the files fit together

- [[pipeline/middleware.py]] is the single place ADR-07 is implemented. Every run of an agent in
  this subsystem, whether a chat, a lens producer, a cross-agent compare, a consistency probe or a
  replay, ends up in `run_validation_loop`.
- [[pipeline/observability.py]] wraps an adapter from the outside so each call becomes a LangFuse
  span. It changes nothing about the loop: the loop gets the wrapped adapter and can't tell the
  difference.

The two are independent; neither imports the other. [[producers/lens.py]] is where they meet: it
wraps the adapter with `make_traced_adapter` and passes the result to `run_validation_loop`.

## `pipeline/__init__.py`

**Role:** package marker for `pipeline/`.

The file is empty. It exists so `pipeline` imports as a package, which
[[tests/test_layering.py]] (`test_every_package_is_importable_as_a_package`) checks. Callers import
from the submodules directly.

Related: [[core/__init__.py]]

## `pipeline/middleware.py`

**Role:** the ADR-07 validation loop: one retry on structural failure, then halt, with every
attempt written to the audit record.

The module docstring states the two commitments: both attempts are always written to the record,
and a rising parse-failure rate across runs is a signal that the directive is decaying.

### The loop, exactly

`run_validation_loop(ticker, context, run_id, agent_id, *, confidence_score=0.7, data_sources=(),
directive=None, call_agent_fn=None, assess_fn=None)`:

1. If `call_agent_fn` is `None`, it raises `TypeError`. The layer has no default model; the
   message tells the caller to provide an adapter of the shape
   `f(subject, context, directive) -> AgentResponse`.
2. If `directive` is `None`, it uses `core.directive.get_active_directive()`.
3. **Attempt 1:** calls the adapter with the directive, then
   `core.parsing.reject_unusable_conclusion(response, directive.text)`. "Structural" therefore
   includes an empty conclusion and one that copies the directive, both of which parse as XML but
   are not answers (code comment).
   - Success: one `ReasoningObject` (attempt 1, `SUCCESS`); returns.
   - `StructuralParseError`: records attempt 1 as `PARSE_FAILURE` with the raw reply, then goes on
     to attempt 2.
4. **Attempt 2:** calls the same adapter with the corrective directive, and runs the same check
   against the corrective text.
   - Success: two records (`PARSE_FAILURE`, then attempt 2 `SUCCESS`); returns.
   - `StructuralParseError` again: records attempt 2 as `HALT` and raises `HaltError` carrying both
     records, chained from the second parse error. No conclusion is delivered.

Only `StructuralParseError` is caught. Any other exception from the adapter (a connection error, a
timeout, a bug) propagates straight out, and no `ReasoningObject` is written for that attempt.

### Key names

- `CORRECTIVE_DIRECTIVE_TEXT` and `_CORRECTIVE_DIRECTIVE`: the attempt-2 directive, a
  `DirectiveVersion` with version `"corrective"`. It is a short format reminder ("Your previous
  response failed structural validation. You must provide your internal reasoning in a
  `<thought_log>` block ..."), used on the retry whatever directive attempt 1 had. It is not in the
  directive registry in [[core/directive.py]], so `get_directive("corrective")` raises `KeyError`.
  Because it is recorded per attempt (`directive_version`, `directive_text` on the record), a stored
  retry shows which instructions the model actually had.
- `HaltError(message, reasoning_objects)`: raised on double failure. It carries every record
  written so far so the caller can persist the audit trail before it propagates the halt (class
  docstring). Callers catch it and keep the records: `web/server.py`'s chat and replay routes,
  [[validation/cross_validation.py]] (which catches only `HaltError` per agent, and is how the
  compare routes reach the loop) and [[validation/consistency.py]]. [[producers/lens.py]] deliberately does not catch it: its docstring
  says swallowing a halt there would defeat ADR-07.
- `ValidationLoopResult(reasoning_objects, final_response)`: the records in attempt order, and the
  successful `AgentResponse`. `final_response` is typed `AgentResponse | None` with the comment
  "None when halted", but a halt raises instead of returning, so a returned result always has one
  (a comment in [[validation/cross_validation.py]] relies on this).
- `_build_reasoning_object(...)`: builds one record. Every attempt records the directive it used,
  the `context_window` (`{"subject": ticker, "context": context}`), the `data_sources` and the
  `confidence_score` passed in. Failed attempts record the raw reply as `raw_output = {"text": ...}`
  and no thought log or conclusion. Successful attempts record both blocks and the raw text. The
  context window is rebuilt on every record, not stored once, so each record is self-describing
  (code comment).
- `_extract(assess_fn, directive, subject, context, response)`: the separate assessment
  extraction. Returns `None` if `assess_fn` is `None` or if the directive itself asks for an
  in-answer block.

### Assessments on a successful attempt

Assessments are recorded only on a successful attempt, after the structural check, so they can't
affect retry or halt (`run_validation_loop` docstring):

- Under a directive where `core.assessment.expects_assessment` is true (v1.6.0 and later), the
  in-answer `<assessment>` text from the `AgentResponse` goes through `parse_assessment`.
  `assessment_source` is `"directive"`. Absent, unclosed and invalid blocks are recorded with their
  status; none of them fails the attempt.
- Otherwise, if `assess_fn` (a `ModelCall`) is given, `extract_assessment` reads the finished
  answer. `assessment_source` is the extraction prompt version. The extraction's reply is kept
  verbatim under `raw_output["assessment_extraction"]`, with the prompt version. A failed
  extraction is recorded as `extraction_failed` and never raised.

The corrective directive's version is `"corrective"`, which never expects a block, so a successful
retry goes down the extraction path if `assess_fn` was given. Only
[[validation/cross_validation.py]] passes `assess_fn` (from `web/server.py`'s ticker compare route);
chat runs get no extraction.

### Design notes

- **One retry, then halt, never degrade.** The loop does not pass through a best-effort answer.
  Without a conclusion, nothing is delivered (`docs/SYSTEM_DESIGN.md` §2.3). The record types in
  [[core/schemas.py]] enforce the same shape independently: attempt 2 can't be `PARSE_FAILURE`, and
  `SUCCESS` requires a conclusion.
- **Failed attempts are evidence.** A halt still produces records, because "the agent failed twice"
  is itself an audited fact (`docs/SYSTEM_DESIGN.md` §4).
- **Echoes routed through the retry.** The call to `reject_unusable_conclusion` on both attempts
  was added so a conclusion that copies the directive is retried and recorded as `PARSE_FAILURE`,
  and halts if it happens twice (`logs/RUN_LOG.md`, 2026-09-24 (continued), "Directive echo,
  properly: v1.5.1 (nothing inside the tags) + a machine check").
- **Per-attempt directive and context.** Recording the directive and inputs on each attempt, not
  only on the session, was added because the corrective directive was built inline here and never
  attached to any record, and the user prompt wasn't recorded at all (`logs/RUN_LOG.md`, 2026-09-22,
  "Feature: expose per-attempt context window (directive + user prompt) in /api/chat").
- **Why the adapter is a parameter.** The retry passes a different directive to the same adapter,
  which is why the directive is part of the `AgentAdapter` call signature ([[core/contracts.py]]
  module docstring).
- **Tested vs observed.** Every branch is tested with scripted, network-free adapters:
  `tests/test_phase2_agent.py` (happy path, retry-then-success, retry-then-halt, the corrective
  directive recorded on attempt 2, run and agent IDs consistent across attempts),
  `tests/test_directive_echo.py` (echo then clean retry, empty twice halts),
  `tests/test_assessment.py` (in-answer assessment recording, corrective retry not asked for one,
  older directives record nothing) and `tests/test_synthesis.py` (extraction). The retry and halt
  paths have also been observed on real models: the `retry-halt-unproven` ledger entry was resolved
  on 2026-09-27 from stored runs, counting 13 retries in 48 real agent-runs between 2026-09-22 and
  2026-09-24 (4 recovered, 9 halted). The same entry notes that nobody has reviewed the 9 halts one
  by one.

### Limits and open issues

- **The retry drops the grounding rules.** Attempt 2 replaces the whole directive with the
  one-paragraph corrective text, so it runs without the GROUNDING and CITATION rules. It was found
  and not changed, because changing it alters ADR-07's contract (`logs/RUN_LOG.md`, 2026-09-24
  (continued), "Directive echo, properly", open issues). The 2026-09-24 (continued) "B1 + U2" entry
  adds that llama3.2 often writes its tool call as JSON text on attempt 2, and that this caused
  every second-attempt halt seen that day.
- **The confidence score is a constant by default.** `confidence_score` defaults to 0.7 and is
  copied onto every record. [[producers/lens.py]] doesn't pass one, so lens-produced records carry
  0.7 whatever happened in the run. The record type's ADR-04 comment ("computed, not
  self-reported") is not implemented by anything in this layer.
- **Non-structural adapter failures leave no record.** An adapter exception other than
  `StructuralParseError` escapes the loop with no `ReasoningObject` for the attempt. What happens
  next is up to the caller.
- The parameter is named `ticker` but is used as the generic subject (it is recorded as
  `context_window["subject"]`), because the loop is also used for non-financial chat.
- `docs/SYSTEM_DESIGN.md` §2.3 says attempt 1 uses `ACTIVE_DIRECTIVE` "(currently `v1.1.0`)"; the
  active directive is v1.5.2 ([[core/directive.py]]).

Related: [[core/parsing.py]], [[core/directive.py]], [[core/schemas.py]], [[core/assessment.py]], [[core/contracts.py]], [[producers/lens.py]], [[validation/cross_validation.py]]

## `pipeline/observability.py`

**Role:** the LangFuse tracing wrapper: `make_traced_adapter` turns an adapter into one whose
every call is recorded as a LangFuse generation span.

The module docstring is clear about what this is and isn't. LangFuse traces what happened (data
flow, latency, timeline); it does not verify correctness or catch hallucination. That job stays
with `validation/consistency.py`, `validation/claims.py` and `validation/verification.py`. The
wrapper is applied from the outside, so neither [[pipeline/middleware.py]] nor any adapter changes.

### Key functions

- `make_traced_adapter(adapter_fn, name)`: returns
  `observe(name=name, as_type="generation")(adapter_fn)`. The loop may call the wrapped adapter up
  to twice (attempt 1 and the corrective attempt 2), and each call produces its own span. Exceptions,
  including `StructuralParseError`, are logged by LangFuse and re-raised unchanged, so ADR-07's
  retry and halt logic is unaffected (docstring).

### Configuration

The LangFuse SDK reads `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` and `LANGFUSE_HOST` from the
environment itself; this module reads none of them. The docstring states that without them the
wrapped calls still run normally, with the SDK disabling itself and logging a warning, which is
what makes the wrapper safe in tests and without a LangFuse instance. That degradation was seen in
an early live-run attempt (`logs/RUN_LOG.md`, 2026-08-29, "First live-run attempts: two real bugs
found and fixed, one external blocker found", which calls the warning "expected, harmless").

### Who uses it

- [[producers/lens.py]]'s `run_lens` wraps the producer's adapter with the name
  `"{lens.trace_prefix}:{ticker}"` before calling the loop. `producers/financial.py` and
  `producers/earnings.py` add their own `@observe` spans (`analyze_ticker`, `analyze_earnings`)
  around `run_lens`, so the generation spans nest under them.
- [[scripts/run_cross_agent_live.py]] wraps both agents' adapters so one trace nests the EDGAR tool
  span and both generation spans. That wrapping was missing in the script's first version and added
  in the same session (`logs/RUN_LOG.md`, 2026-08-28, "Replace fixture Producer B with a real second
  grader", marked FOUND AND FIXED).

`web/server.py` and [[validation/cross_validation.py]] do not import this module; the web routes
call the loop with the adapter as built. [[validation/cross_validation.py]] copies the context
variables into its worker threads so LangFuse's `@observe` nesting survives concurrency when a
wrapped adapter is used.

### Design notes

- `langfuse` is a non-stdlib dependency, listed in `requirements.txt` under "Optional
  observability" as a deliberate exception to stdlib-only, v3 or later for the top-level `observe`
  API.
- Wrapping from the outside, not inside the loop, keeps the loop's contract and its tests
  independent of tracing (docstring).

### Limits and open issues

- **Token and cost fields are blank.** The docstring says they stay empty until the adapters
  surface usage metadata, which is not implemented.
- **Not observed in a dashboard.** The 2026-08-28 entry says the nesting was verified structurally
  but the trace had not been seen in LangFuse. The 2026-09-24 (continued) "BL: unblock the event
  loop, run agents concurrently, stream live events" entry says nesting across the new threads is
  wired but not observed, because LangFuse wasn't running. No later entry records an observed trace.
- **The import is not optional.** `from langfuse import observe` is at module level with no
  fallback. Anything that imports this module, including [[producers/lens.py]] and so every
  producer and the tests that import them, needs `langfuse` installed. `requirements.txt` says the
  core engine's tests "run on a bare interpreter" and calls LangFuse optional. That holds for
  `core/` and [[pipeline/middleware.py]], not for this module or its importers.
- `README.md` describes this file as "used by every producer". That is true of the lens producers
  run through `run_lens`, but the live web routes, including `/api/compare`, don't use it, so those
  agent calls are not traced by this wrapper.
- The subsystem `CLAUDE.md` says `langfuse` is documented as a deliberate exception in this file's
  docstring. The docstring describes the configuration and the graceful degradation but doesn't use
  that wording; the "deliberate exception" statement is in `requirements.txt`.

Related: [[pipeline/middleware.py]], [[producers/lens.py]], [[scripts/run_cross_agent_live.py]], [[validation/cross_validation.py]]

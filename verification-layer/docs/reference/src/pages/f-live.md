---
title: Live runs and the step trace
slug: f-live
section: Features
order: 80
summary: Every fetch, model attempt, search and extraction is recorded as a timed step and streamed to the review app as it happens; nothing is simulated.
---

A comparison result says what was concluded, not how. The step trace records how: every call,
in the order it started, tagged with whose work it was. It is stored with the run and streamed
live while the run happens.

## Steps

[[web/step_trace.py]]'s `StepTrace` records each step with a sequence number (the order steps
*started*), a phase, a label, a start time, a status, a duration and optional detail.

| Phase | Holds |
|---|---|
| `shared` | work done once for both agents: CIK lookup, the one companyfacts fetch, the per-lens summaries |
| `agent_a`, `agent_b` | that agent's LLM attempts, searches and assessment extraction |
| `compare` | the comparison note |
| `chat` | a chat run's single agent |

Shared work is recorded once, as `shared`, because a view that drew the fetch under each agent
would invent a second fetch that never happened.

Steps are created two ways: `record(...)` times a block of work, and `note(...)` records an instant
fact or work timed elsewhere (searches are timed inside the adapter's tool loop).
`wrap_adapter` and `wrap_model_call` turn each agent attempt and each extraction call into a step
without touching the validation loop.

**Thread-safe.** Both agents append at the same time; sequence numbers are assigned under a lock
and are unique and gap-free ([[tests/test_concurrency_and_stream.py]]).

## Streaming

`POST /api/compare/stream` and `POST /api/chat/stream` run the same work as the plain routes on a
worker thread and send server-sent events: `run_started`, `step_started` / `step_finished` as
steps happen, `agent_finished` per agent in a compare, then `result` (the same payload the plain
route returns) or `error`. `result` is always last ([D-21](decisions.html#d-21)).

- **Closing the browser doesn't stop the run.** The record is still stored: "a closed browser tab
  must not be able to delete it" (code comment).
- **Investors get a filtered stream.** No search-result text, no conclusions.
- The browser's `EventSource` can't send a POST with a token, so the app reads the stream with
  `fetch` and its own parser ([[web/frontend/src/api/stream.ts]]).

## In the review app

The live view ([[web/frontend/src/views/CompareView.tsx]], [[web/frontend/src/state/liveRun.ts]])
derives everything from real events ("honest liveness"): a step is running only because its
`step_started` arrived without a `step_finished`, and elapsed time counts from the server's own
start time. If the stream drops, the app polls for the stored record every 5 s and opens it
when it appears.

## Known issue

A chat run's consistency probe calls the model through the same traced adapter, so it is recorded
as "LLM attempt 2" and shown as "Retrying (attempt 2)". It is not a retry
([consistency-probe-shown-as-retry](ledger.html#consistency-probe-shown-as-retry), open).

## Observed

On 2026-09-24, streamed AAPL and MSFT compares on llama3.2 with real Tavily and EDGAR showed both
agents' model calls overlapping by 39.4 s and 16.9 s (`logs/RUN_LOG.md`, "BL: unblock the event
loop, run agents concurrently, stream live events").

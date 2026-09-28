---
title: A run end to end
slug: lifecycle
section: Architecture
order: 20
summary: One chat run and one ticker compare, followed from the browser through every layer to the stored record and the gate.
---

This page follows two requests through the system. Each step links to where it happens; the
[Web server](files-web.html#f-web-server-py) entry has the full detail.

## A chat run

`POST /api/chat/stream` with `{message, context}` and an auditor or investor token.

1. **The route** ([[web/server.py]], `_run_chat`) creates a run id and a step trace, and sends
   `run_started`.
2. **The input is canonicalised**: Unicode NFC, trimmed, spaces collapsed, so the same question
   always gives the same prompt bytes (needed for seed-based replay).
3. **The adapter is built** through [[adapters/registry.py]] and wrapped by [[web/step_trace.py]], so
   each attempt becomes a timed step. Search calls report into the trace as they happen.
4. **The validation loop** ([[pipeline/middleware.py]]) calls the agent with the active directive
   ([[core/directive.py]]). The adapter ([[adapters/langchain_adapter.py]]) runs the model with the
   Tavily tool loop and parses the reply ([[core/parsing.py]]). A broken reply is retried once with
   the corrective directive, then halted.
5. **On success**: claims are extracted and their citations verified ([[validation/claims.py]],
   [[validation/verification.py]]), and the consistency probe asks again
   ([[validation/consistency.py]]).
6. **The record is stored** ([[web/db.py]]), with every attempt's reasoning object, the steps and
   the config snapshot, whatever the outcome.
7. **The stream ends** with `result`: the same payload `POST /api/chat` returns. The review app
   opens the stored record at the viewer's scope.

Chat runs are never gated.

## A ticker compare

`POST /api/compare/stream` with `{ticker: "AAPL", pairing: "lenses"}`.

1. **Shared work, once** (phase `shared`): `lookup_cik` and one `fetch_company_facts`
   ([[datasources/edgar.py]]), then each lens's summary of the same payload
   ([[producers/financial.py]], [[producers/earnings.py]]). The exact context each agent will get
   is kept with the run.
2. **Two agents, at once** ([[validation/cross_validation.py]]): each through its own traced adapter
   and the validation loop, on two threads. `agent_finished` is sent as each completes.
3. **Each answer is read for a grade**: one extraction call per agent ([[core/assessment.py]],
   traced as kind `extract`).
4. **The comparison** ([[validation/facts.py]]): figures tagged with metric and period, one status
   per metric; the pairing's contradiction rule sets `contradiction_flag`.
5. **The checks** ([[validation/constraints.py]]): internal consistency, claim versus source, and
   the filing itself.
6. **The synthesis** ([[validation/divergence.py]]): why the views differ, the counted evidence,
   consensus if there is one.
7. **Claims per agent**, each checked against that agent's own citations.
8. **Stored** with its gate policy (`persist_cross_agent_run`), then **the gate** is computed
   ([[validation/gate.py]]): `AWAITING_DECISION` if any figure, hard check or grade needs a human.
9. **The stream ends** with `result`. An investor's stream carried no search text or
   conclusions, and the result is redacted like a later read would be.

## After the run

1. **A reviewer opens the record** in the review app: `GET /api/runs/{id}` at their scope,
   served through `redact_for_scope`.
2. **They check a figure** against the filing: `GET /api/facts/excerpt`
   ([[datasources/filings.py]]) or the recorded search snippet
   (`GET /api/runs/{id}/source-snippet`).
3. **They decide each open item**: `POST /api/runs/{id}/decisions` (auditor only), validated and
   appended to `gate_decisions`. When every item has a decision, the gate is `DECIDED`, and an
   investor read shows the values, plus the grade the reviewer set.
4. **They export the review**: `GET /api/runs/{id}/export.md` ([[validation/audit.py]]).

## What each layer contributed

| Layer | In a compare |
|---|---|
| `datasources/` | the one EDGAR fetch, and later the filing excerpt |
| `producers/` | what each agent is shown |
| `adapters/` | the model and search calls |
| `pipeline/` | the output contract, retry and halt |
| `core/` | the directive, the parser, the records, the assessment vocabulary |
| `validation/` | the comparison, checks, synthesis, gate, redaction and audit |
| `web/` | the routes, the stream, the trace, the store, the tokens |

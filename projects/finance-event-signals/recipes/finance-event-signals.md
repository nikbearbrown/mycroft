---
status: RUNNABLE-LIVE   # DRAFT | SPECIFIED | RUNNABLE-SAMPLE | RUNNABLE-LIVE | VERIFIED
todos_open: 0
last_gate: "week4-promotion, 2026-08-30, logs/RUN_LOG.md#2026-08-30-week-4"
attestation: "logs/RUN_LOG.md#attestation-2026-08-30"
recipe_version: 0.3.0
---

# Recipe — finance-event-signals

## Executive summary

A near-real-time pipeline that ingests public-company events (SEC 8-K filings, EDGAR
latest-filings feed; later FRED releases), runs each through a LangGraph agent that extracts a
structured **material-event read** — or **withholds** it when the evidence is thin — persists
and serves the reads over gRPC/REST, **halts each read at a human review gate**, and then grades
every cleared read against the realized N-day price move.

It is a monitoring queue for an analyst. It does not decide or place a trade. The human owns
every call (P1).

## Required reads

- `../SNICKERDOODLE.md` (upstream constitution — referenced, not vendored) · `GOVERNANCE.md`
- `data/verified/SCHEMA_REFERENCE.md` — the event envelope contract
- `docs/PLAN.md` — the 4-week build plan
- SEC EDGAR fair-access policy (User-Agent required, ~10 req/s)

## Phase gates

1. **Source gate** — every configured source (EDGAR FTS, EDGAR Atom, FRED) is reachable and
   returns a parseable payload; `EDGAR_USER_AGENT` is set. Test: gateway `cycle complete` log
   shows `fetched > 0` with no `fetchFTS` / `fetchAtom` errors. Human capacity: [TO].
   `[TODO: APPROVE]` first live run.
2. **GIGO gate** — every event promoted to `events.validated` passes schema + freshness +
   ticker-resolution; rejects land on `events.deadletter` **with a reason**.
   `[BUILT Week 2, verified]` `validation-svc`. Not cleared: no logged full sample run.
3. **Extraction-adequacy gate** — the LangGraph graph emits a signal only when self-consistency
   + verify agree; otherwise it **withholds** (P3 — never invent a read).
   `[BUILT Week 2, verified]` `enrichment-svc/graph.py` (6/6 branch tests, run in the image build).
4. **Human-clear gate** — a signal is `pending_review`/`withheld` until a named human calls
   `ClearGate(reviewer, verdict, note)`; nothing reaches `events.actionable` without a
   `gate_decisions` row (P4). `[BUILT Week 2, verified]` `query-api`. Invariant checked:
   `actionable_without_decision = 0`.
5. **Report gate** — every run produces both a machine JSON log (+ OTel trace) and a
   human-readable Markdown report in `reports/generated/` (P5).
   `[BUILT Week 2, verified]` `scripts/run_report.py` — `make report`.
6. **Grading gate** — `outcome-grader` scores cleared signals against realized price moves;
   results are compared honestly against `PRE_REGISTRATION.md`, mismatches explained in
   `logs/RUN_LOG.md`, never silently corrected (P8).
   `[BUILT Week 4, verified]` `services/outcome-grader` + `scripts/scorecard.py` — first run:
   19 actionable, 3 gradeable (n too small to generalize, stated in the scorecard itself),
   16 correctly marked `pending` (never a guessed value). Recurring: `deploy/k8s/grader-cronjob.yaml`.

All 6 gates now have logged evidence. `todos_open: 0` as of the Week-4 promotion
(see `logs/RUN_LOG.md`) — gate 1's `[APPROVE]` closed by a human (sachin) citing four weeks
of live EDGAR runs with `EDGAR_USER_AGENT` set and no sustained source failures.

## Primary stored scripts / services

| Service | Lang | Status | Role (Snickerdoodle layer) |
|---|---|---|---|
| `services/ingest-gateway` | Go | W1 ✅ · W2 +SubmitEvent gRPC | ingest layer — only component that touches the network (P2) |
| `services/validation-svc` | Go | W2 ✅ | GIGO layer — `events.raw → events.validated`; rejects → `events.deadletter` w/ reason; CIK→ticker |
| `services/enrichment-svc` | Python + LangGraph | W2 ✅ | tool layer — reads `events.validated` only; classify→extract→self-consistency→verify→emit\|withhold |
| `services/persistence-svc` | Go | W1 ✅ · W2 +signals/gate model | writes the verified store (PostgreSQL), idempotent tx upsert of event + signal |
| `services/query-api` | Go | W2 ✅ | gRPC + REST; `ClearGate` = the phase gate → `gate_decisions` + `events.actionable` |
| `services/outcome-grader` | Python | W4 ✅ | audit — grades reads against reality; idempotent, never guesses (`correct=NULL` when ungradeable) |
| `services/dashboard` | Python (Streamlit) | W2 ✅ | human report surface + the review-gate UI (localhost:18501) |

Proto: `proto/fes/v1/fes.proto` → `make proto` (buf) → `proto/gen/`. QueryService (ListSignals,
GetSignal, ClearGate) + IngestService (SubmitEvent).

## Workflow

```
poll → events.raw → [validate → events.validated] → enrich (emit|withhold) → events.enriched
     → persist (PostgreSQL, status=pending_review) → human ClearGate → events.actionable
     → (N days later) grade vs realized price move → scorecard audit
```

Week 1 wires: `poll → events.raw → enrich (passthrough stub) → events.enriched → persist`.

## Output contract (two customers, P5)

- **Agent log:** structured JSON per run (service logs) + OTel trace (Week 3). Full detail,
  parseable.
- **Human report:** `reports/generated/run-<date>.md` — events ingested, signals emitted vs.
  withheld, flagged material, gate status. Insight and decisions, not pipeline dump.

## Logging rule

One `logs/RUN_LOG.md` entry per: meaningful run / backfill, prompt-or-schema change, gate
decision, blocker. These entries are the evidence for every recipe-status transition.

## Stop conditions

- `EDGAR_USER_AGENT` unset or a source returns non-2xx repeatedly → gateway logs, keeps
  retrying, does not fabricate events.
- A malformed event → `events.deadletter` with a reason (never silently dropped) *(Week 2)*.
- The LangGraph graph cannot reach agreement → **withhold**, do not emit *(Week 2)*.
- No signal is published to `events.actionable` without a `gate_decisions` row *(Week 2)*.
- No accuracy figure may be quoted until `outcome-grader` has run against realized outcomes and
  been compared to `PRE_REGISTRATION.md` — and even then, a scorecard with n<10 states plainly
  that it is not a generalizable accuracy claim *(Week 4, enforced in `scripts/scorecard.py`)*.

## Status ceiling — VERIFIED is not reachable solo

Per `GOVERNANCE.md`: this is solo development. `RUNNABLE-LIVE` is the honest ceiling — every
gate has been cleared with real evidence, but `VERIFIED` requires an attestation from an
**independent** reviewer, which does not exist here. Do not bump this field past
`RUNNABLE-LIVE` without one.

## Human-only judgment boundary

*Is this event material enough to route to a desk, and is the extracted direction right?* — the
agent extracts and withholds; a named human decides and clears.

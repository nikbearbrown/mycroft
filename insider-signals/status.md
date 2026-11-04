# status.md — Insider Signal Intelligence module

_Snapshot updated at the end of each working session. See `logs/RUN_LOG.md` for full history._

**Last updated:** 2026-11-04
**Fellow:** Gomathy S.
**Module:** `insider-signals/`, which contributes the `insider-signal-agent` recipe.

---

## Recipe lifecycle state

| Recipe | State | Evidence |
|--------|-------|----------|
| `insider-signal-agent` | **DRAFT** | 8 open TODOs; INGEST, PARSE, GIGO run on 2026 Q3 only; no gate cleared |

Lifecycle: `DRAFT → SPECIFIED → RUNNABLE-SAMPLE → RUNNABLE-LIVE → VERIFIED`

## Current dataset

- Source: SEC Insider Transactions Data Sets, study period **2023 Q1 – 2026 Q3**.
- Downloaded so far: **2026 Q3 only** (live test, G1 verify PASS). Raw files are gitignored; `manifest.json` and `request_log.jsonl` are committed.

## Next actions (week 1–2)

- ~~Write `ingest.py` and its tests~~ (done 2026-11-03: 33 tests passing).
- Ingest the full study period (2023 Q1 – 2026 Q3), then run `--verify` and log the G1 decision.
- ~~Start PARSE~~ (done 2026-11-03: 2026 Q3 gives 5,115 qualifying buys of 59,834 Form 4 rows; 57 tests passing).
- ~~Decide the private-purchase rule~~ (done 2026-11-04: `PRE_REGISTRATION.md` Rule 1).
- ~~GIGO `conformance.py`~~ (done 2026-11-04: all halting checks pass on 2026 Q3; 5,115 buys in `data/verified/insider_buys.csv`; spot-check 15 exact / 10 rounding only / 0 other; 83 tests passing).
- Read `data/verified/conformance-audit.md` and log the G2 decision.
- Decide how to handle the data set's 2-decimal rounding (588 buys below $1.00) and the 42 amendment buys that repeat an original.
- Register the `is_10b5_1 = unknown` treatment before SIGNALS.
- Next stage: ENRICH (`enrich.py`, G3), after the full-period ingest.

## Open decisions / blockers

- G6 is a **self-attestation** (Gomathy S.) during development; external review pending.
- See the `[TODO]` list in `recipes/insider-signal-agent.md`.

# status.md — Insider Signal Intelligence module

_Snapshot updated at the end of each working session. See `logs/RUN_LOG.md` for full history._

**Last updated:** 2026-11-03
**Fellow:** Gomathy S.
**Module:** `insider-signals/`, which contributes the `insider-signal-agent` recipe.

---

## Recipe lifecycle state

| Recipe | State | Evidence |
|--------|-------|----------|
| `insider-signal-agent` | **DRAFT** | Spec only; 10 open TODOs; no runs |

Lifecycle: `DRAFT → SPECIFIED → RUNNABLE-SAMPLE → RUNNABLE-LIVE → VERIFIED`

## Current dataset

- Source: SEC Insider Transactions Data Sets, study period **2023 Q1 – 2026 Q3**.
- Downloaded so far: **2026 Q3 only** (live test, G1 verify PASS). Raw files are gitignored; `manifest.json` and `request_log.jsonl` are committed.

## Next actions (week 1–2)

- ~~Write `ingest.py` and its tests~~ (done 2026-11-03: 33 tests passing).
- Ingest the full study period (2023 Q1 – 2026 Q3), then run `--verify` and log the G1 decision.
- Start PARSE: join tables, transaction-code classification, `AFF10B5ONE` normalization.

## Open decisions / blockers

- G6 is a **self-attestation** (Gomathy S.) during development; external review pending.
- See the `[TODO]` list in `recipes/insider-signal-agent.md`.

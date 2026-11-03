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

None yet. Planned source: SEC Insider Transactions Data Sets, study period **2023 Q1 – 2026 Q3**.

## Next actions (week 1–2)

- Write `ingest.py` with the User-Agent check, rate limit, manifest and checkpoint/resume, plus its tests.
- Confirm on downloaded files the two `[verify]` items: `AFF10B5ONE`, and the
  `RPTOWNER_RELATIONSHIP` format.

## Open decisions / blockers

- G6 is a **self-attestation** (Gomathy S.) during development; external review pending.
- See the `[TODO]` list in `recipes/insider-signal-agent.md`.

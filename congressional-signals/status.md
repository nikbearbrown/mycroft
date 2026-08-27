# status.md — Congressional Signal Intelligence module

_Snapshot updated at end of working session. See `logs/RUN_LOG.md` for full history._

**Last updated:** 2026-06-30
**Fellow:** Ameya Deshmukh
**Module:** `congressional-signals/` — contributes the `congressional-signal-agent` recipe.

---

## Recipe lifecycle state

| Recipe | State | Evidence |
|--------|-------|----------|
| `congressional-signal-agent` | **RUNNABLE-LIVE** | Logged runs in RUN_LOG (2026-05-17 → 2026-06-30) |

Lifecycle: `DRAFT → SPECIFIED → RUNNABLE-SAMPLE → RUNNABLE-LIVE → VERIFIED`
Not yet **VERIFIED**: awaiting human attestation gate (G6) on the 64-politician run +
statistical-significance check (see open TODOs).

---

## Current dataset

- **64 politicians**, **9,211 trades** (May 2023 – Jun 2026)
- 4,166 priced (45%) · per-trade SPY market adjustment applied
- Aggregate BUY alpha **+0.04%** (rides beta); **425 clusters**, 33 STRONG
- Top cluster alpha: DDOG +68.94%, SNDK +51.17%, MRVL +31.68%

## Open decisions / blockers

- [TODO: DEV] Migrate legacy scripts to read canonically from `data/verified/` (copies synced).
- [TODO: DEFINE] Statistical-significance threshold for STRONG (t-test / bootstrap) — blocks VERIFIED.
- [TODO: APPROVE] Sign-off on live scrape + yfinance fetch as an approved external action (G-live).
- [TODO: REPORT FIELD] Add sector-adjusted benchmark (XSD ETF) column to verified output.

## Recipes with logged execution evidence

- `congressional-signal-agent` — 5 logged runs, latest `logs/run_20260630_163745.json`.

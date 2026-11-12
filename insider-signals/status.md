# status.md — Insider Signal Intelligence module

_Snapshot updated at the end of each working session. See `logs/RUN_LOG.md` for full history._

**Last updated:** 2026-11-09
**Fellow:** Gomathy S.
**Module:** `insider-signals/`, which contributes the `insider-signal-agent` recipe.

---

## Recipe lifecycle state

| Recipe | State | Evidence |
|--------|-------|----------|
| `insider-signal-agent` | **DRAFT** | 4 open TODOs; INGEST, PARSE, GIGO, ENRICH run on the study period (2023 Q2 – 2026 Q3); last gate G2 (cleared for the study period); G3 not yet cleared |

**Last gate:** G2 (parse + conformance), cleared by Gomathy S. on 2026-11-05 for the study period 2023 Q2 – 2026 Q3: 98 of 98 halting checks pass; 78,495 buys promoted (SHA-256 `a7ec5529…db75b16`); spot-check 25/25 consistent (`logs/RUN_LOG.md#2026-11-05`). Earlier: G2 cleared 2026-11-04 for 2026 Q3; G1 cleared 2026-11-04 for 2023 Q1 – 2026 Q3.

Lifecycle: `DRAFT → SPECIFIED → RUNNABLE-SAMPLE → RUNNABLE-LIVE → VERIFIED`

## Current dataset

- Source: SEC Insider Transactions Data Sets, study period **2023 Q2 – 2026 Q3** (14 quarters; changed 2026-11-04 from 2023 Q1 – 2026 Q3). 2023 Q1 is downloaded and kept on disk but is not in the study.
- Downloaded: **2023 Q1 – 2026 Q3** (15 quarters, G1 cleared 2026-11-04). Raw files are gitignored; `manifest.json` and `request_log.jsonl` are committed.
- Verified (2026-11-04, 14 study quarters): `data/verified/insider_buys.csv`, **78,495 buys**, SHA-256 `a7ec55298bf886c0090f7c5fc4e93bfb18faeabc5d4c407db8d77abefdb75b16` (gitignored; rebuild with `parse.py` + `conformance.py --quarters 2023q2:2026q3`). Eligible for clustering under Rules 1–6, 2a and 2b: **65,106**.
- Enriched (2026-11-09, not yet G3-cleared): `data/verified/enriched_buys.csv`, 78,495 rows, SHA-256 `fa14627333ac754a7f904e3417e5475241d7523659d46d6385779a7c65295bde` (gitignored). Price coverage **80.09%** after Rule 9 (minimum 80%, Rule 8); 2,352 buys `price_mismatch_vs_filing`; 63-day windows not yet closed: 3,114. Prices through 2026-11-06.

## Next actions (week 1–2)

- ~~Write `ingest.py` and its tests~~ (done 2026-11-03: 33 tests passing).
- ~~Ingest the full study period, run `--verify`, log the G1 decision~~ (done 2026-11-04: 2023 Q1 – 2026 Q3 downloaded; G1 cleared).
- ~~Start PARSE~~ (done 2026-11-03: 2026 Q3 gives 5,115 qualifying buys of 59,834 Form 4 rows; 57 tests passing).
- ~~Decide the private-purchase rule~~ (done 2026-11-04: `PRE_REGISTRATION.md` Rule 1).
- ~~GIGO `conformance.py`~~ (done 2026-11-04: all halting checks pass on 2026 Q3; 5,115 buys in `data/verified/insider_buys.csv`; spot-check 15 exact / 10 rounding only / 0 other; 83 tests passing).
- ~~Read the conformance audit and log the G2 decision~~ (G2 cleared 2026-11-04).
- ~~Decide the rounding and repeated-amendment handling~~ (2026-11-04: Rules 2–5 in `PRE_REGISTRATION.md`; 4,052 buys eligible for clustering in 2026 Q3).
- Identify fund and trust issuers and decide whether to exclude them (open item; not implemented).
- ~~Register the `is_10b5_1 = unknown` treatment~~ (2026-11-04: Rule 6).
- Rounding: settled for sub-$1 buys by Rule 4; for buys at $1.00 and above the 2-decimal rounding changes price by at most 0.5%, accepted as negligible.
- ~~Log the G2 decision for the study-period promotion~~ (G2 cleared 2026-11-05).
- ~~Close TODO 3 (4/A matching)~~ (2026-11-05: Rules 2, 2a and 2b).
- ~~Register the return windows and G3 coverage~~ (2026-11-09: Rules 7–8; TODOs 4 and 5 closed).
- ~~Build and run ENRICH~~ (2026-11-09: coverage 83.09%, then 80.09% after Rule 9; audit `data/verified/enrich-audit.md`).
- ~~Ticker sanity check~~ (2026-11-09: Rule 9).
- Read the enrich audit and log the G3 decision.
- Next stage after G3: SIGNALS (needs TODOs 7–9 and the cluster definition registered first).

## Open decisions / blockers

- G6 is a **self-attestation** (Gomathy S.) during development; external review pending.
- Survivorship risk: 8,832 buys have no price data, concentrated in older quarters, likely including delisted companies. Missing delisted stocks can bias results upward. Must be reported with the backtest.
- See the `[TODO]` list in `recipes/insider-signal-agent.md`.

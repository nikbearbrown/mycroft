# Attestation — DRAFT (unsigned)

> Prepared from real runs on 2026-07-13 and 2026-07-24. Per SNICKERDOODLE.md this record
> only becomes an attestation when a named human has personally judged the audits and the
> running system and signs below. Any edit to the recipe or its scripts after signing voids it.

## Attestation
- Recipe: insider-cluster-signal-agent v0.3.0
- By: **[PENDING — Sachin Vishaul Baskar to run the Tested table personally and sign]** · date: ____

### Tested
| Ran | Saw | Expected |
|---|---|---|
| `python fetcher.py --date 2026-03-02 --limit 10000` (in 10-day loop, stopped day 2) | 2,973 index lines -> 1,460 unique filings fetched, 2 errors, manifest with SHA-256 per file | Full day fetched with manifest provenance |
| `python parser.py` on 1,494 manifest-backed XMLs | 2,496 transactions -> 2,471 verified, 25 rejects with reasons, 0 unparseable | verified + rejected == extracted, rejects carry reasons |
| `python price_fetcher.py --start 2026-02-20 --end 2026-05-01` | 54/56 P-tickers priced, BBASX non-priceable (recorded, not dropped), 1 error | Non-priceable tickers recorded with evidence, not silently skipped |
| `python enricher.py` | 114 enriched, 112 with matured 30d alpha, 4 rejects | Immature windows marked with reason, never shortened |
| Hand recomputation of LAW/Friedrichsen 2026-02-27 alpha from raw CSVs | +20.7965 by hand = +20.7965 pipeline (exact) | Pipeline alpha reproducible from raw evidence |
| `python pipeline.py` (run_20260724_163957) | G1 PASSED -> 6 clusters -> 5 STRONG / 1 WATCH -> rule-based research -> dual outputs written | All 5 nodes execute; both customers' artifacts emitted |
| **Deliberate break 1:** conformance node pointed at empty dir | `failed=True`, findings name both missing files | Gate fails loudly, run halts |
| **Deliberate break 2:** trades summary with verified+rejected != extracted | `failed=True`, "LEDGER MISMATCH: 5 + 2 != 10" | Ledger inconsistency is a hard stop, not a warning |
| `python -m unittest discover tests` | 28/28 OK | All fixtures green, incl. alpha-never-classifies test |
| SHA-256 re-hash of raw filing vs manifest (BBASX filing, 2026-07-13) | MATCH | Raw evidence tamper-evident since fetch |

### Did not test
- Claude research node with a live ANTHROPIC_API_KEY (only the rule-based fallback path ran).
- EDGAR throttling behavior at sustained >1-day full-corpus fetch volumes (run was stopped in day 2).
- Ticker symbol collisions (issuer symbol reused/changed between filing date and price fetch).
- Price accuracy for tickers with splits/dividends inside the 30-day window (Yahoo chart closes
  are split-adjusted but the pipeline does not verify adjustment consistency per ticker).
- The signal-quality gate itself — Gate 3 is OPEN; the 19-filing spot-check in
  `data/verified/scored-signals-audit.md` has not been performed by a human.
- Windows-only environment; not run on Linux/macOS.

### Broke during testing, fixed
- Ticker "NONE" passed the non-empty validation rule (found in 2026-07-13 demo run) — placeholder
  and implausible-symbol rejection added to parser.py + tests.
- Stooq (first price-provider choice) served an anti-bot HTML wall to every programmatic request —
  provider re-decided same day to Yahoo v8 chart API; evidence in price-manifest response_head.
- 1,998 unmanifested day-2 XMLs were accidentally committed (module .gitignore gap) — removed
  from version control, gitignore extended; noted in RUN_LOG.
- Fetcher re-downloaded ~1.5k duplicate accessions (daily index repeats filings per joint filer) —
  logged as an improvement TODO; idempotent overwrites made it harmless.

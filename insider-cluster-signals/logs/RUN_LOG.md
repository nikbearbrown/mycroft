# RUN_LOG — insider-cluster-signals

Append-only (P7). Every script run against real data, every gate decision, every blocker.

## 2026-07-12 -- Week 1 data spine: first live fetch + parse (sample mode)

- **Recipe:** insider-cluster-signal-agent (pre-DRAFT; recipe file lands Week 4)
- **Inputs:** SEC EDGAR daily form index for 2026-07-10 (last business day before this run)
- **Commands:**
  - `python fetcher.py --date 2026-07-10 --limit 10`
  - `python parser.py`
- **Outputs:**
  - `data/raw/form4/*.xml` — 10 filings (provenance + SHA-256 in `data/raw/fetch-manifest-20260710.json`)
  - `data/verified/trades.json` — 11 transaction records
  - `data/raw/parse-rejects.json` — 0 rejects, 0 unparseable files
- **Result:** Index reported 694 Form 4 filings for 2026-07-10; sample cap of 10 fetched with 0 errors.
  All 11 extracted transactions passed the validation gate. Fetch → parse → verified chain works
  end-to-end on live data.
- **Open issues:**
  - Sample only (10 of 694). Scale run pending Week 2 alongside enricher.
  - `price_per_share = 0` is legitimate for codes like G (gift) — enricher must not treat it as a data error.
  - One filing contained 2 transactions (11 records from 10 filings) — parser handles multi-transaction
    filings correctly; keep a fixture for this case in tests/.

## 2026-07-13 -- Demo run: second sample date + provenance walk

- **Inputs:** EDGAR daily form index 2026-07-09 (623 Form 4 filings).
- **Commands:** `python fetcher.py --date 2026-07-09 --limit 25` · `python parser.py`
- **Gate decision (live fetch):** approved by Sachin Vishaul Baskar in-session ("see it in action"),
  same scope as 2026-07-12 entry: public EDGAR, sample mode, fair-access honored.
- **Result:** 25 fetched, 0 errors. Corpus now 34 unique filings -> 57 records, 57 verified, 0 rejects.
  Code mix: 32 S, 17 A, 4 P, 2 F, 1 G, 1 M. Found a live cluster candidate: 2 distinct 10%-owners
  bought BBASX same day (2026-07-07). Provenance chain verified: record -> manifest -> SHA-256
  re-hash MATCH -> EDGAR URL.
- **Open issues:**
  - Validation gap found: ticker "NONE" (issuer without a trading symbol) passes the non-empty
    rule. Enricher/cluster must exclude non-priceable tickers; add explicit rule in Week 2.
  - One accession appeared in both days' indexes (34 files from 10+25 fetches) — idempotent
    overwrite worked as designed; parser de-duplicates by accession naturally.

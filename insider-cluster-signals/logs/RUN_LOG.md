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

## 2026-07-13 -- Gate decision: Week 2 historical scale run (approved BEFORE execution)

- **Decision:** approved by Sachin Vishaul Baskar via Week 2 plan approval (plan file:
  "Scale run (gated)" section), recorded here before any request is sent.
- **Scope:** EDGAR daily form indexes 2026-03-02 .. 2026-03-13 (10 trading days), full fetch
  (no sample cap), ~6.5k filings expected, ~13k rate-limited requests (~40 min), SEC
  fair-access honored. Then: parse -> Yahoo price fetch (P tickers + SPY, window padded
  2026-02-20 .. 2026-05-01) -> enrich -> cluster. March chosen so every 30-day alpha
  window is fully matured.

## 2026-07-13 -- Scale run executed (stopped early; 1 complete day) + first real clusters

- **What happened:** the 10-day fetch was stopped during day 2. Day 1 (2026-03-02) completed
  with a manifest: 2,973 index lines -> 1,460 unique filings fetched (2 errors). The 1,998
  day-2 XMLs fetched before the stop have no manifest -> **archived to
  `data/raw/form4-unmanifested/`** and excluded from parsing (P3: no provenance, no entry).
- **Finding (fetcher improvement TODO):** the daily form index repeats a filing once per
  joint filer — 2,971 fetch entries were only 1,460 unique accessions; fetcher should dedupe
  by accession before fetching (idempotent overwrites made this harmless but wasteful).
- **Commands:** fetcher (10-day loop, killed in day 2) -> parser -> price_fetcher
  (--start 2026-02-20 --end 2026-05-01) -> enricher -> cluster_analyzer.
- **Results (manifest-backed corpus: 2026-03-02 + July samples):**
  - parse: 1,494 XMLs -> 2,496 transactions, 2,471 verified, 25 rejected (reasons recorded)
  - prices: 56 P-tickers requested, 54 priced, BBASX non-priceable, 1 error
  - enrich: 114 market trades enriched, 112 with matured 30d alpha, 4 rejects
  - clusters: **6 found** — GENB (4 insiders, conviction 5.0, +13.9 alpha), CTEV (3, 4.5, +22.3),
    LRMR (4, 4.0, -5.4), TNC (3, 3.5, +15.5), LAW (2, 2.5, +24.4), PVLA (2, 2.0, -9.2)
- **Hand verification (P3):** LAW / Friedrichsen (CEO) 2026-02-27 buy at 3.25 recomputed by
  hand from raw CSVs: stock +13.2308%, SPY -7.5657% -> alpha +20.7965 = pipeline value exactly.
- **Open issues:** corpus is 1 trading day, not 10 — remaining 9 days can be fetched later
  under the same logged gate; negative-alpha clusters (LRMR, PVLA) are evidence the detector
  reports what it finds, not what flatters the method.

## 2026-07-24 -- Week 3+4: scorer, gated pipeline (first full run), audit, attestation draft

- **Commands:** `python signal_scorer.py` · `python pipeline.py` (run_20260724_163957) ·
  `python audit_signals.py` · `python -m unittest discover tests` (28/28).
- **Pipeline run:** G1 conformance PASSED (2,471 verified / 114 enriched / 112 alpha) ->
  6 clusters -> 5 STRONG (GENB, LRMR, CTEV, TNC, LAW) / 1 WATCH (PVLA) / 0 SKIP ->
  research node ran rule-based fallback (no ANTHROPIC_API_KEY in env) -> dual outputs:
  logs/run_20260724_163957.json + reports/signal_report_20260724_163957.md (P5).
- **Break tests (P4):** conformance gate halts on (a) missing verified files and (b) ledger
  mismatch (verified+rejected != extracted) — both returned failed=True with named findings.
- **Artifacts:** data/verified/scored_signals.json · scored-signals-audit.md (19 filings for
  the Gate-3 human spot-check) · ATTESTATION-DRAFT.md (unsigned; Did-not-test list included).
- **Recipe:** v0.3.0, todos_open 2 -> 1. Remaining TODO is the Gate-3 APPROVE — deliberately
  left open: it can only be closed by a named human performing the spot-check and logging it.
- **Open issues:** research node untested with a live API key; corpus is 1 trading day;
  attestation unsigned until the human runs the Tested table themselves.

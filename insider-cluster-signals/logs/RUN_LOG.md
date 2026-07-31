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

## 2026-07-24 -- Week 5: fetcher dedupe (TODO closed) + cross-regime study (no new data)

- **TODO closure (2026-07-13 fetcher-improvement):** `dedupe_by_accession` in fetcher.py —
  one fetch per unique accession (~50% fewer requests on joint-filer-heavy days); manifest
  now reports `form4_index_lines` vs `form4_filings_in_index`. Evidence: 4 no-network unit
  tests (suite 32/32), commit dc0afbb.
- **Import (P2/P3):** congressional clusters from upstream PR #3 (`pr-3` local object,
  source commit 823592e9, sha256 in `data/raw/congressional-import/PROVENANCE.md`) — RAW
  third-party claim, shape-validated by cross_regime.py, not independently verified.
- **Commands:** `python cross_regime.py` -> `reports/cross_regime_study.md`. Two numbers
  hand-recomputed from source JSONs: their mean avg_alpha 0.38 (n=369/425, nulls excluded)
  and cluster counts — both match the report exactly.
- **Result:** corporate clusters (n=6, 1-day corpus) mean 30d alpha +10.25% vs congressional
  population +0.38%. Headline finding is methodological: the congressional scorer classifies
  USING realized alpha (avg_alpha > 1% -> STRONG = look-ahead bias), ours never does — tier
  hit-rates across the two modules are NOT comparable, only population alpha is.
- **Open issues:** corporate sample remains 1 trading day (illustrative, not statistical);
  their null-alpha clusters (56 of 425) excluded from means; backtest deferred to a future
  sprint alongside the remaining 9 gated fetch days.

## 2026-07-24 -- Week 6: signal dashboard (static, brutalist-compliant)

- **Commands:** `python build_dashboard.py` -> `reports/dashboard.html` (6 cards, 19 audit
  rows) · `python -m unittest discover tests` (38/38).
- **What it is:** second human-customer artifact (P5) beside the markdown report — one
  self-contained HTML page (no server, no framework, no fetch; data inlined at build time
  from `scored_signals.json` + run log + fetch manifests). Signal cards with tier badge,
  conviction, alpha bar, members, tier reason; per-card evidence drawer linking every
  accession to its EDGAR URL + sha256; Gate-3 worksheet rendered as a reading aid with an
  explicit note that only the logged human decision closes the gate.
- **Design compliance:** brutalist/DESIGN.md — 6 palette tokens only (test-enforced:
  test_only_design_md_hex_colors), EB Garamond/Inter/JetBrains Mono stack, red = STRONG
  badge only (brand/emphasis rule), alpha bars ink/secondary (red never encodes valence).
- **Open issues:** dashboard reflects the latest pipeline run only; rebuild after each run
  (documented in README). Checkbox state is not persisted (deliberate — the gate record
  lives in the log, not the browser).

## 2026-07-27 -- Full-system E2E verification (Playwright) — network-first, then offline re-run

- **Design:** network-dependent checks executed FIRST (connection was expected to drop, and did);
  all remaining checks are local-only. The offline re-run repeated the entire local suite with
  the internet down — everything passed, proving the system's core loop needs no network.
- **Backend (10 checks, all PASS):** unit suite 38/38 · ledger verified+rejected==extracted
  (2471+25==2496) · sha256 re-hash of 5 random raw XMLs vs manifests (all match) · hand-recomputed
  LAW alpha == pipeline (20.7965) · fresh pipeline runs (run_20260727_212745 online,
  run_20260727_213858 offline; identical signals) · conformance gate halts on ledger mismatch AND
  missing files · scorer determinism (two runs identical) · dashboard + audit rebuilt from fresh run
  · LIVE: EDGAR fetch w/ dedupe (694 index lines -> 327 unique, 3 fetched to temp dir, corpus
  untouched) · LIVE: Yahoo SPY prices (10 rows) · LIVE: 2 evidence URLs HTTP 200.
- **Frontend (19 Playwright checks vs Chromium, all PASS after one fix):** loads via file:// with
  zero JS errors (offline too — fonts degrade gracefully) · DOM==verified-JSON parity (cards,
  ticker order, badge counts per tier) · all 4 filter interactions · 19 evidence links all
  well-formed sec.gov URLs · alpha-bar valence classes match data · audit rows == accessions ·
  computed style: STRONG badge renders exactly #C8102E, canvas #FFFFFF (DESIGN.md) · no horizontal
  overflow at 375px.
- **Defect found and fixed by the suite:** count tiles overflowed 59px at mobile width (375px) —
  `.counts` now wraps (flex-wrap) + `.sub` gains overflow-wrap. Rebuilt, re-verified: 0px overflow.
- **Test-script defect (not a system defect):** hardcoded run-id assertion went stale when the
  offline run produced a newer run — made dynamic; the dashboard correctly tracks the latest run.
- **Open issues:** push to fork pending network restoration; Playwright scripts live in the session
  scratchpad (not committed — module stays stdlib-only).

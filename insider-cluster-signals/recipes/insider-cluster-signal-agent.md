---
status: DRAFT
todos_open: 2
last_gate: "scale-run approval (2026-03-02..13 historical corpus), 2026-07-13, logs/RUN_LOG.md#2026-07-13"
attestation: null
recipe_version: 0.2.0
---

# Insider Cluster Signal Agent

## Purpose

Turn public SEC Form 4 insider-trade disclosures into sourced STRONG / WATCH / SKIP research
signals by detecting clustered insider buying (2+ distinct insiders, same ticker, 30-day
window), benchmarked per-trade against SPY. Research only — no trades placed, no financial
advice. The human decides what, if anything, a signal means; the pipeline only prepares
evidence (P1).

## Source Inventory

| Source | Type | URL / Path | Human check |
|---|---|---|---|
| EDGAR daily form index | Fixed-width text | `https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{q}/form.{yyyymmdd}.idx` | Public, no key. Fair-access: declared User-Agent, <10 req/s. |
| Form 4 ownershipDocument | XML | Resolved per filing via directory `index.json` | Form type matched exactly `4`; amendments (4/A) excluded. |
| Price history (per P-ticker + SPY) | JSON → Date,Close CSV | Yahoo Finance v8 chart API (`query1.finance.yahoo.com/v8/finance/chart/{sym}`) | **DATA SOURCE closed 2026-07-13 (Sachin Vishaul Baskar):** first choice Stooq CSV was re-decided same day after Stooq served an anti-bot HTML wall to every programmatic request (evidence: `data/raw/price-manifest-*.json` `response_head`). Yahoo v8 = same source yfinance wraps; parity with congressional-signals sibling. Research use, rate-limited 0.5s. |

## Definitions (DEFINE closures)

- **Cluster** = ≥2 distinct `owner_cik`, same ticker, open-market purchases (code P) only,
  all dates within a greedy chronological 30-day window. Mirrors the congressional-signals
  window for cross-regime comparability.
- **Role weights** (closed 2026-07-13): officer 1.5, director 1.0, 10%-owner 0.75, other 0.5 —
  officers trade closest to operating information; large holders often rebalance mechanically
  (routine-vs-opportunistic gradient, Cohen/Malloy/Pomorski 2012).
- **Alpha** = `raw_return_30d − spy_return_30d`, closes at nearest prior trading day, formula
  mirrors `congressional-signals/market_adjusted.py` (branch pr-3). Immature windows are
  marked with a reason, never silently shortened.

## Phase Gates

1. **Live-fetch approval:** any network call requires a logged human approval naming scope and
   rate policy. Evidence: RUN_LOG entries. *Cleared 2026-07-12 (sample, limit 10) and
   2026-07-13 (scale run, 10 trading days of 2026-03) by Sachin Vishaul Baskar.*
2. **Data-shape gate:** every record entering `data/verified/` passes all validation rules in
   `parser.py` (incl. placeholder-ticker rejection); rejects recorded with reasons.
   Machine-testable: `records_verified + records_rejected == records_extracted`.
3. **Signal-quality gate:** [TODO: APPROVE] before any signal report is shared beyond this repo,
   a named human spot-checks >= 10 signals against their EDGAR source filings and logs the
   decision.
4. **Report gate:** run emits both customers' artifacts (P5): `logs/run_*.json` (agent) and
   `reports/signal_report_*.md` (human). Test: both files exist for the run ID.

## Steps

1. **Fetch** — `fetcher.py` (exists; verified live 2026-07-12/13). Labor: AI, gated by Gate 1.
   Output: raw XML + SHA-256 manifest -> `data/raw/`.
2. **Parse + validate** — `parser.py` (exists; 11 unit tests). Labor: AI.
   Output: `data/verified/trades.json` + rejects with reasons.
3. **Price fetch** — `price_fetcher.py` (exists; DEV closed 2026-07-13). Labor: AI, gated by Gate 1.
   Output: `data/raw/prices/{TICKER}.csv` + SHA-256 manifest.
4. **Enrich** — `enricher.py` (exists; DEV closed 2026-07-13; hand-computed return test). Labor: AI.
   Output: `data/verified/enriched_trades.json`; price-0 market trades and non-priceable
   tickers -> rejects with reasons.
5. **Cluster** — `cluster_analyzer.py` (exists; DEV closed 2026-07-13; 10 unit tests). Labor: AI.
   Output: `data/verified/cluster_signals.json`, every cluster tracing to its accessions.
6. **Score + report** — `signal_scorer.py` [TODO: DEV] conviction + alpha -> STRONG/WATCH/SKIP;
   emit agent log + human report per the Output Contract. (Week 3.)

## Output Contract

**Agent log** `logs/run_<timestamp>.json`: run_id, mode, filings_seen, records_verified,
rejects, clusters_found, signals {strong, watch, skip}, gate_decisions, source manifest paths.

**Human report** `reports/signal_report_<timestamp>.md`:
Reader: a researcher deciding whether any cluster merits deeper investigation.
Decision enabled: pursue / ignore each STRONG signal, with the evidence trail one click away.
Sections: run summary, method, per-signal table (ticker, insiders, roles, dates, alpha vs SPY,
EDGAR links), rejects summary, limitations, provenance chain.

## Stop Conditions

- Stop if EDGAR or Yahoo responds with throttling or errors on >10% of requests.
- Stop if any credential, key, or token would need to be hardcoded (none should exist).
- Stop if a signal would be emitted without a traceable accession URL (P3).
- Stop if output would state or imply investment advice.

## Provenance

Signal -> cluster -> enriched trade -> verified trade record -> raw XML (SHA-256 in fetch
manifest) -> EDGAR accession URL; prices trace to the Yahoo chart URL + SHA-256 in the price
manifest. See `DATA_CONTRACT.md`.

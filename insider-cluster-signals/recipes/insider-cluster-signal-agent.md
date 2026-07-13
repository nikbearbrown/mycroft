---
status: DRAFT
todos_open: 5
last_gate: "live-fetch approval (sample, limit 10), 2026-07-12, logs/RUN_LOG.md#2026-07-12"
attestation: null
recipe_version: 0.1.0
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
| Price history (per ticker + SPY) | JSON/CSV | [TODO: DATA SOURCE] Choose provider (stooq CSV vs yfinance) with provenance note — needed by enricher. | Free tier limits; document rate policy before live use. |

## Phase Gates

1. **Live-fetch approval:** any network call requires a logged human approval naming scope and
   rate policy. Evidence: RUN_LOG entry. *Cleared 2026-07-12 for sample mode (limit 10) by
   Sachin Vishaul Baskar.*
2. **Data-shape gate:** every record entering `data/verified/` passes all 6 validation rules in
   `parser.py`; rejects recorded with reasons. Machine-testable: rejects file exists and
   `records_verified + records_rejected == records_extracted`.
3. **Signal-quality gate:** [TODO: APPROVE] before any signal report is shared beyond this repo,
   a named human spot-checks >= 10 signals against their EDGAR source filings and logs the
   decision.
4. **Report gate:** run emits both customers' artifacts (P5): `logs/run_*.json` (agent) and
   `reports/signal_report_*.md` (human). Test: both files exist for the run ID.

## Steps

1. **Fetch** — `fetcher.py` (exists, verified live 2026-07-12). Labor: AI, gated by Gate 1.
   Output: raw XML + SHA-256 manifest -> `data/raw/`.
2. **Parse + validate** — `parser.py` (exists, verified live 2026-07-12). Labor: AI.
   Output: `data/verified/trades.json` + rejects with reasons.
3. **Enrich** — `enricher.py` [TODO: DEV] SPY-matched per-trade returns; must treat
   `price_per_share = 0` codes (G gifts, A awards) as non-market rows, not errors.
4. **Cluster** — `cluster_analyzer.py` [TODO: DEV] 2+ distinct `owner_cik`, same ticker,
   30-day window, open-market purchases (code P) only; role-weighted (officer > director).
5. **Score + report** — `signal_scorer.py` [TODO: DEV] conviction score -> STRONG/WATCH/SKIP;
   emit agent log + human report per the Output Contract.

## Output Contract

**Agent log** `logs/run_<timestamp>.json`: run_id, mode, filings_seen, records_verified,
rejects, clusters_found, signals {strong, watch, skip}, gate_decisions, source manifest paths.

**Human report** `reports/signal_report_<timestamp>.md`:
Reader: a researcher deciding whether any cluster merits deeper investigation.
Decision enabled: pursue / ignore each STRONG signal, with the evidence trail one click away.
Sections: run summary, method, per-signal table (ticker, insiders, roles, dates, alpha vs SPY,
EDGAR links), rejects summary, limitations, provenance chain.

## Stop Conditions

- Stop if EDGAR responds with throttling or errors on >10% of requests.
- Stop if any credential, key, or token would need to be hardcoded (none should exist).
- Stop if a signal would be emitted without a traceable accession URL (P3).
- Stop if output would state or imply investment advice.

## Provenance

Signal -> cluster -> verified trade record -> raw XML (SHA-256 in fetch manifest) -> EDGAR
accession URL. See `DATA_CONTRACT.md`.

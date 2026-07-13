# Data Contract — insider-cluster-signals

Two-layer architecture per SNICKERDOODLE.md P2: exactly two scripts touch the network —
`fetcher.py` (EDGAR filings) and `price_fetcher.py` (Yahoo daily closes) — and nothing
enters `data/verified/` without passing validation (`parser.py` for trades, `enricher.py`
for price joins).

## Layers

| Layer | Path | Written by | Contents |
|---|---|---|---|
| Raw | `data/raw/form4/*.xml` | `fetcher.py` | Unmodified ownershipDocument XML, byte-for-byte as served by EDGAR |
| Raw | `data/raw/fetch-manifest-*.json` | `fetcher.py` | Provenance: index date, URL, SHA-256, bytes, fetch timestamp per filing |
| Raw | `data/raw/parse-rejects.json` | `parser.py` | Records failing validation, each with explicit `reject_reasons` |
| Raw | `data/raw/prices/{TICKER}.csv` | `price_fetcher.py` | Date,Close daily series (P-code tickers + SPY) |
| Raw | `data/raw/price-manifest-*.json` | `price_fetcher.py` | Provenance: URL, SHA-256, row count per series; non-priceable tickers with response evidence |
| Raw | `data/raw/enrichment-rejects.json` | `enricher.py` | Market trades that could not be enriched, with reasons |
| Verified | `data/verified/trades.json` | `parser.py` | Normalized trade records that passed ALL validation rules |
| Verified | `data/verified/enriched_trades.json` | `enricher.py` | Market trades + close_t0 + 30d raw/SPY/alpha returns (immature windows marked, never shortened) |
| Verified | `data/verified/cluster_signals.json` | `cluster_analyzer.py` | ≥2-insider 30-day buy clusters, role-weighted, tracing to accessions |

## Sources

**SEC EDGAR daily form index → Form 4 filings (ownershipDocument XML).**

- Index: `https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{q}/form.{yyyymmdd}.idx`
- Free, public, no API key. Fair-access policy honored: declared User-Agent, <10 req/s.
- Form type matched **exactly** `4` — amendments (`4/A`) and other 4xx forms excluded.

**Yahoo Finance v8 chart API → daily closes (P-code tickers + SPY benchmark).**

- `https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=..&period2=..&interval=1d`
- Decision history (human-closed DATA SOURCE): Stooq chosen first (2026-07-13), re-decided
  same day after Stooq served an anti-bot HTML wall to every programmatic request — evidence
  preserved in `price-manifest` `response_head` fields. Yahoo v8 is the same source yfinance
  wraps (parity with the congressional-signals sibling). Research use; rate-limited 0.5s;
  browser-style User-Agent required by the endpoint (contact intent documented here).

## Validation rules (the raw → verified gate)

A record enters `data/verified/` only if ALL hold:

1. `ticker` non-empty
2. `owner_name` non-empty
3. `transaction_code` in the SEC Form 4 code set (P, S, A, F, D, G, V, J, K, C, E, H, I, M, O, U, W, X, L, Z)
4. `acquired_disposed` is exactly `A` or `D`
5. `transaction_date` parses as ISO `YYYY-MM-DD`
6. `shares` and `price_per_share` numeric and non-negative

Anything else lands in `parse-rejects.json` with its reasons — rejects are recorded, never dropped (P3).

## Provenance chain

signal → cluster → verified trade record → raw XML (SHA-256 in fetch manifest) → EDGAR accession URL.
Every layer is on disk; every hop is reproducible.

## Version control policy

- Committed: fetch manifests, rejects, `data/verified/trades.json` sample outputs, all scripts.
- Gitignored: bulk `data/raw/form4/*.xml` (regenerable via `fetcher.py` from the manifest's URLs).

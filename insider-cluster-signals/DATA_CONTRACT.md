# Data Contract — insider-cluster-signals

Two-layer architecture per SNICKERDOODLE.md P2: only `fetcher.py` touches the network;
nothing enters `data/verified/` without passing every validation rule in `parser.py`.

## Layers

| Layer | Path | Written by | Contents |
|---|---|---|---|
| Raw | `data/raw/form4/*.xml` | `fetcher.py` | Unmodified ownershipDocument XML, byte-for-byte as served by EDGAR |
| Raw | `data/raw/fetch-manifest-*.json` | `fetcher.py` | Provenance: index date, URL, SHA-256, bytes, fetch timestamp per filing |
| Raw | `data/raw/parse-rejects.json` | `parser.py` | Records failing validation, each with explicit `reject_reasons` |
| Verified | `data/verified/trades.json` | `parser.py` | Normalized trade records that passed ALL validation rules |

## Source

SEC EDGAR daily form index → Form 4 filings (ownershipDocument XML).

- Index: `https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{q}/form.{yyyymmdd}.idx`
- Free, public, no API key. Fair-access policy honored: declared User-Agent, <10 req/s.
- Form type matched **exactly** `4` — amendments (`4/A`) and other 4xx forms excluded.

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

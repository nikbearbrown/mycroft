# Step 2 ingest audit: portfolio-price-fetcher, set `clean`

Source: Yahoo Finance chart API (stood in for by invented sample fixtures). Type: sample fixtures (invented Yahoo Finance chart responses). Fetched at 2026-10-10T00:00:00Z (sample mode: true).
Records ingested: 5. Rejects: 0.

| File | Manifest | SHA-256 (first 12) | What it exercises |
|---|---|---|---|
| clean/AMD.json | manifest.json | 532888a5c92e | loss |
| clean/GOOGL.json | manifest.json | dbc623c1b7a4 | regularMarketPrice null: falls back to previousClose |
| clean/META.json | manifest.json | aa1eaca6a180 | regularMarketPrice 0: JavaScript || treats 0 as missing, falls back |
| clean/MSFT.json | manifest.json | d51610de8e6b | gain |
| clean/NVDA.json | manifest.json | 2633560d6573 | gain; total-value rounding tie (.125) |

## Rejects

None.

## Naming ledger (file names only)

- Holdings declared by the workflow: AMD, GOOGL, META, MSFT, NVDA.
- Holdings with no file named for them: none.
- Files named for no holding: none.
- Files named for one holding: none

This step ingests; it does not judge. A response with no price, an unknown ticker, an empty result, or a second response for a ticker is ingested like any other. Step 3 judges each response and step 4 judges the set.

Follows step 1: {"approval_state": "no approval record: live mode not approved; sample mode only", "checked_at": "2026-10-10T00:00:00+00:00", "file": "logs/portfolio-price-fetcher-provenance-2026-10-10.json", "found": true, "readable": true, "result": "pass"}

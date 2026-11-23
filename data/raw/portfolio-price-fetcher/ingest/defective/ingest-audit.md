# Step 2 ingest audit: portfolio-price-fetcher, set `defective`

Source: Yahoo Finance chart API (stood in for by invented sample fixtures). Type: sample fixtures (invented Yahoo Finance chart responses). Fetched at 2026-10-10T00:00:00Z (sample mode: true).
Records ingested: 4. Rejects: 1.

| File | Manifest | SHA-256 (first 12) | What it exercises |
|---|---|---|---|
| defective/empty-result.json | manifest.json | d901b4ecddfa | - |
| defective/no-price.json | manifest.json | e528c9c8e056 | - |
| defective/price-not-a-number.json | manifest.json | 7e8d4775700c | - |
| defective/unknown-ticker.json | manifest.json | a949da2ddade | - |

## Rejects

- `defective/truncated-json.txt`: not valid JSON (Invalid control character at)

## Naming ledger (file names only)

- Holdings declared by the workflow: AMD, GOOGL, META, MSFT, NVDA.
- Holdings with no file named for them: AMD, GOOGL, META, MSFT, NVDA.
- Files named for no holding: empty-result.json, no-price.json, price-not-a-number.json, unknown-ticker.json.
- Files named for one holding: none

This step ingests; it does not judge. A response with no price, an unknown ticker, an empty result, or a second response for a ticker is ingested like any other. Step 3 judges each response and step 4 judges the set.

Follows step 1: {"approval_state": "no approval record: live mode not approved; sample mode only", "checked_at": "2026-10-10T00:00:00+00:00", "file": "logs/portfolio-price-fetcher-provenance-2026-10-10.json", "found": true, "readable": true, "result": "pass"}

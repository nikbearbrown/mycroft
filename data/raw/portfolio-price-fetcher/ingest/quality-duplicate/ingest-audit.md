# Step 2 ingest audit: portfolio-price-fetcher, set `quality-duplicate`

Source: Yahoo Finance chart API (stood in for by invented sample fixtures). Type: sample fixtures (invented Yahoo Finance chart responses). Fetched at 2026-10-10T00:00:00Z (sample mode: true).
Records ingested: 6. Rejects: 0.

| File | Manifest | SHA-256 (first 12) | What it exercises |
|---|---|---|---|
| quality-duplicate/AMD.json | quality-manifest.json | 532888a5c92e | two valid responses for NVDA that disagree |
| quality-duplicate/GOOGL.json | quality-manifest.json | dbc623c1b7a4 | two valid responses for NVDA that disagree |
| quality-duplicate/META.json | quality-manifest.json | aa1eaca6a180 | two valid responses for NVDA that disagree |
| quality-duplicate/MSFT.json | quality-manifest.json | d51610de8e6b | two valid responses for NVDA that disagree |
| quality-duplicate/NVDA-restated.json | quality-manifest.json | 4e18428b4e96 | two valid responses for NVDA that disagree |
| quality-duplicate/NVDA.json | quality-manifest.json | 2633560d6573 | two valid responses for NVDA that disagree |

## Rejects

None.

## Naming ledger (file names only)

- Holdings declared by the workflow: AMD, GOOGL, META, MSFT, NVDA.
- Holdings with no file named for them: none.
- Files named for no holding: none.
- Files named for one holding: NVDA: NVDA-restated.json, NVDA.json

This step ingests; it does not judge. A response with no price, an unknown ticker, an empty result, or a second response for a ticker is ingested like any other. Step 3 judges each response and step 4 judges the set.

Follows step 1: {"approval_state": "no approval record: live mode not approved; sample mode only", "checked_at": "2026-10-10T00:00:00+00:00", "file": "logs/portfolio-price-fetcher-provenance-2026-10-10.json", "found": true, "readable": true, "result": "pass"}

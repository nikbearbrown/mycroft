# Step 3 audit: portfolio-price-fetcher, fixture set `defective`

Files read: 5 · promoted: 0 · rejected: 5 · parse errors: 1

Contract: yahoo-chart-meta/1 (fields read by the workflow's Calculate Metrics node)

## Promoted

| File | Ticker | Effective price | Taken from |
|---|---|---|---|
| (none) | | | |

## Rejected

| File | Reason |
|---|---|
| empty-result.json | chart.result is missing or empty (the original reads result[0]) |
| no-price.json | neither regularMarketPrice nor previousClose is present |
| price-not-a-number.json | effective price 'abc' is not a finite number > 0 |
| truncated-json.txt | the response is not valid JSON |
| unknown-ticker.json | meta.symbol 'ZZZZ' is not in the workflow's portfolio |

This audit reports what it found; it does not say pass. Whether the rejects are acceptable is a human call (gate 3).

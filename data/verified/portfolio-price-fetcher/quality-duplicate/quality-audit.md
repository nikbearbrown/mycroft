# Step 4 audit: portfolio-price-fetcher, fixture set `quality-duplicate`

Records read from step 3: 6 · verified: 4 of 5 holdings · duplicates: 1 · rejected: 2 · flags: 3

## Verified records

| Ticker | Price | Taken from | Day change | Price / buy price | Flags |
|---|---|---|---|---|---|
| MSFT | 412.0 | regularMarketPrice | +0.61% | 1.177 | none |
| GOOGL | 166.0 | previousClose | n/a | 1.186 | PRICE_FELL_BACK |
| META | 590.0 | previousClose | n/a | 1.844 | PRICE_FELL_BACK |
| AMD | 102.0 | regularMarketPrice | -2.16% | 0.85 | none |

## Flags

| Ticker | Code | Severity | Detail |
|---|---|---|---|
| NVDA | HOLDING_MISSING | high | no verified price for NVDA (its records conflict (see rejects)); the portfolio summary would leave out 50 shares, cost basis 22,500.00 |
| GOOGL | PRICE_FELL_BACK | medium | regularMarketPrice was null; the previous close 166.0 was used, so this is yesterday's price, not today's |
| META | PRICE_FELL_BACK | medium | regularMarketPrice was 0; the previous close 590.0 was used, so this is yesterday's price, not today's |

## Duplicates and rejects

| Ticker | Files | Identical | Action |
|---|---|---|---|
| NVDA | NVDA-restated.json, NVDA.json | False | rejected every record for this ticker; a person decides which is right |

| Rejected file | Reason |
|---|---|
| NVDA-restated.json | conflicting records for NVDA: 530.0 (NVDA-restated.json) vs 504.5625 (NVDA.json) |
| NVDA.json | conflicting records for NVDA: 530.0 (NVDA-restated.json) vs 504.5625 (NVDA.json) |

## Notes

- The three numeric lines are ours, a judgment, not the workflow's: day move 15%, price over 3x or under 0.33x the buy price. A flag asks a person to look; it is not a verdict.
- Every price in the sample corpus is invented. These checks say nothing about any real market.
- Step 5 still reads step 3's output; this step's verified_records are written beside it for the report to cross-check.

This audit reports what it found; it does not say pass. Whether a flag matters, and which of two conflicting prices is right, is a human call (gate 3).

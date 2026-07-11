# Data Contract: Forward Price to Earnings Ratio

Spot-checked against the underlying price and earnings data myself; this is a price-derived market metric, not a filing, so it cannot be "Verified" against a filing the way the other contracts are.

| Field | Value |
|---|---|
| Source | stockanalysis.com/stocks/meta/statistics/ (context only, price-derived, not a filing) — explicitly labels and reports a "forward PE ratio" field, unlike macrotrends |
| Period | As of July 10, 2026 |
| Entity | Meta Platforms Inc |
| Version/accession | N/A, this is a market data reference, not a filing accession |
| Owner | me |
| Freshness need | High — a price-derived ratio goes stale daily; needs a fresh pull at time of use |
| Retrieval-timestamp | 2026-07-11 |
| Verified? | Spot-checked, not filing-verified (see note) |

**Source resolved:** the prior citation (macrotrends.net's pe-ratio page) was confirmed to be trailing P/E only, not forward. Replaced with stockanalysis.com's statistics page, which reports forward P/E as a distinct, explicitly labeled field. GuruFocus's forward-PE field was used as a secondary cross-check.

**Current figure:** stockanalysis.com reports META's forward P/E at 19.37 as of July 10, 2026 (trailing P/E on the same page: 22.97).

**Material change since the last check (2026-07-04):** this is materially higher than the ~17 figure spot-checked a week earlier. In the interim, META rallied sharply — reported as the best-performing stock in the S&P 500 on a Friday session — on investor enthusiasm around AI-monetization progress (new low-cost AI pricing, infrastructure plans, and product launches like Muse Image). Price moved up faster than the consensus forward-EPS estimate did, which mechanically pushes the forward P/E higher. This is a real, source-confirmed move, not a data-quality issue — but it means the "about 17" framing from the prior check is now stale and should not be reused without a fresh pull.

**Cross-check for internal consistency:** macrotrends' trailing P/E read 19.72 as of July 8, 2026, versus stockanalysis.com's trailing P/E of 22.97 as of July 10. The two-day gap and likely differences in trailing-EPS basis (e.g., inclusion/exclusion of one-time items) account for some of the gap; treat any single-source trailing or forward P/E as an approximation and re-pull at time of use rather than treating either number as precise to the decimal.

**Caveat retained:** given how much this moved in one week, this metric should be re-pulled immediately before use in any decision, not read from this file.
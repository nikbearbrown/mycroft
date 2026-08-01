# Data Contract: Analyst Consensus Estimates — META

Context-only source, per sources-of-truth.md — this is a third-party aggregation of analyst estimates, not a filing, and is not a substitute for reported actuals.

| Field | Value |
|---|---|
| Source | Yahoo Finance, ticker page → Analysis tab (finance.yahoo.com/quote/META/analysis) |
| Supplied by | human (pasted into conversation, not fetched by the assistant) |
| Retrieval date | 2026-07-23 (date supplied; Yahoo does not stamp an exact pull time) |
| Entity | Meta Platforms Inc |
| Periods covered | Current Qtr. (Jun 2026), Next Qtr. (Sep 2026), Current Year (2026), Next Year (2027) |
| Verified? | Not filing-verified — this is a consensus estimate, which by definition has no single authoritative source to verify against. Treated as context, consistent with the existing forward-P/E contract. |

## Revenue estimate (USD)

| | Current Qtr. (Jun 2026) | Next Qtr. (Sep 2026) | Current Year (2026) | Next Year (2027) |
|---|---|---|---|---|
| No. of analysts | 48 | 45 | 59 | 58 |
| Avg estimate | 60.26B | 63.23B | 253.29B | 304.11B |
| Low estimate | 59.03B | 61.23B | 237.14B | 282.2B |
| High estimate | 62.81B | 65.48B | 269.08B | 353.93B |
| Year-ago sales | 47.52B | 51.24B | 200.97B | 253.29B |
| Sales growth (YoY est.) | 26.82% | 23.39% | 26.04% | 20.06% |

## EPS estimate (normalized, USD)

| | Current Qtr. (Jun 2026) | Next Qtr. (Sep 2026) | Current Year (2026) | Next Year (2027) |
|---|---|---|---|---|
| Current estimate | 7.23 | 7.07 | 33.07 | 35.16 |
| 7 days ago | 7.20 | 7.06 | 32.92 | 34.93 |
| 30 days ago | 7.20 | 7.04 | 32.87 | 34.92 |
| 60 days ago | 7.20 | 7.04 | 32.91 | 34.75 |
| 90 days ago | 7.14 | 7.13 | 29.64 | 34.42 |

## EPS revisions (analyst count, last N days)

| | Current Qtr. (Jun 2026) | Next Qtr. (Sep 2026) | Current Year (2026) | Next Year (2027) |
|---|---|---|---|---|
| Up last 7 days | 1 | — | — | 1 |
| Up last 30 days | 22 | 10 | 3 | 3 |
| Down last 7 days | — | 1 | — | — |
| Down last 30 days | 13 | 22 | — | 3 |

**Caveat:** consensus estimates drift continuously as analysts revise (visible in the trend/revisions tables above). Like the forward-P/E contract, this is a moving snapshot — re-pull immediately before using it to judge an actual quarter's result, not from this stored file.

**Period mismatch note:** these estimates cover Q2 2026 / FY2026 / FY2027, all periods for which Meta has not yet reported actuals. This contract cannot be used to compute a variance against FY2025, which is already reported and closed.

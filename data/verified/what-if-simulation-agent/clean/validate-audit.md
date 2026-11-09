# Validate data shape: what-if-simulation-agent, `clean`

Written by `scripts/gigo/what-if-simulation-agent-validate-data-shape.py`. This audit says what was found; it does not say pass.

- Folder read: `data/raw/what-if-simulation-agent/sample/clean` (sample mode, invented requests)
- Requests in: 15; accepted: 15; rejected: 0
- Contract: the workflow's `Parse & Validate Input` node (defaults, then five rules, same messages). One stated addition: numeric fields must be finite.
- Open question for the maintainers, not a finding: in JavaScript a value that parses to NaN passes every comparison, so the node's own rules accept it; this gate rejects it so that no simulation runs on a non-number.

## Accepted

| Request | Fields filled by the workflow's defaults |
|---|---|
| `c01-strong-buy-on-the-thresholds` | none |
| `c02-growth-ignored-by-the-market` | none |
| `c03-bubble-risk` | none |
| `c04-hold-on-both-lower-thresholds` | none |
| `c05-both-bearish` | none |
| `c06-empty-body-all-defaults` | company, ticker, revenue_growth, sentiment_score, risk_appetite, time_horizon, current_price, pe_ratio, debt_equity, market_cap_billions |
| `c07-webhook-body-wrapper` | none |
| `c08-text-numbers-and-mixed-case` | none |
| `c09-unknown-horizon-and-blank-name` | none |
| `c10-rounding-ties-js-vs-python` | none |
| `c11-aggressive-on-its-limits` | none |
| `c12-zero-values-are-values` | none |
| `c13-another-tie-65-and-a-half` | none |
| `c14-low-growth-middling-sentiment` | none |
| `c15-medium-growth-high-sentiment` | none |

## What this audit did not look at

- Whether any request describes a real company: every one is invented.
- Anything past the input rules (the simulators run in step 5).

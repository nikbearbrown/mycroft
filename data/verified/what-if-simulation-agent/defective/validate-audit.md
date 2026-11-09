# Validate data shape: what-if-simulation-agent, `defective`

Written by `scripts/gigo/what-if-simulation-agent-validate-data-shape.py`. This audit says what was found; it does not say pass.

- Folder read: `data/raw/what-if-simulation-agent/sample/defective` (sample mode, invented requests)
- Requests in: 10; accepted: 0; rejected: 10
- Contract: the workflow's `Parse & Validate Input` node (defaults, then five rules, same messages). One stated addition: numeric fields must be finite.
- Open question for the maintainers, not a finding: in JavaScript a value that parses to NaN passes every comparison, so the node's own rules accept it; this gate rejects it so that no simulation runs on a non-number.

## Rejected

| Request | Reason |
|---|---|
| `d01-growth-above-20` | revenue_growth must be between -1.0 and 20.0 |
| `d02-sentiment-above-1` | sentiment_score must be 0–1 |
| `d03-unknown-risk-appetite` | risk_appetite must be low \| medium \| high |
| `d04-negative-pe` | pe_ratio must be positive |
| `d05-negative-debt-equity` | debt_equity must be positive |
| `d06-two-rules-broken-at-once` | revenue_growth must be between -1.0 and 20.0 ; pe_ratio must be positive |
| `d07-growth-is-not-a-number` | revenue_growth is not a finite number (the workflow's range checks let it through; this gate does not) |
| `d08-sentiment-is-empty-text` | sentiment_score is not a finite number (the workflow's range checks let it through; this gate does not) |
| `d09-payload-is-a-list` | a request must be a JSON object |
| `d10-truncated-json` | does not parse as JSON (JSONDecodeError: Expecting ',' delimiter: line 1 column 72 (char 71)) |

## What this audit did not look at

- Whether any request describes a real company: every one is invented.
- Anything past the input rules (the simulators run in step 5).

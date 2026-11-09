# Validate data shape: scenariostresstestingagent, `defective`

Written by `scripts/gigo/scenariostresstestingagent-validate-data-shape.py`. This audit says what was found; it does not say pass.

- Folder read: `data/raw/scenariostresstestingagent/sample/defective` (sample mode, invented requests)
- Requests in: 10; accepted: 0; rejected: 10
- Contract: the workflow's `Validate Portfolio` node, with its own two messages.
- **One stated addition**, marked in every reason that comes from it: holdings must be a non-empty array of objects; every weight must be present, a finite number, and not negative; the total must be positive; scenario_type, if present, must be one of the five templates; with no custom_scenario and no scenario_type the workflow's default (tech_crash) applies; custom_scenario, if present, must be a string; horizon_days, if present, must be a finite number.
- Open question for the maintainers, not a finding: several requests this gate rejects are ones the workflow itself would run (a negative weight, an unknown scenario_type, an empty holdings array); the reasons say what the workflow would do.

## Rejected

| Request | Reason |
|---|---|
| `d01-portfolio-missing` | Portfolio must have holdings array (the node's own rule) |
| `d02-holdings-missing` | Portfolio must have holdings array (the node's own rule) |
| `d03-holding-without-ticker` | Each holding must have a ticker (the node's own rule) |
| `d04-holdings-is-an-object` | portfolio.holdings is not iterable (the node's own rule) ; holdings is a dict, not an array (gate addition) |
| `d05-weight-is-a-string` | holding 0 (NVDA) has a weight that is not a number ('0.5'): JavaScript would join it as text (gate addition) |
| `d06-all-weights-zero` | weights total 0.0: rescaling by a zero total gives NaN weights (gate addition) |
| `d07-negative-weight` | holding 1 (AMD) has a negative weight (-0.3): the engine would treat it as a short position without saying so (gate addition) |
| `d08-unknown-scenario-type` | scenario_type 'meltdown' is not one of ['ai_regulation', 'black_swan', 'chip_shortage', 'rate_hike', 'tech_crash']: the workflow would silently run tech_crash (gate addition) |
| `d09-empty-holdings` | holdings is empty: nothing to stress-test (gate addition) |
| `d10-weight-missing` | holding 1 (AMD) has no weight: the node counts it as 0 and the engine then fails on it (gate addition) |

## What this audit did not look at

- Whether any portfolio describes a real holding: every one is invented.
- Anything past the input rules (the stress test runs in step 5).
- The five template scenarios' numbers: they are the workflow's own, copied, not judged.

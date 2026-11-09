# Validate data shape: scenariostresstestingagent, `clean`

Written by `scripts/gigo/scenariostresstestingagent-validate-data-shape.py`. This audit says what was found; it does not say pass.

- Folder read: `data/raw/scenariostresstestingagent/sample/clean` (sample mode, invented requests)
- Requests in: 12; accepted: 12; rejected: 0
- Contract: the workflow's `Validate Portfolio` node, with its own two messages.
- **One stated addition**, marked in every reason that comes from it: holdings must be a non-empty array of objects; every weight must be present, a finite number, and not negative; the total must be positive; scenario_type, if present, must be one of the five templates; with no custom_scenario and no scenario_type the workflow's default (tech_crash) applies; custom_scenario, if present, must be a string; horizon_days, if present, must be a finite number.
- Open question for the maintainers, not a finding: several requests this gate rejects are ones the workflow itself would run (a negative weight, an unknown scenario_type, an empty holdings array); the reasons say what the workflow would do.

## Accepted

| Request | Scenario route |
|---|---|
| `c01-tech-crash-semiconductor-heavy` | template `tech_crash` |
| `c02-rate-hike-mixed-book` | template `rate_hike` |
| `c03-ai-regulation-outside-the-map` | template `ai_regulation` |
| `c04-chip-shortage-mostly-unmapped` | template `chip_shortage` |
| `c05-black-swan-two-names` | template `black_swan` |
| `c06-weights-sum-to-six-tenths` | template `tech_crash` |
| `c07-weights-within-tolerance` | template `chip_shortage` |
| `c08-weights-sum-to-one-point-two` | template `tech_crash` |
| `c09-scenario-type-absent` | template `tech_crash (default)` |
| `c10-custom-scenario-needs-the-llm` | custom scenario: needs the Groq call, recorded as a handoff |
| `c11-exactly-ten-percent` | template `rate_hike` |
| `c12-growth-stack-rate-hike` | template `rate_hike` |

## What this audit did not look at

- Whether any portfolio describes a real holding: every one is invented.
- Anything past the input rules (the stress test runs in step 5).
- The five template scenarios' numbers: they are the workflow's own, copied, not judged.

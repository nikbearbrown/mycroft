# Transform and quality check: scenariostresstestingagent, `clean`

Written by `scripts/gigo/scenariostresstestingagent-transform-quality-check.py`. This note says what was found; it does not say pass.

- 12 request(s) came in from step 3 and 0 were rejected there; 12 have a step-5 result (1 stopped at a handoff).
- 11 result(s) reconciled on every check and 1 stopped at a handoff with nothing to reconcile; 0 failure(s); 0 duplicate group(s); 11 advisory flag(s).
- Every figure was re-derived from the workflow's own template shocks (sector map, ai_stocks, growth_stocks) with exact decimals; the step-5 engine was not called.
- Flags are for a human to read. They are not failures, and the checks do not judge whether the template shocks or risk thresholds are sound.

## Verified records

- `c01-tech-crash-semiconductor-heavy`
- `c02-rate-hike-mixed-book`
- `c03-ai-regulation-outside-the-map`
- `c04-chip-shortage-mostly-unmapped`
- `c05-black-swan-two-names`
- `c06-weights-sum-to-six-tenths`
- `c07-weights-within-tolerance`
- `c08-weights-sum-to-one-point-two`
- `c09-scenario-type-absent`
- `c11-exactly-ten-percent`
- `c12-growth-stack-rate-hike`

## Stopped at a handoff (no result to reconcile)

- `c10-custom-scenario-needs-the-llm`

## Failures

- none

## Duplicates

- none

## Rejected before this step or at it

- none

## Flags for a human

- `c02-rate-hike-mixed-book` **default-sector**: 50% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c03-ai-regulation-outside-the-map` **default-sector**: 100% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c04-chip-shortage-mostly-unmapped` **default-sector**: 90% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c05-black-swan-two-names` **default-sector**: 100% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c06-weights-sum-to-six-tenths` **rescaled**: the request's weights add to 0.6; the workflow rescaled them to 1.0
- `c07-weights-within-tolerance` **majority-holding**: OMNI is 50.5% of the book after rescaling, more than half
- `c07-weights-within-tolerance` **default-sector**: 50% of the book is in tickers the workflow's sector map does not list, so it gets the default tech_sector shock
- `c08-weights-sum-to-one-point-two` **rescaled**: the request's weights add to 1.2; the workflow rescaled them to 1.0
- `c09-scenario-type-absent` **scenario-defaulted**: no scenario_type in the request; the workflow runs the default, tech_crash
- `c10-custom-scenario-needs-the-llm` **handoff**: Groq chat call needed for a custom scenario: not approved, not made
- `c11-exactly-ten-percent` **on-threshold**: drawdown -10.0% sits within 0.05 points of the 10% line; the rule is 'above', so the level is LOW

## Checks run on every result

`weights-sum`, `position-shock`, `position-initial`, `position-loss`, `position-final`, `total-loss`, `final-value`, `drawdown`, `risk-level`, `positions-order`, `top-losers`, `scenario-name`, `duplicate-id`, `duplicate-content`

# Transform and quality check: scenariostresstestingagent, `defective`

Written by `scripts/gigo/scenariostresstestingagent-transform-quality-check.py`. This note says what was found; it does not say pass.

- 0 request(s) came in from step 3 and 10 were rejected there; 0 have a step-5 result (0 stopped at a handoff).
- 0 result(s) reconciled on every check and 0 stopped at a handoff with nothing to reconcile; 0 failure(s); 0 duplicate group(s); 0 advisory flag(s).
- Every figure was re-derived from the workflow's own template shocks (sector map, ai_stocks, growth_stocks) with exact decimals; the step-5 engine was not called.
- Flags are for a human to read. They are not failures, and the checks do not judge whether the template shocks or risk thresholds are sound.

## Verified records

- none

## Stopped at a handoff (no result to reconcile)

- none

## Failures

- none

## Duplicates

- none

## Rejected before this step or at it

- `d01-portfolio-missing` at step 3 (validate data shape): Portfolio must have holdings array (the node's own rule)
- `d02-holdings-missing` at step 3 (validate data shape): Portfolio must have holdings array (the node's own rule)
- `d03-holding-without-ticker` at step 3 (validate data shape): Each holding must have a ticker (the node's own rule)
- `d04-holdings-is-an-object` at step 3 (validate data shape): portfolio.holdings is not iterable (the node's own rule); holdings is a dict, not an array (gate addition)
- `d05-weight-is-a-string` at step 3 (validate data shape): holding 0 (NVDA) has a weight that is not a number ('0.5'): JavaScript would join it as text (gate addition)
- `d06-all-weights-zero` at step 3 (validate data shape): weights total 0.0: rescaling by a zero total gives NaN weights (gate addition)
- `d07-negative-weight` at step 3 (validate data shape): holding 1 (AMD) has a negative weight (-0.3): the engine would treat it as a short position without saying so (gate addition)
- `d08-unknown-scenario-type` at step 3 (validate data shape): scenario_type 'meltdown' is not one of ['ai_regulation', 'black_swan', 'chip_shortage', 'rate_hike', 'tech_crash']: the workflow would silently run tech_crash (gate addition)
- `d09-empty-holdings` at step 3 (validate data shape): holdings is empty: nothing to stress-test (gate addition)
- `d10-weight-missing` at step 3 (validate data shape): holding 1 (AMD) has no weight: the node counts it as 0 and the engine then fails on it (gate addition)

## Flags for a human

- none

## Checks run on every result

`weights-sum`, `position-shock`, `position-initial`, `position-loss`, `position-final`, `total-loss`, `final-value`, `drawdown`, `risk-level`, `positions-order`, `top-losers`, `scenario-name`, `duplicate-id`, `duplicate-content`

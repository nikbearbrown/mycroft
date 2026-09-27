# Multi-Month Performance Investigation

## Decision Boundary

- Classification: `HISTORICAL_COMPARISON_NOT_FORECAST`
- This report compares verified historical calculations only.
- Causation, forecasts, recommendations, and distribution approval are not supplied.
- Human gate: `OPEN`

## Scope

- Run ID: `week35-trend`
- Entity: Northstar Software Sample
- Periods compared: 3
- Materiality: 10000.00 (`DEMO_UNAPPROVED`)
- Plan: `projects/Mycroft-Finance-Investigator/config/sample-trend.json` (SHA-256 `cf4c740e591bd9d1a77e418fea1c541f11fe1bb7d756aaac99d0055891593c09`)

## Historical EBITDA

| Period | Budget | Actual | Variance | Change from prior | Movement | Source run |
|---|---:|---:|---:|---:|---|---|
| 2026-01 | 344000.00 | 261000.00 | -83000.00 | — | `FIRST_PERIOD` | `sample-2026-01` |
| 2026-02 | 350000.00 | 230000.00 | -120000.00 | -31000.00 | `DETERIORATED` | `sample-2026-02` |
| 2026-03 | 360000.00 | 265000.00 | -95000.00 | 35000.00 | `IMPROVED` | `sample-2026-03` |

## Category Pattern

A recurring material adverse category meets the unapproved demo threshold in at least two included periods.

| Category | Impacts by period | Adverse periods | Favorable periods | Recurring adverse |
|---|---|---:|---:|---|
| revenue | 2026-01: -50000.00; 2026-02: -90000.00; 2026-03: -60000.00 | 3 | 0 | `YES` |
| cogs | 2026-01: -30000.00; 2026-02: -35000.00; 2026-03: -35000.00 | 3 | 0 | `YES` |
| payroll | 2026-01: 8000.00; 2026-02: 20000.00; 2026-03: 10000.00 | 0 | 2 | `NO` |
| opex | 2026-01: -11000.00; 2026-02: -15000.00; 2026-03: -10000.00 | 3 | 0 | `YES` |

## Verified Pattern

- Recurring material adverse categories: `revenue`, `cogs`, `opex`
- This is a mathematical pattern, not a causal explanation.

## Source Runs

- 2026-01: `logs/mycroft-finance-investigator-sample-2026-01.json` (SHA-256 `0a274dd901d55f87558a202b780147f0ff758bf875b232ca212f956887d3d1d5`)
- 2026-02: `logs/mycroft-finance-investigator-sample-2026-02.json` (SHA-256 `41cfa60e7f28f47b3ef2484213155bdd90fa236f1789d6b306899d870ced4869`)
- 2026-03: `logs/mycroft-finance-investigator-sample-2026-03.json` (SHA-256 `8f6546e63c4d91b3d89ddd398f54e8b7e305b831a5d44595b3efdd748677253c`)

## Current Explanation — Owner Required

_Intentionally blank. Recurrence does not establish why a variance occurred._

## Human Review

- [ ] Approve or replace the demo materiality threshold
- [ ] Assess causal explanations using additional business evidence
- [ ] Determine whether the history is adequate for a decision
- [ ] Approve or block distribution

- Reviewer:
- Review date:
- Decision:

# Finance Investigator Scenario Decision Pack

- Run: `week33`
- Baseline investigation: `sample-2026-02`
- Baseline actual EBITDA: 230000.00
- Classification: `SIMULATION_NOT_FORECAST`
- Recommendation: `NONE`
- Decision: `HUMAN_REQUIRED`
- Adequacy: `PENDING_HUMAN_REVIEW`

Outputs are arithmetic sensitivities to synthetic exercise assumptions; they are not forecasts, probabilities, recommendations, or approvals.

## Comparison

| Scenario | EBITDA | Difference from baseline |
|---|---:|---:|
| Revenue recovery exercise | 275500.00 | 45500.00 |
| COGS reduction exercise | 250000.00 | 20000.00 |
| Balanced operating exercise | 252300.00 | 22300.00 |

## Explicit Assumptions

### Revenue recovery exercise

Show the arithmetic EBITDA sensitivity if actual revenue were 5% higher than the verified sample baseline.

| Category | Method | Input | Adjustment | EBITDA impact | Source |
|---|---|---:|---:|---:|---|
| revenue | `PERCENT_OF_ACTUAL` | 5.00 | 45500.00 | 45500.00 | Unapproved sample exercise |

### COGS reduction exercise

Show the arithmetic EBITDA sensitivity if sample COGS were 20000 lower than the verified actual baseline.

| Category | Method | Input | Adjustment | EBITDA impact | Source |
|---|---|---:|---:|---:|---|
| cogs | `AMOUNT` | -20000.00 | -20000.00 | 20000.00 | Unapproved sample exercise |

### Balanced operating exercise

Show a combined sensitivity across revenue, payroll, and operating expenses without selecting it as a preferred case.

| Category | Method | Input | Adjustment | EBITDA impact | Source |
|---|---|---:|---:|---:|---|
| revenue | `PERCENT_OF_ACTUAL` | 3.00 | 27300.00 | 27300.00 | Unapproved sample exercise |
| payroll | `AMOUNT` | 10000.00 | 10000.00 | -10000.00 | Unapproved sample exercise |
| opex | `AMOUNT` | -5000.00 | -5000.00 | 5000.00 | Unapproved sample exercise |

## Human Decision Required

A named finance owner must approve or replace each assumption, judge whether the scenarios are useful and sufficient, and make any resulting business decision. This pack makes no recommendation.

# Monthly Performance Investigation

## Review Status

- Run ID: `sample-2026-01`
- Decision: `PENDING HUMAN REVIEW`
- Entity: Northstar Software Sample
- Period: 2026-01
- Materiality: 10000.00 (`DEMO_UNAPPROVED`)

## Question

Why did actual EBITDA differ from budget?

## Verified Mathematical Findings

| Finding | Evidence references |
|---|---:|
| Actual EBITDA was 261000.00 versus budget 344000.00, a variance of -83000.00. | 4 |
| Revenue contributed EBITDA performance impact -50000.00 from actual 920000.00 versus budget 970000.00. | 6 |
| Cogs contributed EBITDA performance impact -30000.00 from actual 205000.00 versus budget 175000.00. | 3 |
| Payroll contributed EBITDA performance impact 8000.00 from actual 302000.00 versus budget 310000.00. | 3 |
| Opex contributed EBITDA performance impact -11000.00 from actual 152000.00 versus budget 141000.00. | 9 |
| Subscription Revenue had actual 735000.00 versus budget 780000.00; EBITDA performance impact -45000.00. | 5 |
| Cloud Hosting had actual 205000.00 versus budget 175000.00; EBITDA performance impact -30000.00. | 5 |

## Investigation Prompts

- 4 revenue driver records were attached for owner review; no causal conclusion was generated.

## Current Explanation — Owner Required

_Intentionally blank. The investigator does not infer business causation from numerical movement._

## Evidence Index

- `account_mapping.csv:account=4000`
- `account_mapping.csv:account=4010`
- `account_mapping.csv:account=5000`
- `account_mapping.csv:account=6000`
- `account_mapping.csv:account=6100`
- `account_mapping.csv:account=6200`
- `account_mapping.csv:account=6300`
- `actuals.csv:account=4000`
- `actuals.csv:account=4010`
- `actuals.csv:account=5000`
- `actuals.csv:account=6000`
- `actuals.csv:account=6100`
- `actuals.csv:account=6200`
- `actuals.csv:account=6300`
- `budget.csv:account=4000`
- `budget.csv:account=4010`
- `budget.csv:account=5000`
- `budget.csv:account=6000`
- `budget.csv:account=6100`
- `budget.csv:account=6200`
- `budget.csv:account=6300`
- `category:cogs`
- `category:opex`
- `category:payroll`
- `category:revenue`
- `customers.csv:customer_id=CUST-ENT-A`
- `customers.csv:customer_id=CUST-ENT-B`
- `customers.csv:customer_id=CUST-MID-C`
- `customers.csv:customer_id=CUST-SMB-COHORT`
- `ledger.csv:transaction_id=JAN-TXN-001`
- `ledger.csv:transaction_id=JAN-TXN-002`
- `ledger.csv:transaction_id=JAN-TXN-005`
- `ledger.csv:transaction_id=JAN-TXN-006`

## Agent Trace

| Step | Tool | Reason |
|---:|---|---|
| 1 | `scan_material_variances` | Begin with a reconciled EBITDA bridge and materiality scan |
| 2 | `analyze_category` | revenue has performance impact -50000.00, above the configured threshold |
| 3 | `analyze_category` | cogs has performance impact -30000.00, above the configured threshold |
| 4 | `analyze_category` | opex has performance impact -11000.00, above the configured threshold |
| 5 | `inspect_driver_records` | revenue has a verified operational driver dataset |

## Human Decision

- Reviewer:
- Review date:
- Materiality decision:
- Causal explanation and supporting evidence:
- Distribution decision: `APPROVE` / `REQUEST CHANGES` / `BLOCK`

### Did Not Test

- Human adequacy of materiality and business explanations.

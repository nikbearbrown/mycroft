# Monthly Performance Investigation

## Review Status

- Run ID: `sample-2026-02`
- Decision: `PENDING HUMAN REVIEW`
- Entity: Northstar Software Sample
- Period: 2026-02
- Materiality: 10000.00 (`DEMO_ONLY_PENDING_HUMAN_APPROVAL`)

## Question

Why did actual EBITDA differ from budget for the month?

## Verified Mathematical Findings

| Finding | Evidence references |
|---|---:|
| Actual EBITDA was 230000.00 versus budget 350000.00, a variance of -120000.00. | 4 |
| Revenue contributed EBITDA performance impact -90000.00 from actual 910000.00 versus budget 1000000.00. | 6 |
| Cogs contributed EBITDA performance impact -35000.00 from actual 215000.00 versus budget 180000.00. | 3 |
| Payroll contributed EBITDA performance impact 20000.00 from actual 300000.00 versus budget 320000.00. | 3 |
| Opex contributed EBITDA performance impact -15000.00 from actual 165000.00 versus budget 150000.00. | 9 |
| Subscription Revenue had actual 720000.00 versus budget 800000.00; EBITDA performance impact -80000.00. | 5 |
| Services Revenue had actual 190000.00 versus budget 200000.00; EBITDA performance impact -10000.00. | 5 |
| Cloud Hosting had actual 215000.00 versus budget 180000.00; EBITDA performance impact -35000.00. | 5 |
| Salaries and Benefits had actual 300000.00 versus budget 320000.00; EBITDA performance impact 20000.00. | 5 |
| Marketing Programs had actual 90000.00 versus budget 80000.00; EBITDA performance impact -10000.00. | 5 |

## Investigation Prompts

- 4 revenue driver records were attached for owner review; no causal conclusion was generated.
- 2 payroll driver records were attached for owner review; no causal conclusion was generated.

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
- `headcount.csv:department=Engineering`
- `headcount.csv:department=Sales`
- `ledger.csv:transaction_id=TXN-001`
- `ledger.csv:transaction_id=TXN-002`
- `ledger.csv:transaction_id=TXN-003`
- `ledger.csv:transaction_id=TXN-004`
- `ledger.csv:transaction_id=TXN-005`
- `ledger.csv:transaction_id=TXN-006`
- `ledger.csv:transaction_id=TXN-007`
- `ledger.csv:transaction_id=TXN-008`
- `ledger.csv:transaction_id=TXN-009`
- `ledger.csv:transaction_id=TXN-010`

## Agent Trace

| Step | Tool | Reason |
|---:|---|---|
| 1 | `scan_material_variances` | Begin with a reconciled EBITDA bridge and materiality scan |
| 2 | `analyze_category` | revenue has performance impact -90000.00, above the configured threshold |
| 3 | `analyze_category` | cogs has performance impact -35000.00, above the configured threshold |
| 4 | `analyze_category` | payroll has performance impact 20000.00, above the configured threshold |
| 5 | `analyze_category` | opex has performance impact -15000.00, above the configured threshold |
| 6 | `inspect_driver_records` | revenue has a verified operational driver dataset |
| 7 | `inspect_driver_records` | payroll has a verified operational driver dataset |

## Human Decision

- Reviewer:
- Review date:
- Materiality decision:
- Causal explanation and supporting evidence:
- Distribution decision: `APPROVE` / `REQUEST CHANGES` / `BLOCK`

### Did Not Test

- Human adequacy of materiality and business explanations.

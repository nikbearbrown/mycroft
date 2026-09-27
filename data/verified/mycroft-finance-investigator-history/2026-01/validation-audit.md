# Finance Pack Validation Audit

This audit reports deterministic observations. Human adequacy review is still required.

## Row Counts

| Dataset | Rows | SHA-256 |
|---|---:|---|
| `account_mapping.csv` | 7 | `c45ba1275b8daa38b6827e7257170a9ea34b255033be5128c4c6e74e51d1a839` |
| `actuals.csv` | 8 | `007f5786115fbf94af981f8604fc2a6dffcfd26da6c2a473bfafa8104eaae6fc` |
| `budget.csv` | 8 | `f2a6de1ee3fa367c1b7d16657184308a4a8ece2af50199246e83526145a15304` |
| `customers.csv` | 4 | `bd94e40093870334aa276bd05504d094a8d9766cce06d77528702cb995623ba9` |
| `headcount.csv` | 2 | `05497113cdb1d7346a5adfbc1eeabbcf07c94e4c940772f9161f2de415099b9e` |
| `ledger.csv` | 14 | `55ecf3a9064375b53b00d5d21888a318adb3a74b4e25635ea0b76bb28a57fc1d` |

## Reconciliation Observations

| Check | Observed |
|---|---|
| Account mapping coverage | All budget, actual, and ledger accounts mapped |
| Scope | One period (2026-01) and one entity (Northstar Software Sample) |
| Actuals-to-ledger control total | Reconciled at 1579000.00 |
| Customer revenue drivers | Budget 970000.00; actual 920000.00; reconciled |
| Headcount cost drivers | Budget 310000.00; actual 302000.00; reconciled |

## Adequacy

`PENDING_HUMAN_REVIEW` — the sample is structurally conformant; this audit does not approve materiality, causation, or distribution.

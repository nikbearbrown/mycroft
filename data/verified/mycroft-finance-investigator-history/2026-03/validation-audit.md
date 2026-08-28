# Finance Pack Validation Audit

This audit reports deterministic observations. Human adequacy review is still required.

## Row Counts

| Dataset | Rows | SHA-256 |
|---|---:|---|
| `account_mapping.csv` | 7 | `c45ba1275b8daa38b6827e7257170a9ea34b255033be5128c4c6e74e51d1a839` |
| `actuals.csv` | 8 | `31d6adc59f2532ba7e0d285ea522e2017444ffb2eac0be0837fd9d59027fb085` |
| `budget.csv` | 8 | `41e8484e0b1c1aab87a41138e9ee62dd858584550cb6849afb81688941ef9bfd` |
| `customers.csv` | 4 | `029cef3ea65cf380146099c5b4a6ea0ea181d55b4053c5b5b31c140a349c1676` |
| `headcount.csv` | 2 | `016e0c5cff768221d555f149e6df1e8bdb7fee6316466a293d64f64446ed744e` |
| `ledger.csv` | 14 | `72987794e2b79b35b5c2e2499c7e598fbdbcb39bd4cc9f364470b795edc02c71` |

## Reconciliation Observations

| Check | Observed |
|---|---|
| Account mapping coverage | All budget, actual, and ledger accounts mapped |
| Scope | One period (2026-03) and one entity (Northstar Software Sample) |
| Actuals-to-ledger control total | Reconciled at 1675000.00 |
| Customer revenue drivers | Budget 1030000.00; actual 970000.00; reconciled |
| Headcount cost drivers | Budget 330000.00; actual 320000.00; reconciled |

## Adequacy

`PENDING_HUMAN_REVIEW` — the sample is structurally conformant; this audit does not approve materiality, causation, or distribution.

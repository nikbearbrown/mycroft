# Finance Pack Validation Audit

This audit reports deterministic observations. Human adequacy review is still required.

## Row Counts

| Dataset | Rows | SHA-256 |
|---|---:|---|
| `account_mapping.csv` | 7 | `c45ba1275b8daa38b6827e7257170a9ea34b255033be5128c4c6e74e51d1a839` |
| `actuals.csv` | 8 | `389b724554635514fddb6bfbb0356744780dd21465f9795f7158626bab994015` |
| `budget.csv` | 8 | `de05edd74e10eab58406d8378cc603699e4f1b34d38fdfa6bb0c7d4bd719dc79` |
| `customers.csv` | 4 | `4deba1e908e005d30fdd69fe564b71891f1a545d5010fa5a9e176eb9bc1b8b03` |
| `headcount.csv` | 2 | `8938672e39fc1d0135b2ee961ce81036d0f141daab823ffed0bcc81c6550fb24` |
| `ledger.csv` | 14 | `3dddbc583608426447ca799360bf58bb00be8b86962ef2677107feebc9a3a05d` |

## Reconciliation Observations

| Check | Observed |
|---|---|
| Account mapping coverage | All budget, actual, and ledger accounts mapped |
| Scope | One period (2026-02) and one entity (Northstar Software Sample) |
| Actuals-to-ledger control total | Reconciled at 1590000.00 |
| Customer revenue drivers | Budget 1000000.00; actual 910000.00; reconciled |
| Headcount cost drivers | Budget 320000.00; actual 300000.00; reconciled |

## Adequacy

`PENDING_HUMAN_REVIEW` — the sample is structurally conformant; this audit does not approve materiality, causation, or distribution.

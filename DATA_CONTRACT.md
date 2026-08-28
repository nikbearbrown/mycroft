# Data Contract

## Source Data

Put source exports, original datasets, and approved reference records in
`data/`.

## Generated Data

Generated audits and reports should sit beside the data they inspect and use
`-audit.md` when appropriate.

## Vendor Intelligence Data Layer

| Dataset | Raw Source | Raw Location | Verified Location | Gate | Owner |
|---|---|---|---|---|---|
| `ai_company_signals` | PostgreSQL (4 ingest pipelines: EDGAR, GitHub, ArXiv, News RSS/scraping) | Production DB (external) | `data/verified/ai_company_signals/` + schema in `data/verified/ai_company_signals-schema.yaml` (v0.2.0) | **Phase 2: Signal Validation — PARTIALLY CLEARED.** Entity verification cleared 2026-08-22 by Muskan Khandelwal (batch-level: entity audit + 782-row purge, evidence in `logs/RUN_LOG.md#2026-08-22`). Still open: per-signal human review of source URL + score confidence. | Muskan Khandelwal |
| `company-competitive-graph` | Neo4j (50 Company nodes + 8 Investor nodes; COMPETES_WITH, BACKED_BY edges) | Production DB (external) | `data/verified/company-graph.json` (quarterly snapshot) | Implicit: Neo4j query accuracy spot-checked before brief generation | Graph ingest owner (TBD) |

## Mycroft Finance Investigator Data Layer

| Dataset | Raw Source | Raw Location | Verified Location | Gate | Owner |
|---|---|---|---|---|---|
| `monthly-performance-sample` | Locally created synthetic budget, actual, ledger, customer, headcount, mapping, and provenance records | `data/raw/mycroft-finance-investigator/` | `data/verified/mycroft-finance-investigator/` | Provenance, schema, single-period/entity scope, account mapping, actuals-to-ledger reconciliation, customer-to-revenue reconciliation, headcount-to-payroll reconciliation, human materiality, and named human release review | Finance reviewer (TBD) |
| `monthly-performance-history-sample` | Locally created synthetic January and March packs combined with the existing February sample | `data/raw/mycroft-finance-investigator-history/` | `data/verified/mycroft-finance-investigator-history/` | Every month passes the single-period controls; comparison additionally requires ordered unique periods, one entity, exact run-log/source hashes, recomputed EBITDA agreement, human materiality, interpretation, and release review | Finance reviewer (TBD) |

The included finance pack is synthetic and may support software verification
only. Validation can establish structural conformance and control-total
reconciliation. It cannot approve the demo materiality amount, a causal
explanation, or distribution.

Historical comparison may establish exact numerical movement and recurrence
under an explicit threshold. It cannot establish causation, predict another
period, recommend action, or clear a human gate.

## Rules

- Check local data before external lookup.
- Never invent counts, rates, coverage, or confidence.
- Mark missing data as missing.
- Do not store secrets in tracked data files.
- Vendor intelligence signals must be validated before entering `data/verified/` (Phase 2 gate).
- A company name is not a unique identifier. Every name-searched signal must pass
  entity verification (`check_entity`) before it can be cited as evidence — 782 rows
  about namesake organisations were purged on 2026-08-07 after one of them moved a
  vendor's score by 25 points. See the `entity_verification` section of
  `data/verified/ai_company_signals-schema.yaml`.
- An audit that removes failing rows does not certify the rows that remain. Say which
  of the two a gate decision rests on.
- Finance-investigator outputs must retain their source hashes, validation audit, calculation lineage, tool trace, open human gate, and blank owner-required explanation until review. Human decisions must be run-bound, evidence-backed, named, and append-only.

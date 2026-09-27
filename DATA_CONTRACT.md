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

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
| `ai_company_signals` | PostgreSQL (4 ingest pipelines: EDGAR, GitHub, ArXiv, News RSS/scraping) | Production DB (external) | `data/verified/ai_company_signals/` + schema in `data/verified/ai_company_signals-schema.yaml` | **Phase 2: Signal Validation** — human must validate source URL + score confidence before signal enters verified layer. Evidence: `signals-validation-audit.md` + signed-off gate decision in `logs/RUN_LOG.md` | Data steward (TBD) |
| `company-competitive-graph` | Neo4j (50 Company nodes + 8 Investor nodes; COMPETES_WITH, BACKED_BY edges) | Production DB (external) | `data/verified/company-graph.json` (quarterly snapshot) | Implicit: Neo4j query accuracy spot-checked before brief generation | Graph ingest owner (TBD) |

## SEC Filings Financial Metrics Data Layer

| Dataset | Raw Source | Raw Location | Verified Location | Gate | Owner |
|---|---|---|---|---|---|
| `sec-financial-metrics` | SEC EDGAR XBRL `companyfacts` (read-only public API, rate-limited) | `data/raw/sec-filings-financial-metrics/` (cached responses, each wrapped with a `_provenance` fetch timestamp + source URL) | `data/verified/sec-filings-financial-metrics/<TICKER>_financial_metrics.json` | **Validation** — accounting identity (Assets = Liabilities + Equity) and margin bounds (≤ 100%) must pass; missing/impossible values are flagged (PASS/FAIL/UNKNOWN), never guessed. Every value retains its `us-gaap` tag + accession. Evidence: `validation` block in the output JSON | Fellow (Asavari Shejwal) |

## Rules

- Check local data before external lookup.
- Never invent counts, rates, coverage, or confidence.
- Mark missing data as missing.
- Do not store secrets in tracked data files.
- Vendor intelligence signals must be validated before entering `data/verified/` (Phase 2 gate).
- SEC financial metrics must retain per-value provenance (XBRL tag + accession) and pass rule-based validation before use.

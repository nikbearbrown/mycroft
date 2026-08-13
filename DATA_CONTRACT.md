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

## Earnings Call Sentiment Data Layer

| Dataset | Raw Source | Raw Location | Verified Location | Gate | Owner |
|---|---|---|---|---|---|
| `earnings-call-transcripts` | Human-approved TXT or text-based PDF transcript | `data/raw/earnings-call-sentiment-analyzer/` | `data/verified/earnings-call-sentiment-analyzer/` | Source provenance, extractable text, constrained path, parser attribution, model/version traceability, chunk-to-aggregate evidence, and named human adequacy review | Research analyst (TBD) |

The imported Northstar transcript is explicitly a user-created sample, not a real issuer record. FinBERT probabilities and derived net tone are model judgments. They become verified records only after the recipe's parser, model, evidence, and human review gates are logged.

## Rules

- Check local data before external lookup.
- Never invent counts, rates, coverage, or confidence.
- Mark missing data as missing.
- Do not store secrets in tracked data files.
- Vendor intelligence signals must be validated before entering `data/verified/` (Phase 2 gate).
- Earnings-call aggregates must retain their transcript chunks, speaker/section attribution, model identifier, and human review record.

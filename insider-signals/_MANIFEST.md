# _MANIFEST — Insider Signal Intelligence module

Navigation map for the `insider-signals/` module. Links to canonical sources and does
not repeat their content. Governance order:
`SNICKERDOODLE.md` (repo constitution) > repo `DOMAIN.md` > this manifest.

## Tier 1 — canonical (authoritative)

| File | Role |
|------|------|
| `recipes/insider-signal-agent.md` | Canonical recipe spec (a conflict with a script is a logged defect — P6) |
| `DATA_CONTRACT.md` | Data locations, SEC fields used, validation rules |
| `logs/RUN_LOG.md` | Append-only execution history (P7) |
| `status.md` | Current lifecycle snapshot |

## Tier 2 — task-specific (executable; planned, not yet written)

| File | Layer |
|------|-------|
| `ingest.py` | INGEST — SEC Insider Transactions Data Sets → `data/raw/form345/` |
| `parse.py` | PARSE — join tables, classify transaction codes → `data/raw/parsed/` |
| `conformance.py` | GIGO — G2 checks, audit, raw → `data/verified/insider_buys.csv` |
| `enrich.py` | ENRICH — prices, SPY-adjusted returns → `data/verified/enriched_buys.csv` |
| `signals.py` | SIGNALS — clusters, STRONG/WATCH/SKIP → `data/verified/clusters.json` |
| `langgraph_pipeline.py` | AGENT — gated LangGraph pipeline with human attestation → `logs/`, `reports/` |
| `server.py` | TOOL — MCP server (week 9) |
| `tests/` | stdlib `unittest`, no network, fixtures in `tests/fixtures/` |
| `requirements.txt` | Python dependencies |

## Tier 3 — generated / regenerable

| Path | Note |
|------|------|
| `data/raw/form345/*.zip`, `data/raw/form345/*/`, `data/raw/parsed/`, `data/raw/prices/` | Re-downloadable or rebuildable; gitignored. Provenance is in `manifest.json`. |
| `logs/run_*.json`, `reports/*_<run_id>.md` | Per-run outputs. Keep them: they are evidence for gates. |
| `__pycache__/`, `*.pyc` | Build artifacts |

> Source files, data, recipes, logs and hand-made work are permanent. Archive them, never delete them.

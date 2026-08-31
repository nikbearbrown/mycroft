# Databases

SQLite schemas, ticker registry, and HITL approvals. Databases are created under `src/ecis/data/db/` (`DB_DIR` in `.env`).

| File | Role |
|---|---|
| [init_db.py](init_db.py) | Schema DDL and migrations |
| [ticker_registry.py](ticker_registry.py) | Company inventory |
| [approvals.py](approvals.py) | HITL queue |

Embeddings: [`../embedding/README.md`](../embedding/README.md). Transcript fetch: [`../../../data/README.md`](../../../data/README.md). Scorecard: [`../../../docs/scoring-and-feedback.md`](../../../docs/scoring-and-feedback.md).

## Initialise

```bash
python -m ecis.main --init-db
```

Creates the four files and inserts default reader weights and escalation thresholds:

```
src/ecis/data/db/
  signals.db
  outcomes.db
  agents.db
  checkpoints.db
```

| File | Role | Written by |
|---|---|---|
| `signals.db` | Append-only guidance log | `--extract` / `--batch` |
| `outcomes.db` | Horizon prices and correctness | `--resolve-outcomes` |
| `agents.db` | Registry, weights, thresholds, classifications, HITL, ingest metadata | ingest, extract, watchdog, learn, vindicate |
| `checkpoints.db` | Pipeline crash recovery | LangGraph |

## `agents.db` tables

| Table | Role |
|---|---|
| `tickers` | Registry: source, transcript count, extraction / outcome status |
| `file_metadata` | Cached raw files; `period_of_report` when EDGAR provides it |
| `reader_weights` | Triangulator weights (including per-LLM aliases) |
| `escalation_thresholds` | Fast-pass routing knobs |
| `chunk_classifications` | Category A/B/C/D per chunk |
| `chunk_rejections` | Chunks dropped by the validator |
| `vindication_records` | Which reader won after the fact |
| `pending_approvals` | HITL queue |
| `agent_actions` | Audit log |

## `signals`

Each row is one triangulated decision: ticker, direction (`raised` / `lowered` / `maintained`), raw and calibrated confidence, quote, section, speaker, date, offsets, reasoning, NER JSON, self-consistency votes, `llm_model`, `content_hash`, provenance, `low_confidence`. Schema: `src/ecis/schemas/signal.py`. Low-confidence rows stay in the log and do not enter the Scorecard.

## Commands

```bash
python -m ecis.main --init-db
python -m ecis.main --migrate-tickers
python -m ecis.main --list-tickers
python -m ecis.main --resolve-outcomes
python -m ecis.main --approve 1
python -m ecis.main --reject 1
```

# Data layer

Turns filings into labelled chunks with embeddings. Direction (raised / lowered / maintained) is the extraction layer, not this one.


| Module                            | Path                             |
| --------------------------------- | -------------------------------- |
| Ingest                            | `src/ecis/ingestion/`            |
| Clean, normalise, chunk, validate | `src/ecis/preprocessing/`        |
| Embeddings                        | `src/ecis/embedding/`            |
| Ticker registry                   | `src/ecis/db/ticker_registry.py` |
| Config                            | `src/ecis/config/settings.py`    |


- Fetch: [README.md](README.md). 
- Flow: [flow.md](flow.md). 
- Databases: [src/ecis/db/README.md](../src/ecis/db/README.md).
- Vectors: [src/ecis/embedding/README.md](../src/ecis/embedding/README.md).

---



## Ingestion:

1. **EDGAR** (`edgar_fetcher.py`) — ticker → CIK, full-text search for earnings-related 8-Ks. Rate limit: 10 requests/second (`EDGAR_USER_AGENT`). HTML under `raw/edgar/{ticker}/`; `file_metadata` includes `period_of_report` when present.
2. **FMP** (`fmp_fetcher.py`) — JSON transcripts under `raw/fmp/{ticker}/`. Free tier: 250 calls/day with a counter and backoff. Cached files are not re-downloaded.

---



## Cleaning (`cleaner.py`):

- **EDGAR:** strip 8-K wrappers, safe-harbour / forward-looking disclaimers, HTML, nested tables, duplicate headers.
- **FMP:** pull transcript text from JSON; fix encoding.
- Output: UTF-8 under `processed/cleaned/`.

---



## Normalisation (`normaliser.py`):

- Label prepared remarks vs Q&A.
- Canonicalise speaker strings.
- EDGAR filings without headers use heuristics (question-mark rate, speaker rotation).
- Markers such as `[SECTION: prepared_remarks]` and `[SPEAKER: …]` travel into chunking.

---



## Chunking (`chunker.py`):


| Setting     | Value                                      |
| ----------- | ------------------------------------------ |
| Target size | ~400 tokens                                |
| Overlap     | 50 tokens                                  |
| Tokenizer   | FinBERT (512-token context)                |
| Boundaries  | Do not cross section; prefer speaker turns |


Each chunk keeps source path, ticker, transcript date, section, speaker, chunk index, and character offsets.

---



## Validation (`chunk_validator.py`):

Chunks are dropped (and logged) when empty, below `min_chunk_tokens`, or above `max_boilerplate_ratio`. 

---



## Embeddings (`embedder.py`, `exemplar_store.py`):

- Model: `sentence-transformers/all-MiniLM-L6-v2` (384-d), cosine distance.
- `ecis_transcripts`: valid chunks; filter by ticker, date range, section.
- `ecis_exemplars`: few-shot extraction examples.

Used at extract time for similar exemplars and prior-quarter context, and on the dashboard RAG tab.

---



## Ticker registry (`ticker_registry.py`):

Source of truth for which companies are in the system.


| Field                                       | Role                                          |
| ------------------------------------------- | --------------------------------------------- |
| `ticker`                                    | Primary key                                   |
| `company_name`, `sector`, `fiscal_calendar` | Identity                                      |
| `transcript_source`                         | `edgar` / `fmp` / `both`                      |
| `total_transcripts`, `last_ingestion_date`  | Inventory                                     |
| `extraction_status`                         | `pending` / `complete` / `empty` / `no_files` |
| `outcome_resolution_status`                 | Whether outcomes have been graded             |


```bash
python -m ecis.main --migrate-tickers
python -m ecis.main --list-tickers
```

---



## Filing dates:

Some 8-K filenames use the *acceptance* date, not the earnings-call date. The pipeline prefers `period_of_report` / transcript date from `file_metadata` when available.

---



## Stores:


| Store                                        | Role                                |
| -------------------------------------------- | ----------------------------------- |
| `signals.db`                                 | Append-only extraction log          |
| `outcomes.db`                                | Horizon prices and correctness      |
| `agents.db`                                  | Registry, weights, thresholds, HITL |
| `checkpoints.db`                             | LangGraph crash recovery            |
| Chroma `ecis_transcripts` / `ecis_exemplars` | Chunk and few-shot vectors          |



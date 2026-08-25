# Data

How ECIS fetches transcripts and what happens to them on disk. Runtime files are written under `src/ecis/data/`.


| Document                                                          | Contents                                     |
| ----------------------------------------------------------------- | -------------------------------------------- |
| [README.md](README.md)                                            | Fetching transcripts (this file)             |
| [flow.md](flow.md)                                                | Ingest → clean → chunk → embed               |
| [architecture/](architecture/)                                    | Data-flow diagram                            |
| [layer.md](layer.md)                                              | Sources, preprocessing, embeddings, registry |
| [src/ecis/db/README.md](../src/ecis/db/README.md)                 | SQLite databases and tables                  |
| [src/ecis/embedding/README.md](../src/ecis/embedding/README.md)   | ChromaDB collections                         |


Code: `src/ecis/ingestion/`, `src/ecis/preprocessing/`, `src/ecis/embedding/`, `src/ecis/db/`.

---

## Layout:

```
src/ecis/data/
  raw/edgar/{ticker}/{filing_date}.htm
  raw/fmp/{ticker}/{transcript_date}.json
  processed/cleaned/{ticker}/
  processed/normalised/{ticker}/
  processed/chunks/{ticker}/{date}_chunks.json
  db/signals.db
  db/outcomes.db
  db/agents.db
  db/checkpoints.db
```

---

## Prerequisites:

```bash
cp src/ecis/.env.example src/ecis/.env
python -m ecis.main --init-db
```


| Variable           | Needed for              |
| ------------------ | ----------------------- |
| `EDGAR_USER_AGENT` | SEC EDGAR               |
| `FMP_API_KEY`      | Financial Modeling Prep |


---

## Fetch transcripts:

Replace `TICKER` with any listed symbol (comma-separated for several companies).

```bash
python -m ecis.main --ingest --ticker TICKER --source edgar
python -m ecis.main --ingest --ticker TICKER --source fmp
python -m ecis.main --ingest --ticker TICKER --source both
python -m ecis.main --ingest --ticker TICKER1,TICKER2 --source both
```

`--ingest` writes under `raw/`, records `file_metadata`, and upserts the ticker registry. It does not clean or extract.

**EDGAR** (`src/ecis/ingestion/edgar_fetcher.py`) — ticker → CIK, full-text search for earnings-related 8-Ks (and exhibits). Rate limit: 10 requests/second.

**FMP** (`src/ecis/ingestion/fmp_fetcher.py`) — JSON transcripts with speaker turns. Daily counter at 250 calls; cached files are skipped on rerun.

---

## After fetch:

```bash
python -m ecis.main --preprocess --ticker TICKER
python -m ecis.main --batch --ticker TICKER --model llama
```

If raw files already exist:

```bash
python -m ecis.main --migrate-tickers
python -m ecis.main --list-tickers
```

Market prices for the Scorecard (`yfinance`):

```bash
python -m ecis.main --resolve-outcomes
python -m ecis.main --resolve-outcomes --ticker TICKER
```


# Data layer

This pipeline ingests raw filings from EDGAR and FMP, parsing them into semantically chunked, labeled, and embedded representations for downstream readers. The generated signals, structured outcomes, and high-dimensional vectors are then persisted to SQLite and ChromaDB, respectively.


| Document                                                        | Contents                                          |
| --------------------------------------------------------------- | ------------------------------------------------- |
| [data/README.md](../data/README.md)                             | How to fetch transcripts (EDGAR / FMP)            |
| [data/flow.md](../data/flow.md)                                 | Ingest → clean → chunk → embed                    |
| [data/layer.md](../data/layer.md)                               | Sources, preprocessing, ChromaDB, ticker registry |
| [src/ecis/db/README.md](../src/ecis/db/README.md)               | SQLite databases and tables                       |
| [src/ecis/embedding/README.md](../src/ecis/embedding/README.md) | ChromaDB collections                              |


---



### Code:

1. `src/ecis/ingestion/`
2. `src/ecis/preprocessing/`
3. `src/ecis/embedding/`
4. `src/ecis/db/`

---


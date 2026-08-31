# ECIS package

Installable Python package (`import ecis`). CLI: `python -m ecis.main`.

| Path | Role |
|---|---|
| [ingestion/](ingestion/) | EDGAR and FMP fetchers |
| [preprocessing/](preprocessing/) | Clean, normalise, chunk, validate |
| [embedding/](embedding/) | MiniLM + ChromaDB |
| [readers/](readers/) | Keyword, FinBERT, NER, LLM |
| [extraction/](extraction/) | Triangulate, dedup, vindicate |
| [graphs/](graphs/) | LangGraph pipeline and agent loops |
| [scoring/](scoring/) | Outcomes and Scorecard |
| [db/](db/) | SQLite schemas, registry, HITL |
| [dashboard/](dashboard/) | Streamlit |
| [api/](api/) | FastAPI |
| [config/](config/) | Settings and taxonomy |
| [schemas/](schemas/) | Signal and graph state |
| [notebooks/](notebooks/) | Colab / Ollama |
| [scripts/](scripts/) | One-off utilities |
| [main.py](main.py) | CLI |

Guides: [`docs/`](../../docs/README.md). Data: [`data/`](../../data/README.md).
# Embeddings

MiniLM vectors and ChromaDB collections for transcript chunks and few-shot exemplars.

- Databases: `[../db/README.md](../db/README.md)`. 
- Data layer: `[../../../data/layer.md](../../../data/layer.md)`.


| File                                   | Role                                         |
| -------------------------------------- | -------------------------------------------- |
| [embedder.py](embedder.py)             | Encode chunks; collection `ecis_transcripts` |
| [exemplar_store.py](exemplar_store.py) | Add / retrieve few-shot exemplars            |


---

## Collections:


| Collection         | Contents                                 | Used for                                                |
| ------------------ | ---------------------------------------- | ------------------------------------------------------- |
| `ecis_transcripts` | ~400-token chunks, cosine / MiniLM 384-d | Prior-quarter context, conflict surround, dashboard RAG |
| `ecis_exemplars`   | Curated extraction examples              | LLM few-shot retrieval                                  |


Filters: ticker, date range, section label.

```bash
python -m ecis.main --preprocess --ticker TICKER
```

---
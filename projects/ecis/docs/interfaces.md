# Interfaces

## Streamlit dashboard:

```bash
python -m ecis.main --dashboard
```

App: `src/ecis/dashboard/app.py`. 


| Tab                   | Purpose                                                                               |
| --------------------- | ------------------------------------------------------------------------------------- |
| **Signal Explorer**   | Filterable table: ticker, direction, confidence, quote, `llm_model`, reasoning traces |
| **Reader Comparison** | Per-reader Brier / ECE / accuracy; current triangulator weights                       |
| **Model Comparison**  | Llama vs Mistral Scorecard; ticker registry table                                     |
| **Calibration**       | Reliability diagrams (stated confidence vs observed accuracy)                         |
| **Agent Activity**    | Audit log of orchestration, watchdog, learning, vindication                           |
| **Approvals**         | HITL: inspect proposal + evidence, Approve or Reject                                  |
| **RAG Query**         | Natural-language search over ChromaDB chunks with citations                           |


RAG is only as dense as the embedding store. 

SQLite is opened with WAL and short-lived connections so the dashboard and scoring jobs can share files.

---



## FastAPI:

```bash
python -m ecis.main --api
```


| Method | Path                      | Body / query                                            | Result                                               |
| ------ | ------------------------- | ------------------------------------------------------- | ---------------------------------------------------- |
| GET    | `/health`                 |                                                         | `{status: ok}`                                       |
| GET    | `/signals`                | `ticker`, `direction`, `source_method`, dates, `limit`  | Signal rows                                          |
| GET    | `/signals/{id}`           |                                                         | One signal                                           |
| GET    | `/signals/{id}/outcomes`  |                                                         | Horizon grades                                       |
| GET    | `/scores`                 | `ticker`, `horizon`                                     | Per-reader metrics                                   |
| GET    | `/scores/{source_method}` |                                                         | One reader                                           |
| GET    | `/scorecard`              | `ticker`, `horizon`                                     | Readers + by-model + weights + HITL + recent actions |
| POST   | `/query`                  | `{query, n_results, ticker, section_label}`             | Cited chunks                                         |
| GET    | `/tickers`                |                                                         | Registry (fallback: distinct signal tickers)         |
| POST   | `/extract`                | `{ticker, transcript_path? , transcript_text?, model?}` | Run pipeline, return signals                         |
| GET    | `/approvals`              |                                                         | Pending HITL                                         |
| POST   | `/approvals/{id}/approve` | optional `{note}`                                       | Apply proposal                                       |
| POST   | `/approvals/{id}/reject`  | optional `{note}`                                       | Dismiss proposal                                     |


`POST /extract` `model` accepts `llama`, `mistral`, `both`, or a raw Ollama tag. If only `transcript_text` is sent, it is written to a temp file for the existing pipeline.

---


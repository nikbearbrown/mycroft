# ECIS documentation

**ECIS** (Earnings Call Intelligence Signals) is a financial intelligence system that turns raw earnings-call transcripts into structured, confidence-scored guidance and then grades every signal against what the market actually did.

The pages below are the map of that system. If this is your first time here, start with the workflow. Otherwise, feel free to open whichever section you need.


| #   | Document                                                        | Contents                                                                                                              |
| --- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 1   | [workflow.md](workflow.md)                                      | End-to-end workflow, data flow, and agent loops                                                                       |
| 2   | [running-the-pipeline.md](running-the-pipeline.md)              | Environment, CLI, and how to run every command                                                                        |
| 3   | [data/](../data/)                                               | Fetching, data flow, and data layer ([README](../data/README.md), [flow](../data/flow.md), [layer](../data/layer.md)) |
| 4   | [extraction.md](extraction.md)                                  | Signal schema, four readers, triangulation, deduplication                                                             |
| 5   | [orchestration.md](orchestration.md)                            | LangGraph pipeline, escalation A/B/C/D, conflict resolution                                                           |
| 6   | [scoring-and-feedback.md](scoring-and-feedback.md)              | Outcomes, Scorecard metrics, watchdog, learning graph, HITL                                                           |
| 7   | [interfaces.md](interfaces.md)                                  | Streamlit dashboard and FastAPI                                                                                       |
| 8   | [models-and-colab.md](models-and-colab.md)                      | Llama vs Mistral, Ollama, Colab notebooks                                                                             |
| —   | [src/ecis/db/README.md](../src/ecis/db/README.md)               | SQLite databases and tables                                                                                           |
| —   | [src/ecis/embedding/README.md](../src/ecis/embedding/README.md) | ChromaDB collections                                                                                                  |




---

## Visuals:


| Folder                         | Contents                                                                                                                   |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| [architecture/](architecture/) | [System](architecture/ecis_system_architecture.png) and [data flow](architecture/ecis_data_flow_architecture.png) diagrams |
| [artifacts/](artifacts/)       | Claude artifacts and other generated reference files                                                                       |




---

## Code map:


| Area      | Package                                                                                                                                          |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| CLI       | `src/ecis/main.py`                                                                                                                               |
| Config    | `src/ecis/config/`                                                                                                                               |
| Data      | `src/ecis/ingestion/`, `src/ecis/preprocessing/`, `src/ecis/embedding/` — [data/](../data/), [embedding README](../src/ecis/embedding/README.md) |
| Readers   | `src/ecis/readers/`                                                                                                                              |
| Combine   | `src/ecis/extraction/`                                                                                                                           |
| Graphs    | `src/ecis/graphs/`                                                                                                                               |
| Scorecard | `src/ecis/scoring/`                                                                                                                              |
| UI / API  | `src/ecis/dashboard/`, `src/ecis/api/`                                                                                                           |
| Storage   | `src/ecis/db/` — [db README](../src/ecis/db/README.md)                                                                                           |
| Tests     | `tests/`                                                                                                                                         |



# Orchestration

The extraction pipeline is a LangGraph state machine in `src/ecis/graphs/pipeline_graph.py`. Typed state is `PipelineState` in `src/ecis/schemas/state.py`.

---

## Graph nodes:

```
ingestion → chunking → fast_pass → escalation
        → llm_extraction → conflict_resolution
        → ner → triangulation → deduplication → logging
```


| Node                  | What it does                                   |
| --------------------- | ---------------------------------------------- |
| `ingestion`           | Load file, clean, normalise                    |
| `chunking`            | Section-aware token chunks                     |
| `fast_pass`           | Keyword + FinBERT on every chunk               |
| `escalation`          | Assign A/B/C/D; persist classifications        |
| `llm_extraction`      | LLM on A and B only                            |
| `conflict_resolution` | LLM tie-break on C                             |
| `ner`                 | Entities on A/B/C                              |
| `triangulation`       | Weighted consensus                             |
| `deduplication`       | Merge near-duplicate quotes                    |
| `logging`             | Append to `signals.db`; update ticker registry |


`run_pipeline(ticker, path, llm_model=...)` compiles the graph and invokes it. `--extract --model both` calls this once per model.

LangGraph can take a checkpointer. Crash-recovery tests against `checkpoints.db` are still a follow-up.

---

## Escalation classifier:

`src/ecis/graphs/orchestration_agent.py`. Thresholds are loaded from `escalation_thresholds` in `agents.db` (defaults: FinBERT min 0.6, keyword min 0.5).


| Category | Rule                                                    | Downstream        |
| -------- | ------------------------------------------------------- | ----------------- |
| **D**    | No keyword match and no FinBERT direction               | Skip              |
| **C**    | Both detected, FinBERT confident, directions differ     | Conflict subgraph |
| **A**    | Both detected, FinBERT confident, same direction        | LLM confirm       |
| **B**    | Everything else (one reader, or low FinBERT confidence) | LLM reason        |


Every batch is also written to `chunk_classifications` so the learning graph can measure Category D near-misses (FinBERT just below the skip threshold).

---

## Conflict subgraph:

`src/ecis/graphs/conflict_subgraph.py` and `src/ecis/extraction/conflict_resolver.py`.

1. Retrieve the previous and next chunk (three-chunk window).
2. Build a prompt that states the disagreement.
3. LLM resolves direction and names the vindicated reader.
4. Insert into `vindication_records`.

Those records feed [vindication aggregation](scoring-and-feedback.md).

---

## Conditional routing note:

LangGraph conditional edges return **one** next node for the whole state. Escalation therefore **partitions chunk indices** into `category_a_indices` … `category_d_indices` on the shared state. Downstream nodes pull only their lists. That avoids routing an entire transcript to a single category.

---

## CLI entry:

```bash
python -m ecis.main --extract --ticker TICKER --model llama
python -m ecis.main --extract --ticker TICKER --model mistral
python -m ecis.main --extract --ticker TICKER --model both
```

---


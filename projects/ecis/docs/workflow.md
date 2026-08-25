# Overall workflow

ECIS is a pipeline plus three feedback loops. Transcripts go in; scored, calibrated guidance signals come out; the system then updates its own thresholds, weights, and displayed confidence.

---

## Big picture:



---

## Stages in order:

### 1. Ingest

EDGAR full-text search downloads earnings-related 8-K HTML. FMP downloads pre-formatted transcript JSON. Files are cached under `src/ecis/data/raw/{edgar|fmp}/{ticker}/` and indexed. The **ticker registry** records company, source, transcript count, and extraction status.

### 2. Preprocess

HTML/JSON wrappers, legal boilerplate, and encoding noise are stripped. Speaker labels are canonicalised. Prepared remarks and Q&A are tagged. Text is split into overlapping ~400-token chunks (50-token overlap, FinBERT tokenizer, section-aware). Chunks are embedded with MiniLM and stored in ChromaDB (`ecis_transcripts`). Few-shot exemplars live in a second collection (`ecis_exemplars`).

### 3. Fast pass

Every chunk is scored by:

- **Keyword reader** — regex taxonomy of raised / lowered / maintained phrases (microseconds).
- **FinBERT** — financial sentiment mapped to a guidance direction (batched).

These two votes are cheap. They decide whether the LLM is worth calling.

### 4. Escalation (orchestration agent)


| Category | Meaning                                  | Next step         |
| -------- | ---------------------------------------- | ----------------- |
| **A**    | Both readers agree, FinBERT is confident | LLM confirmation  |
| **B**    | One reader fired, or confidence is low   | LLM deeper pass   |
| **C**    | Readers disagree on direction            | Conflict subgraph |
| **D**    | Neither reader found anything            | Skip LLM          |


This cut typically avoids 60–80% of LLM calls. Thresholds live in SQLite and can be retuned by the learning graph.

### 5. LLM extraction

For A/B chunks the LLM reader runs:

1. Few-shot exemplar retrieval (similar labelled examples).
2. Prior-quarter chunks for the same ticker (implicit raises/cuts).
3. Chain-of-thought JSON extraction (`raised` / `lowered` / `maintained` / `none`).
4. Self-consistency at temperatures 0.1, 0.3, 0.5.
5. Multi-turn verification (CONFIRM / REVISE / REJECT).

**Llama 3.1 8B Instruct** and **Mistral 7B Instruct** are both supported. Each signal is stamped with `llm_model` so the Scorecard can compare them.

### 6. Conflict, NER, triangulation, dedup

Category C chunks get a three-chunk context window and an LLM tie-break. The winner is recorded as a **vindication**. spaCy NER attaches companies, amounts, percentages, and dates (NER does not vote on direction). The triangulator combines keyword / FinBERT / LLM with dynamic weights. Quotes with cosine similarity ≥ 0.90 and the same direction are merged.

### 7. Pre-registration

Every validated signal is appended to `signals.db`. Schema: [db README](../src/ecis/db/README.md).

### 8. Outcomes and Scorecard

After 30 / 90 / 180 days, yfinance prices vs a sector benchmark produce excess return. Grading:

- `raised` is correct if excess return > 0
- `lowered` is correct if excess return < 0
- `maintained` is correct if |excess return| ≤ 2%

Metrics: Brier score, Brier skill vs keyword baseline, expected calibration error, Murphy decomposition (calibration vs resolution), information ratio.

### 9. Feedback loops


| Loop                    | Watches                | Action                                  |
| ----------------------- | ---------------------- | --------------------------------------- |
| Calibration watchdog    | Rolling ECE and skill  | Recalibrate, or propose a weight cut    |
| Learning graph          | Category D near-misses | Loosen or tighten escalation thresholds |
| Vindication aggregation | Who won conflicts      | Update triangulator weights             |


Routine changes apply automatically. Structural moves (large threshold jumps, weight cuts) pause as **pending approvals** for a human on the dashboard or CLI.

---



## What a “signal” is:

A signal is one guidance detection with provenance: ticker, direction, raw and calibrated confidence, supporting quote, section, speaker, transcript date, chunk index, character offsets, reasoning trace, NER entities, self-consistency votes, verification status, and which LLM produced it.

The contract is `src/ecis/schemas/signal.py` (`SignalRecord`). Invalid records never enter the log.

---



## Runtime paths:

Two ways to run the same workflow:

- **Local** — Ollama on the Mac, CLI in this repo.
- **Colab** — Ollama on a Colab GPU; either the whole pipeline runs in the notebook, or only inference is tunneled back to the Mac.

See [running-the-pipeline.md](running-the-pipeline.md) and [models-and-colab.md](models-and-colab.md).

---


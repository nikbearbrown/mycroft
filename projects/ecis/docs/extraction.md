# Extraction layer

Extraction turns chunks into `SignalRecord` objects. Four readers run; only some of them vote on direction.

---

## Signal contract:

Defined in `src/ecis/schemas/signal.py`. Important fields:


| Field                                                 | Meaning                                        |
| ----------------------------------------------------- | ---------------------------------------------- |
| `ticker`                                              | Company                                        |
| `direction`                                           | `raised` / `lowered` / `maintained`            |
| `confidence_raw`                                      | Model confidence in 0, 1                       |
| `confidence_calibrated`                               | After Platt / isotonic                         |
| `source_method`                                       | `keyword`, `finbert`, `llm`, `triangulated`, … |
| `supporting_quote`                                    | Exact span                                     |
| `section_label`                                       | `prepared_remarks` or `qa`                     |
| `speaker`                                             | Normalised identity                            |
| `transcript_date`, `chunk_index`, `character_offsets` | Provenance                                     |
| `reasoning_trace`                                     | LLM chain-of-thought                           |
| `ner_entities`                                        | Structured extras                              |
| `self_consistency_votes`                              | Three temperature passes                       |
| `verification_status`                                 | `confirmed` / `revised` / `rejected`           |
| `llm_model`                                           | Ollama tag that produced the LLM vote          |


Invalid records raise; they are not written to the decision log.

---

## Keyword reader:

`src/ecis/readers/keyword_reader.py` + `src/ecis/config/taxonomy.yaml`.

- 30–50 phrases per direction (`raising guidance`, `revised downward`, `reaffirming guidance`, …).
- Word-boundary regex to avoid substring false positives.
- Output: matched phrases, direction, binary confidence.
- Baseline for **Brier skill score** of every other reader.



---

## FinBERT reader:

`src/ecis/readers/finbert_reader.py` — `ProsusAI/finbert`.

- Batched inference (16–32), eval mode, CUDA / MPS / CPU.
- Three-way sentiment (positive / negative / neutral) mapped to guidance direction with thresholds. Positive sentiment is **not** automatically “raised”.
- Chunks near 512 tokens are validated so batch padding does not silently truncate.



---

## NER reader:

`src/ecis/readers/ner_reader.py` — spaCy.

Extracts ORG names, dollar amounts, percentages, dates/periods, and financial metrics. Attached as metadata. **Does not vote** on direction.

---

## LLM reader:

`src/ecis/readers/llm_reader.py` — Ollama client at `OLLAMA_BASE_URL`.

### Models


| Alias     | Default tag                 | Notes                                               |
| --------- | --------------------------- | --------------------------------------------------- |
| `llama`   | `llama3.1:8b-instruct-q8_0` | Stronger calibration; better on explicit numbers    |
| `mistral` | `mistral:7b-instruct`       | Better on hedged language; JSON sometimes truncates |


`--model both` runs the pipeline twice and stamps `llm_model` on each signal. Mistral prompts add an explicit “close every brace” reminder and retry if `{` / `}` counts do not match.

### Technique stack

1. **Few-shot retrieval** — 3 similar exemplars from `ecis_exemplars`.
2. **Temporal retrieval** — 2–3 prior-quarter chunks for the same ticker (soft-fail if ChromaDB is empty).
3. **Chain-of-thought** — forward vs backward looking; change vs reaffirmation; lexical evidence; direction; confidence.
4. **Self-consistency** — temperatures 0.1 / 0.3 / 0.5. Unanimous → keep; 2-of-3 → keep with a confidence penalty; 3-way split → `none`.
5. **Verification** — second call at temperature 0: CONFIRM, REVISE, or REJECT.

`none` means “no guidance signal in this chunk”, which is distinct from `maintained` (guidance explicitly reaffirmed). That boundary is a known error cluster; the CoT prompt was tightened for it.

---

## Triangulator:

`src/ecis/extraction/triangulator.py`.

Initial weights (updated later by vindication):


| Reader          | Weight |
| --------------- | ------ |
| Keyword         | 0.15   |
| FinBERT         | 0.20   |
| LLM             | 0.50   |
| Agreement bonus | 0.15   |


Highest weighted direction wins. Adapters normalise binary flags, probability distributions, entity lists, and JSON extractions into one schema. Partial outputs are allowed.

---

## Deduplicator:

`src/ecis/extraction/deduplicator.py`.

- Cosine similarity on quote embeddings.
- ≥ 0.90 and same direction → merge (keep higher confidence, note both chunks).
- ≥ 0.90 and opposite direction → flag for review.

Stops the same sentence in prepared remarks and Q&A from counting twice.

---

## Logging:

`log_signal` appends to `signals.db`. Pre-registration: no updates, no deletes. `llm_model` is stored so Llama and Mistral can be scored separately.
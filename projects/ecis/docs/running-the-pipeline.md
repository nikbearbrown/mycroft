# Running the pipeline

All commands are run from the **repository root** (`Mycroft_Contribution`). The package lives at `src/ecis/` (src layout); `pip install -e .` makes `python -m ecis.main` importable. 

Data files default to `src/ecis/data/`.

---

## 1. Environment:

```bash
cd Mycroft_Contribution

python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -e .
python -m spacy download en_core_web_sm

cp src/ecis/.env.example src/ecis/.env
```

Edit `src/ecis/.env`:


| Variable            | Required            |
| ------------------- | ------------------- |
| `EDGAR_USER_AGENT`  | Yes for EDGAR       |
| `FMP_API_KEY`       | For FMP transcripts |
| `OLLAMA_BASE_URL`   | Yes                 |
| `LLM_MODEL`         | No (default Llama)  |
| `LLM_LLAMA_MODEL`   | No                  |
| `LLM_MISTRAL_MODEL` | No                  |
| `LLM_QWEN_MODEL`    | No                  |


Pull all three extraction models:

```bash
ollama serve
ollama pull llama3.1:8b-instruct-q8_0
ollama pull mistral:7b-instruct
ollama pull qwen2.5:14b-instruct-q4_K_M
```

Initialise SQLite:

```bash
python -m ecis.main --init-db
```

Creates `signals.db`, `outcomes.db`, `agents.db`, `checkpoints.db` under `src/ecis/data/db/`, plus default reader weights and escalation thresholds. 

- Schema: `[src/ecis/db/README.md](../src/ecis/db/README.md)`. 
- Embeddings: `[src/ecis/embedding/README.md](../src/ecis/embedding/README.md)`.

If you already have files on disk:

```bash
python -m ecis.main --migrate-tickers
python -m ecis.main --list-tickers
```

---

## 2. Stage-by-stage:

Replace `TICKER` with any listed symbol.

```bash
# A. Download transcripts
python -m ecis.main --ingest --ticker TICKER --source both

# B. Clean, normalise, chunk, embed
python -m ecis.main --preprocess --ticker TICKER

# C. Extract guidance (Llama, Mistral, Qwen, both, or all)
python -m ecis.main --extract --ticker TICKER --model llama
python -m ecis.main --extract --ticker TICKER --model mistral
python -m ecis.main --extract --ticker TICKER --model qwen
python -m ecis.main --extract --ticker TICKER --model both
python -m ecis.main --extract --ticker TICKER --model all

# One file only
python -m ecis.main --extract --ticker TICKER --file src/ecis/data/raw/edgar/TICKER/YYYY-MM-DD.htm --model llama
```

`--extract` without `--ticker` uses the ticker registry.

Several tickers:

```bash
python -m ecis.main --ingest --ticker TICKER1,TICKER2 --source both
python -m ecis.main --preprocess --ticker TICKER1,TICKER2
python -m ecis.main --extract --ticker TICKER1,TICKER2 --model all
```

---

## 3. One-shot batch:

Ingest → preprocess → extract:

```bash
python -m ecis.main --batch --ticker TICKER1,TICKER2 --model all
```

---

## 4. Outcomes and Scorecard:

```bash
python -m ecis.main --resolve-outcomes
python -m ecis.main --resolve-outcomes --ticker TICKER

python -m ecis.main --score
python -m ecis.main --score --ticker TICKER --horizon 30

python -m ecis.main --recalibrate platt
python -m ecis.main --recalibrate isotonic
```

`--resolve-outcomes` fetches prices at the signal date and at +30 / +90 / +180 days. Horizons that are still in the future are left unresolved.

---

## 5. Agent loops and HITL:

```bash
python -m ecis.main --watchdog      # calibration / weight proposals
python -m ecis.main --learn         # retune A/B/C/D thresholds
python -m ecis.main --vindicate     # update triangulator weights

python -m ecis.main --approve 1
python -m ecis.main --reject 1
```

Pending proposals also appear on the dashboard **Approvals** tab.

---

## 6. Dashboard and API:

```bash
python -m ecis.main --dashboard     # Streamlit
python -m ecis.main --api           # FastAPI
```

---

## 7. Tests:

```bash
python -m pytest tests/ -q
```

---

## CLI reference:


| Flag                           | Meaning                                                                                 |
| ------------------------------ | --------------------------------------------------------------------------------------- |
| `--init-db`                    | Create / migrate databases                                                              |
| `--ticker A,B`                 | Comma-separated tickers                                                                 |
| `--file PATH`                  | Single transcript for `--extract`                                                       |
| `--ingest`                     | Fetch EDGAR / FMP                                                                       |
| `--source edgar                | fmp                                                                                     |
| `--preprocess`                 | Clean → normalise → chunk → embed                                                       |
| `--extract`                    | Run the LangGraph extraction graph                                                      |
| `--batch`                      | Ingest + preprocess + extract                                                           |
| `--model`                      | `llama`, `mistral`, `qwen`, `both` (Llama+Mistral), `all` (all three), or an Ollama tag |
| `--resolve-outcomes`           | Grade signals vs market prices                                                          |
| `--score`                      | Print Scorecard                                                                         |
| `--horizon 30                  | 90                                                                                      |
| `--recalibrate platt           | isotonic`                                                                               |
| `--watchdog`                   | Calibration watchdog                                                                    |
| `--learn`                      | Orchestration learning graph                                                            |
| `--vindicate`                  | Vindication → weights                                                                   |
| `--migrate-tickers`            | Fill registry from `data/raw/`                                                          |
| `--list-tickers`               | Print registry                                                                          |
| `--approve ID` / `--reject ID` | HITL                                                                                    |
| `--dashboard` / `--api`        | UI servers                                                                              |


---

## Typical workflow:

1. `--ingest` new filings.
2. `--preprocess` then `--extract --model all`.
3. `--resolve-outcomes` for signals that have reached a horizon.
4. `--score` and inspect the dashboard (Reader Comparison, Model Comparison, Calibration).
5. `--watchdog`, `--learn`, `--vindicate`. Approve or reject HITL items.

---

## Common failures:


| Symptom                  | What to check                                     |
| ------------------------ | ------------------------------------------------- |
| EDGAR 403                | `EDGAR_USER_AGENT` must include a real email      |
| FMP empty                | Key missing or daily 250-call cap                 |
| LLM connection error     | `ollama serve` and `OLLAMA_BASE_URL`              |
| Model not found          | `ollama pull` all three tags                      |
| No raw files             | `--ingest` first, or `--migrate-tickers`          |
| Sparse RAG               | Preprocess so ChromaDB is populated               |
| Jagged calibration curve | Too few resolved outcomes; wait for more horizons |


GPU / Colab execution: [models-and-colab.md](models-and-colab.md).

---


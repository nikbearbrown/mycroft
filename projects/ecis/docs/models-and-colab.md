# Models and Colab

ECIS treats **Llama 3.1 8B Instruct**, **Mistral 7B Instruct**, and **Qwen2.5 14B Instruct** as peer extractors. All three must be available wherever inference runs (local Ollama or Colab).

---

## Local Ollama:

```bash
ollama serve
ollama pull llama3.1:8b-instruct-q8_0
ollama pull mistral:7b-instruct
ollama pull qwen2.5:14b-instruct-q4_K_M
```

Tags in `src/ecis/.env`:

```
OLLAMA_BASE_URL="http://localhost:11434"
LLM_MODEL="llama3.1:8b-instruct-q8_0"
LLM_LLAMA_MODEL="llama3.1:8b-instruct-q8_0"
LLM_MISTRAL_MODEL="mistral:7b-instruct"
LLM_QWEN_MODEL="qwen2.5:14b-instruct-q4_K_M"
```

```bash
python -m ecis.main --extract --ticker TICKER --model llama
python -m ecis.main --extract --ticker TICKER --model mistral
python -m ecis.main --extract --ticker TICKER --model qwen
python -m ecis.main --extract --ticker TICKER --model both
python -m ecis.main --extract --ticker TICKER --model all
```

`--model both` runs Llama and Mistral. `--model all` runs all three. Each signal stores `llm_model`. The dashboard Model Comparison tab and `GET /scorecard` `by_model` split on that field.

The Python client uses `OLLAMA_BASE_URL`, so a Colab Cloudflare tunnel works from the CLI machine without code changes.

---



## Colab notebooks:


| Notebook                                      | Use                                                                         |
| --------------------------------------------- | --------------------------------------------------------------------------- |
| `src/ecis/notebooks/colab/ollama_colab.ipynb` | Unzip the repo on Colab, pull all three models, run extraction there        |
| `src/ecis/notebooks/ollama_server.ipynb`      | **Mode A**: pipeline on Colab. **Mode B**: tunnel Ollama to the CLI machine |


Setup: **Runtime → Change runtime type → GPU** (A100 preferred for Qwen 14B).

Both notebooks:

1. Install and start Ollama.
2. Pull Llama 8B, Mistral 7B, and Qwen2.5 14B (4-bit).
3. Refuse to continue if any of the three is missing.
4. Smoke-test one ticker on Llama, then Mistral, then Qwen.
5. Full run with `EXTRACT_MODEL = "all"` (or `llama` / `mistral` / `qwen` / `both`).
6. Print signal counts by `llm_model`.

---



### Mode A — everything on Colab:

```python
EXTRACT_MODEL = "all"   # or llama / mistral / qwen / both
```

---



### Mode B — Colab as remote GPU:

The notebook prints:

```
OLLAMA_BASE_URL="https://….trycloudflare.com"
```

Paste that into `src/ecis/.env` on the CLI machine. Keep the notebook running, then from the repo root:

```bash
python -m ecis.main --extract --ticker TICKER --model qwen
python -m ecis.main --extract --ticker TICKER --model all
```

Signals are written to the SQLite files on the CLI machine.

---



## Runtime notes:

Inference is Ollama (local or Colab). Qwen 14B 4-bit needs more VRAM than the 7B/8B models; A100 is the usual Colab target. Ollama loads one model at a time.
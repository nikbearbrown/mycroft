# Earnings Call Intelligence Signals

#### Every quarter, 500 companies tell the market where they're headed. The signal hides in plain sight. ECIS reads what others skim.

---

## What is ECIS?

ECIS (Earnings Call Intelligence Signals) is a financial intelligence system that transforms raw earnings call transcripts into structured, confidence-scored guidance signals, and then holds itself accountable by grading every prediction against real market outcomes.

> Built to extract. Designed to doubt. Engineered to improve.

---

## The Vision:

Earnings calls are the richest public source of corporate intent. Executives disclose revenue targets, margin expectations, and strategic direction. Analysts probe for weakness. The language is deliberate, the stakes are real, and every transcript is public record.

ECIS turns that language into structured intelligence, not by trusting a single model, but by orchestrating multiple readers that challenge each other, catch each other's blind spots, and build trust through validated outcomes.

---

## How It Thinks:

ECIS doesn't just extract. It reasons, verifies, and learns.

**Four Readers, One Signal**

Every transcript chunk runs through four independent lenses:

1. **Keyword Reader** — Fast, interpretable pattern matching against a curated financial taxonomy. The permanent baseline that every other reader must beat to justify its existence.
2. **FinBERT Reader** — Financial sentiment analysis via a domain-specific transformer. Catches tone and framing that keywords miss.
3. **NER Reader** — Extracts the specifics: company names, dollar amounts, percentages, dates. Attaches the numbers to the narrative.
4. **LLM Reader** — Deep reasoning powered by chain-of-thought prompting, dynamic few-shot retrieval, cross-transcript temporal context, self-consistency decoding, and multi-turn verification. The heavy hitter that earns its compute cost.

**Intelligent Routing:**

Not every chunk deserves an LLM call. The orchestration agent classifies each chunk and routes intelligently:

| Category | What it means | Where it goes |
| --- | --- | --- |
| **A** | Both readers agree with confidence | LLM confirms |
| **B** | Ambiguous, one reader flagged | LLM reasons deeply |
| **C** | Readers disagree | Conflict resolution |
| **D** | Nothing detected | Skip entirely |

Result: **60-80% fewer LLM calls.** Same quality. Fraction of the cost.

**Self-Consistency Verification:**

The same extraction runs at three temperatures. If the answer holds across all three, the signal is robust. If it drifts, the evidence isn't strong enough. When passes diverge completely, the system exercises disciplined restraint; it withholds the signal rather than committing noise to the decision log.

**Multi-Turn Verification:**

After self-consistency approves a signal, the model argues against its own answer. "You said guidance was raised. Are you sure? Could this be maintenance with optimistic framing?" Only signals that survive self-critique enter the decision log.

---

## How It Learns:

This is what makes ECIS genuinely different. It doesn't just extract; it grades itself and adapts.

**The Decision Scorecard:**

Every signal is pre-registered in an append-only, immutable log before outcomes are known. No retroactive adjustments. No cherry-picking. After 30, 90, and 180 days, the Scorecard checks what actually happened:

- Brier Score — How accurate were the predictions?
- Skill Score — Did the LLM actually beat keyword matching?
- Calibration Error — When we said 80% confident, were we right 80% of the time?
- Murphy Decomposition — Is the error fixable (calibration) or fundamental (resolution)?
- Information Ratio — Would acting on these signals have made money?

**Three Feedback Loops:**

1. Confidence Calibration — The watchdog detects when stated confidence drifts from observed accuracy and recalibrates automatically. Future signals display earned trust, not raw model confidence.
2. Extraction Routing — The learning graph analyzes missed signals and adjusts which chunks get sent to the LLM. Too aggressive? Loosen thresholds. Too conservative? Tighten them.
3. Reader Trust — The vindication aggregator tracks which readers win in conflicts and shifts triangulator weights accordingly. Proven readers gain influence. Unreliable ones lose it.

Every cycle, the system gets a little more honest, a little more efficient, and a little harder to fool.

---

## Repository:

| Path | Role |
| --- | --- |
| [`src/ecis/`](src/ecis/) | Installable package. CLI: `python -m ecis.main`. See the [package README](src/ecis/README.md). |
| [`docs/`](docs/) | System documentation. Start at [docs/README.md](docs/README.md). |
| [`docs/architecture/`](docs/architecture/) | Architecture and pipeline diagrams. |
| [`docs/artifacts/`](docs/artifacts/) | Artifacts and other reference files. |
| [`data/`](data/) | How transcripts are fetched, stored, and transformed. |
| [`tests/`](tests/) | Unit tests (`pytest`). |
| [`pyproject.toml`](pyproject.toml) | Package metadata and pytest `pythonpath`. |
| [`requirements.txt`](requirements.txt) | Runtime and test dependencies. |

## Package (`src/ecis/`):

| Path | Role | Docs |
| --- | --- | --- |
| [`ingestion/`](src/ecis/ingestion/) | EDGAR and FMP fetchers | [data/README.md](data/README.md) |
| [`preprocessing/`](src/ecis/preprocessing/) | Clean, normalise, chunk, validate | [data/layer.md](data/layer.md) |
| [`embedding/`](src/ecis/embedding/) | MiniLM embeddings; ChromaDB stores | [embedding/README.md](src/ecis/embedding/README.md) |
| [`config/`](src/ecis/config/) | Settings and keyword taxonomy | [running-the-pipeline.md](docs/running-the-pipeline.md) |
| [`schemas/`](src/ecis/schemas/) | Signal and graph state | [extraction.md](docs/extraction.md) |
| [`readers/`](src/ecis/readers/) | Keyword, FinBERT, NER, LLM | [extraction.md](docs/extraction.md) |
| [`extraction/`](src/ecis/extraction/) | Triangulate, dedup, vindicate | [extraction.md](docs/extraction.md) |
| [`graphs/`](src/ecis/graphs/) | Pipeline, conflict, watchdog, learning | [orchestration.md](docs/orchestration.md) |
| [`scoring/`](src/ecis/scoring/) | Outcomes and Scorecard | [scoring-and-feedback.md](docs/scoring-and-feedback.md) |
| [`db/`](src/ecis/db/) | SQLite, ticker registry, HITL | [db/README.md](src/ecis/db/README.md) |
| [`dashboard/`](src/ecis/dashboard/) | Streamlit | [interfaces.md](docs/interfaces.md) |
| [`api/`](src/ecis/api/) | FastAPI | [interfaces.md](docs/interfaces.md) |
| [`notebooks/`](src/ecis/notebooks/) | Colab / Ollama | [models-and-colab.md](docs/models-and-colab.md) |
| [`scripts/`](src/ecis/scripts/) | Align signals; sample outcomes | [running-the-pipeline.md](docs/running-the-pipeline.md) |
| [`main.py`](src/ecis/main.py) | CLI | [running-the-pipeline.md](docs/running-the-pipeline.md) |

End-to-end flow: [docs/workflow.md](docs/workflow.md).

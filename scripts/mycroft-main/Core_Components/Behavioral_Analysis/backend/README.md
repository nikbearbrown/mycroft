# Backend

FastAPI + LangGraph backend. Parses brokerage CSVs, enriches trade data with market context, runs six parallel analysis agents, and synthesizes findings into a narrative edge report via Groq.

---

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file at the backend root:

```
GROQ_API_KEY=gsk_...
FRED_API_KEY=...       # free at fred.stlouisfed.org/docs/api/api_key.html
```

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

---

## API Endpoints

### `POST /parse-preview`

Validates a brokerage CSV and returns trade metadata without running the full analysis. Use this to confirm the file is correctly formatted before committing to a full run.

**Request:** `multipart/form-data` with a `file` field containing the CSV.

**Response:**
```json
{
  "broker": "robinhood",
  "total_trades": 58,
  "unique_tickers": 9,
  "date_range": { "start": "2023-01-05", "end": "2024-04-10" },
  "closed_trades": 32,
  "sample_tickers": ["AAPL", "NVDA", "MSFT", "TSLA", "META"]
}
```

---

### `POST /analyze`

Runs the full pipeline. Parses the CSV, enriches every trade, runs all six agents in parallel, and returns a complete `EdgeReport`.

**Request:** `multipart/form-data` with a `file` field containing the CSV.

**Response:** `EdgeReport` object containing:

| Field | Description |
|---|---|
| `trade_stats` | Aggregate metrics — total trades, win rate, avg hold, total P&L |
| `agent_findings` | List of findings from each agent: insights, metrics, edge score |
| `narrative` | LLM-generated verdict — the full edge report |
| `edge_profile` | Structured summary: edge scores by dimension, overall score, key insights |
| `generated_at` | ISO timestamp |

Expect 30–60 seconds on first run while yfinance and FRED data is fetched. Subsequent runs use cached data.

---

## Pipeline

**`parser.py`** — Detects broker format from CSV column signatures, normalizes to a common schema, and runs FIFO cost basis matching to compute realized P&L, hold duration, and win/loss on every closed position.

**`enricher.py`** — Joins each trade with yfinance ticker metadata (sector, industry, market cap), FRED macro data (VIX, fed funds rate, recession indicator), SPY-derived market regime classification, and earnings proximity from the yfinance calendar. All external calls are cached with `lru_cache`.

**`agents.py`** — Six pure Python functions, each taking the enriched DataFrame and returning an `AgentFindings` object with metrics, insights, and an edge score in the range −1 to +1.

**`graph.py`** — LangGraph `StateGraph` wiring. A `compute_stats` node runs first, then all six agent nodes run in parallel via fan-out edges. A `synthesize` node collects all findings, builds the prompt, and calls Groq to generate the narrative. Returns a complete `EdgeReport`.

**`models.py`** — Pydantic models: `Trade`, `EnrichedTrade`, `AgentFindings`, `EdgeReport`, `TradeStats`.

**`main.py`** — FastAPI app with CORS middleware, file upload handling, and the two endpoints above.
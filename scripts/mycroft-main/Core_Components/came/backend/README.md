# CAME — Backend

FastAPI backend with a six-node LangGraph intelligence pipeline and deterministic analytics engine.

## Setup

```bash
cp .env.example .env   # set DATABASE_URL and OLLAMA_* vars
pip install -r requirements.txt
uvicorn main:app --reload
```

## Structure

```
backend/
├── main.py              # FastAPI app entry
├── config.py            # Settings from .env
├── agent/
│   ├── graph.py         # LangGraph DAG
│   ├── nodes.py         # Six pipeline nodes
│   ├── state.py         # AgentState TypedDict
│   └── analytics.py     # HHI, entropy, turnover, drift math
├── db/
│   ├── models.py        # SQLAlchemy models
│   └── session.py       # Engine, SessionLocal, init_db
├── models/schemas.py    # Pydantic I/O schemas
└── routers/
    ├── events.py        # POST/GET/DELETE /event
    ├── strategy.py      # /strategy/compute|current|history|drift
    ├── capital.py       # /capital-flow, /simulate-allocation
    └── metrics.py       # /metrics
```

## API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/event` | Ingest a financial event |
| GET | `/event` | List all events |
| POST | `/strategy/compute` | Run the full LangGraph pipeline |
| GET | `/strategy/current` | Get latest strategy profile |
| GET | `/strategy/drift` | Get drift vs previous baseline |
| GET | `/capital-flow` | Sankey node/link data |
| POST | `/simulate-allocation` | Preview hypothetical events |
| GET | `/metrics` | Behavior feature history |

## Pipeline

```
Event Normalizer → State Builder → Pattern Engine →
Behavior Modeler → Drift Detector → Strategy Synthesizer
```

Strategy Synthesizer calls Ollama. If unavailable, falls back to a deterministic narrative automatically.
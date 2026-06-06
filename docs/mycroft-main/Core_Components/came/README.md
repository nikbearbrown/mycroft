# CAME — Capital Allocation Memory Engine

> **Developed by:** Darshan Rajopadhye (rajopadhye.d@northeastern.edu)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/therrshan)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/therrshan)

An agentic financial intelligence system that reconstructs a user's implicit capital allocation strategy from observed financial behavior over time.

Instead of analyzing assets or returns, CAME models how capital is deployed, identifies behavioral patterns, detects drift between intended and actual strategy, and infers latent risk posture and liquidity preference.

## Stack

- **Backend** — FastAPI, LangGraph, SQLAlchemy, PostgreSQL
- **Frontend** — React, Vite, Tailwind v4, Recharts, D3
- **LLM** — Ollama (local, free) with deterministic fallback

## Structure

```
came/
├── backend/    # FastAPI app, LangGraph pipeline, analytics engine
└── frontend/   # React dashboard
```

## Quickstart

```bash
# Postgres
psql -c "CREATE USER came WITH PASSWORD 'came';"
psql -c "CREATE DATABASE came OWNER came;"

# Backend
cd backend && cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# LLM (optional — fallback runs without it)
ollama pull llama3.1
```

Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`.
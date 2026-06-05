# Mycroft What-If Simulation Agent

**Developed by:** Anshika Khandelwal

[![n8n](https://img.shields.io/badge/Built%20with-n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Groq](https://img.shields.io/badge/LLM-Groq%20API-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://console.groq.com)
[![LLaMA](https://img.shields.io/badge/Model-LLaMA%203.3%2070B-blueviolet?style=for-the-badge)](https://groq.com)
[![Mycroft](https://img.shields.io/badge/Part%20of-Mycroft%20Framework-black?style=for-the-badge)](https://github.com/Humanitariansai/Mycroft)

---

## Overview

The **What-If Simulation Agent** is an n8n-based workflow designed to help investors evaluate investment decisions under uncertainty by simulating multiple "what if" scenarios before committing to a position.

Named after Sherlock Holmes's elder brother — a man of superior analytical ability who preferred to orchestrate from behind the scenes — this agent is part of the **Mycroft Framework**, an open-source educational experiment in AI-powered investment intelligence.

The agent accepts a stock profile as input, runs it through **three specialized simulation engines**, aggregates the results into a risk-adjusted verdict, and uses **Groq's free LLM (LLaMA 3.3 70B)** to generate a human-readable investment narrative. All results are persisted to a **PostgreSQL** database for historical tracking.

> **Tagline:** *"This agent doesn't just model outcomes — it analyzes how decisions change under different assumptions, identifies key risk drivers, and highlights the exact thresholds where recommendations shift."*

> ⚠️ **Disclaimer:** This agent provides structured scenario-based investment guidance using heuristic simulation logic and AI-generated narrative. It is intended for decision support and exploration, not as a live trading or valuation system.

---

## Key Capabilities

- Runs 3 independent what-if simulations on any stock profile
- Detects conflicts between fundamental growth and market sentiment
- Personalizes recommendations based on investor risk appetite (Low / Medium / High)
- Identifies the exact threshold where a recommendation changes (e.g. "if sentiment drops below 0.62 → BUY becomes HOLD")
- Runs 6 stress tests to measure decision stability
- Generates probabilistic scenario distributions (Best / Expected / Worst case)
- Produces AI-powered narrative insights via Groq (free LLM)
- Saves every simulation to PostgreSQL for audit and historical analysis
- Returns a fully structured JSON response in under 3 seconds

---

## The 3 Simulation Engines

### 1. 📈 Growth vs Sentiment Tradeoff
> *"What if revenue grows but sentiment drops — or vice versa?"*

Evaluates the relationship between a company's fundamental growth rate and its market sentiment score using a **3×3 signal matrix**. Detects four key scenarios:

| Growth | Sentiment | Signal |
|--------|-----------|--------|
| HIGH | HIGH | STRONG_BUY |
| HIGH | LOW | FUNDAMENTAL_BUY ⚠️ Conflict |
| LOW | HIGH | BUBBLE_RISK 🚨 |
| LOW | LOW | STRONG_SELL |

Outputs a bubble risk score, conflict flag, and return estimates for short and long term horizons.

---

### 2. ⚖️ Risk Appetite Simulator
> *"What if the same stock is evaluated by different types of investors?"*

Evaluates the stock against 4 weighted criteria (Revenue Growth, Sentiment, P/E Ratio, Debt/Equity) for each investor profile — Conservative, Balanced, and Aggressive. Shows how the same stock receives different recommendations depending on who is asking.

| Profile | Max Position | Stop-Loss | P/E Ceiling |
|---------|-------------|-----------|-------------|
| Conservative | 5% | 5% | 25x |
| Balanced | 10% | 10% | 40x |
| Aggressive | 20% | 20% | 80x |

---

### 3. 🎯 Threshold Break Simulator
> *"At what exact point does the recommendation change?"*

Sweeps sentiment (0.00 → 1.00) and growth (-10% → 60%) in 5% steps to find every breakpoint where the recommendation flips. Also runs 6 stress tests:

- Sentiment −10% / +10%
- Growth −10pp / +10pp
- Both −10% / Both +10%

Outputs a **stability score** (0–1), a **primary driver** (Sentiment or Growth), and a **stress resiliency** rating (HIGH / MEDIUM / LOW).

---

## Workflow Structure

High-level flow:

```
1. Receive POST request via Webhook
2. Parse and validate all input fields
3. Run Simulation 1 — Growth vs Sentiment Tradeoff
4. Run Simulation 2 — Risk Appetite Simulator
5. Run Simulation 3 — Threshold Break Simulator
6. Aggregate all 3 simulations into a weighted score
7. Build structured prompt for Groq LLM
8. Call Groq API (llama-3.3-70b-versatile)
9. Parse and validate LLM response
10. Prepare and execute PostgreSQL INSERT
11. Build and return final JSON response
```

### n8n Node Map

| # | Node Name | Type | Role |
|---|-----------|------|------|
| 1 | 🎯 Webhook | Webhook | Receives POST request |
| 2 | 🔍 Parse & Validate Input | Code | Defaults, types, validation |
| 3 | 📈 Sim 1 — Growth vs Sentiment | Code | 3×3 signal matrix |
| 4 | ⚖️ Sim 2 — Risk Appetite | Code | 4-criteria weighted evaluation |
| 5 | 🎯 Sim 3 — Threshold Break | Code | Breakpoint sweeps + stress tests |
| 6 | 🧠 Aggregate & Score | Code | Weighted scoring + scenarios |
| 7 | 📝 Build AI Prompt | Code | Prompt engineering for Groq |
| 8 | 🤖 Groq — Generate Insights | HTTP Request | Calls Groq API |
| 9 | 🔄 Parse Groq Response | Code | Extracts structured JSON |
| 10 | 🗄️ Prepare DB Record | Code | Builds SQL-safe INSERT |
| 11 | 💾 Save to PostgreSQL | PostgreSQL | Persists simulation results |
| 12 | 📊 Build Final Response | Code | Assembles full response payload |
| 13 | ✅ Respond to Webhook | Respond to Webhook | Returns JSON |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Workflow Engine | n8n (self-hosted) |
| LLM | Groq — LLaMA 3.3 70B Versatile (free tier) |
| Database | PostgreSQL |
| Language | JavaScript (n8n Code nodes) |
| API Protocol | REST / JSON |

---

## Sample Input

```json
{
  "company": "NVIDIA",
  "ticker": "NVDA",
  "revenue_growth": 0.35,
  "sentiment_score": 0.72,
  "risk_appetite": "medium",
  "time_horizon": "1year",
  "current_price": 875.50,
  "pe_ratio": 45.2,
  "debt_equity": 0.42,
  "market_cap_billions": 2160
}
```

### Input Field Reference

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `company` | string | — | Company name |
| `ticker` | string | — | Stock ticker symbol |
| `revenue_growth` | float | -1.0 to 20.0 | YoY revenue growth (0.35 = 35%) |
| `sentiment_score` | float | 0.0 to 1.0 | Market sentiment (0.72 = positive) |
| `risk_appetite` | string | low / medium / high | Investor risk profile |
| `time_horizon` | string | 3month / 1year / 5year | Investment time horizon |
| `current_price` | float | > 0 | Current stock price in USD |
| `pe_ratio` | float | > 0 | Price-to-earnings ratio |
| `debt_equity` | float | > 0 | Debt-to-equity ratio |
| `market_cap_billions` | float | > 0 | Market cap in billions USD |

---

## Sample Output

```json
{
  "verdict": {
    "emoji": "⚖️",
    "recommendation": "HOLD",
    "score": "3.54/5.0",
    "confidence": "62%",
    "mycroft_says": "NVIDIA's strong growth and high sentiment make it attractive, but caution is warranted due to sensitivity to sentiment changes."
  },
  "action_plan": {
    "immediate": "HOLD",
    "monitor_weekly": "Sentiment score",
    "exit_trigger": "Sentiment drops below 0.62 or growth below 25% YoY",
    "position_sizing": "Max 10% of portfolio — medium risk profile"
  },
  "risk_summary": {
    "overall_risk_level": "HIGH",
    "flag_count": 1,
    "primary_driver": "SENTIMENT"
  },
  "scenarios": {
    "best_case":  { "probability": 47, "return_estimate": "+38%" },
    "expected":   { "probability": 32, "return_estimate": "+10%" },
    "worst_case": { "probability": 21, "return_estimate": "-32%" }
  }
}
```

---

## Database Schema

Run this SQL in your PostgreSQL instance before activating the workflow:

```sql
CREATE TABLE IF NOT EXISTS mycroft_whatif_simulations (
  id                   SERIAL PRIMARY KEY,
  simulation_id        VARCHAR(50) UNIQUE NOT NULL,
  company              VARCHAR(100),
  ticker               VARCHAR(20),
  risk_appetite        VARCHAR(20),
  time_horizon         VARCHAR(20),
  final_recommendation VARCHAR(50),
  confidence_pct       INTEGER,
  aggregate_score      DECIMAL(3,2),
  bubble_risk_score    DECIMAL(4,3),
  stability_score      DECIMAL(4,3),
  input_params         JSONB,
  simulation_results   JSONB,
  ai_insights          JSONB,
  ai_verdict           TEXT,
  created_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mycroft_ticker         ON mycroft_whatif_simulations(ticker);
CREATE INDEX idx_mycroft_recommendation ON mycroft_whatif_simulations(final_recommendation);
CREATE INDEX idx_mycroft_created        ON mycroft_whatif_simulations(created_at DESC);
```

---

## Credentials & Setup

### Environment Variable
| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Free API key from [console.groq.com](https://console.groq.com) |

### n8n Credential
Create a PostgreSQL credential in n8n named exactly:
```
Mycroft PostgreSQL
```

### Free Groq Models (configurable in node 8)
| Model | Best For |
|-------|----------|
| `llama-3.3-70b-versatile` | Best quality (default) |
| `llama-3.1-8b-instant` | Fastest / high-volume testing |
| `mixtral-8x7b-32768` | Strong reasoning |
| `gemma2-9b-it` | Lightweight fallback |

---

## Credentials & Security

- No API keys or secrets are stored in this repository
- Groq authentication is handled via n8n environment variables
- PostgreSQL authentication is handled via n8n credentials (referenced by name only)
- No pinned execution data is included in the exported workflow JSON

---

## Usage Notes

- Import `mycroft_whatif_agent_groq.json` into n8n via **Workflows → Import from file**
- Run the SQL schema setup before activating
- Set `GROQ_API_KEY` in n8n Settings → Variables
- Groq free tier supports up to 30 requests/minute — suitable for testing and demos
- Designed for research, educational use, and investment analysis experimentation

---

## Future Possibilities

This agent is designed to be extensible. Potential enhancements include:

- **Additional Simulations**
  - Macro Shock Simulator (interest rate, inflation scenarios)
  - Hype vs Reality Detector (bubble probability scoring)
  - Counterfactual Reasoning ("what if sentiment were the opposite?")
  - Time Horizon Comparison (same stock, 3-month vs 5-year side by side)

- **Data Enrichment**
  - Real-time sentiment from news APIs and social media
  - Live price and financials from Yahoo Finance or Alpha Vantage
  - SEC filing integration for earnings signal detection

- **Visualization Layer**
  - Interactive dashboard (Streamlit, Grafana, or Metabase)
  - Breakpoint heatmaps showing sensitivity across parameter ranges
  - Scenario probability charts

- **Agent Orchestration**
  - Connect to Mycroft's Research Agent for automated company profiling
  - Feed output to Portfolio Agent for position sizing recommendations
  - Multi-stock comparison and ranking engine

---

## Project Context

This workflow is part of the **Mycroft Framework**, an open-source educational experiment under [Humanitarians.AI](https://github.com/Humanitariansai/Mycroft), focused on building modular, transparent, and reproducible AI-powered intelligence agents for investment research and education.

# Goal Setting System

**Investment goal extraction and portfolio simulation engine using local LLM and Monte Carlo analysis**

Part of Mycroft Orchestrator | Sprint 8 | Humanitarians AI

---

## Overview

Mycroft Goal Simulator combines natural language processing with financial simulation to analyze investment goals. The system extracts structured goals from conversational input and runs thousands of Monte Carlo simulations to calculate success probabilities and provide actionable recommendations.

**Key Capabilities:**
- Extract investment goals from natural language (local LLaMA via Ollama)
- Run Monte Carlo simulations (100-10,000 scenarios)
- Analyze multiple competing goals simultaneously
- Calculate success probabilities and risk metrics
- Provide data-driven recommendations

**Technology Stack:**
- FastAPI (Python web framework)
- Ollama (local LLM inference)
- yfinance (free market data)
- NumPy/Pandas (numerical computing)

---

## What It Does

### 1. Goal Extraction

**Input:** Natural language description
```
"I want to retire in 20 years with $2M. I have $100k saved and can invest $3k/month."
```

**Output:** Structured goal data
```json
{
  "goal_type": "retirement",
  "target_amount": 2000000,
  "timeline_years": 20,
  "current_savings": 100000,
  "monthly_contribution": 3000,
  "risk_tolerance": "moderate"
}
```

### 2. Portfolio Simulation

**Process:**
1. Fetches 20 years of historical market data (SPY, AGG, Treasury rates)
2. Runs 1,000+ Monte Carlo simulations with random market scenarios
3. Calculates portfolio growth with monthly contributions
4. Accounts for inflation, rebalancing, and volatility

**Output:** Probability analysis
```json
{
  "success_probability": 0.847,
  "median_outcome": 2145000,
  "worst_case_10th": 1650000,
  "best_case_90th": 2850000,
  "recommended_adjustments": [
    "✅ High success probability (84.7%). Goal is on track!"
  ]
}
```

## Example Usage

### Extract Goals

```bash
curl -X POST http://localhost:8000/api/v1/goals/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I want to retire in 20 years with $2M"
  }'
```

### Run Simulation

```bash
curl -X POST http://localhost:8000/api/v1/simulation/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "goals": [{
      "goal_id": "retirement_1",
      "goal_name": "Retirement",
      "target_amount": 2000000,
      "timeline_years": 20,
      "current_savings": 100000,
      "monthly_contribution": 3000,
      "allocation": {"stocks": 70, "bonds": 25, "cash": 5}
    }],
    "config": {"num_simulations": 1000}
  }' | jq
```
---

## Understanding Results

### Success Probability
- **> 85%** - Excellent, highly achievable
- **70-85%** - Good, on track
- **50-70%** - Moderate, needs attention
- **< 50%** - Low, significant changes needed

### Outcome Percentiles
- **10th Percentile** - Worst case (bad market conditions)
- **50th Percentile (Median)** - Most likely outcome
- **90th Percentile** - Best case (favorable markets)

### Recommendations
System provides actionable advice:
- Increase monthly contributions
- Adjust timeline expectations
- Modify risk allocation
- Prioritize competing goals

---

## Configuration

Edit `.env` file:

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.1:8b

# Simulation
DEFAULT_NUM_SIMULATIONS=1000
MARKET_DATA_YEARS=20
DEFAULT_INFLATION_RATE=0.03

# Market Data Sources
STOCK_TICKER=SPY   # S&P 500
BOND_TICKER=AGG    # Aggregate Bonds
CASH_TICKER=^IRX   # 13-week Treasury
```

---


See `backend/README.md` for detailed backend documentation.

---

## Key Features

- **Local Processing** - No API costs, complete privacy
- **Free Data Sources** - yfinance for historical market data
- **Production Ready** - Error handling, logging, validation
- **Modular Architecture** - Clean separation of concerns
- **Type Safe** - Full Pydantic schema validation
- **Auto Documentation** - OpenAPI/Swagger at `/api/v1/docs`

---

## API Documentation

When running, access interactive documentation:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

## License

MIT License

---

## Contact

**Project:** Mycroft Orchestrator  
**Author:** Darshan  
**Organization:** Humanitarians AI  
**Sprint:** 8 (January 2026)

---

**Built for intelligent financial planning automation**
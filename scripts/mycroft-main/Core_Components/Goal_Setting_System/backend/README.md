# Backend Documentation

Complete guide to the Mycroft Goal Simulator backend architecture, API routes, and setup.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                           │
│                        (app/main.py)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼──────────┐
│   API Layer    │      │   Core Logic      │
│   app/api/     │──────│   app/core/       │
└────────────────┘      └───────────────────┘
        │                         │
        │               ┌─────────┴──────────┐
        │               │                    │
        │        ┌──────▼──────┐    ┌───────▼────────┐
        │        │   LLM       │    │  Simulation    │
        │        │  (Ollama)   │    │ (Monte Carlo)  │
        │        └─────────────┘    └────────────────┘
        │               │                    │
        │        ┌──────▼──────┐    ┌───────▼────────┐
        │        │   Data      │    │   Schemas      │
        │        │ (yfinance)  │    │  (Pydantic)    │
        │        └─────────────┘    └────────────────┘
        │
┌───────▼────────┐
│   Endpoints    │
│  - health      │
│  - goals       │
│  - simulation  │
└────────────────┘
```

---

## API Routes

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Health Check

**GET** `/health`

Check service status and Ollama availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-29T13:36:38.123456",
  "version": "1.0.0",
  "environment": "development",
  "ollama": {
    "available": true,
    "url": "http://localhost:11434",
    "default_model": "llama3.1:8b",
    "available_models": ["llama3.1:8b", "llama3.2:3b"]
  }
}
```

**Implementation:** `app/api/v1/endpoints/health.py`

---

#### 2. Extract Goals

**POST** `/goals/extract`

Extract structured investment goals from natural language.

**Request Body:**
```json
{
  "text": "I want to retire in 20 years with $2M",
  "model": "llama3.1:8b",  // Optional
  "temperature": 0.1,       // Optional
  "user_id": "user_123"     // Optional
}
```

**Response:**
```json
{
  "success": true,
  "goals": [
    {
      "goal_type": "retirement",
      "description": "Retire with $2M in assets",
      "target_amount": 2000000,
      "timeline_years": 20,
      "timeline_months": 240,
      "risk_tolerance": "moderate",
      "priority": "high",
      "current_savings": null,
      "monthly_contribution": null,
      "annual_return_assumption": null,
      "constraints": [],
      "confidence_score": 0.85,
      "extracted_entities": {
        "amounts": ["$2M"],
        "dates": ["20 years"],
        "keywords": ["retire", "retirement"]
      }
    }
  ],
  "summary": "Primary retirement goal with moderate risk tolerance",
  "processed_at": "2026-01-29T13:36:38.123456",
  "model_used": "llama3.1:8b",
  "processing_time_ms": 2340.5
}
```

**Implementation:** `app/api/v1/endpoints/goals.py`

**Flow:**
1. Validate request (Pydantic)
2. Check Ollama availability
3. Build extraction prompt
4. Call Ollama LLM
5. Parse JSON response
6. Validate extracted goals
7. Return structured response

---

#### 3. Run Simulation

**POST** `/simulation/simulate`

Run Monte Carlo simulation for investment goals.

**Request Body:**
```json
{
  "goals": [
    {
      "goal_id": "retirement_1",
      "goal_name": "Retirement",
      "target_amount": 2000000,
      "timeline_years": 20,
      "current_savings": 100000,
      "monthly_contribution": 3000,
      "allocation": {
        "stocks": 70,
        "bonds": 25,
        "cash": 5
      }
    }
  ],
  "config": {
    "num_simulations": 1000,         // Optional: 100-10000
    "confidence_level": 0.95,        // Optional: 0.8-0.99
    "inflation_rate": 0.03,          // Optional: 0.0-0.1
    "rebalancing_frequency": "annually",  // monthly/quarterly/annually
    "use_historical_data": true,     // Optional
    "historical_years": 20           // Optional: 5-30
  }
}
```

**Response:**
```json
{
  "success": true,
  "total_success_probability": 0.847,
  "goals": [
    {
      "goal_id": "retirement_1",
      "goal_name": "Retirement",
      "success_probability": 0.847,
      "median_outcome": 2145000,
      "worst_case_10th": 1650000,
      "best_case_90th": 2850000,
      "expected_shortfall": 45000,
      "recommended_adjustments": [
        "✅ High success probability (84.7%). Goal is on track!"
      ],
      "percentile_outcomes": {
        "p5": 1520000,
        "p10": 1650000,
        "p25": 1890000,
        "p50": 2145000,
        "p75": 2420000,
        "p90": 2850000,
        "p95": 3100000
      }
    }
  ],
  "portfolio_statistics": {
    "total_goals": 1,
    "total_target_amount": 2000000,
    "total_monthly_contribution": 3000,
    "average_success_probability": 0.847,
    "weakest_goal": "Retirement",
    "strongest_goal": "Retirement"
  },
  "recommendations": [
    "✅ GOOD: 84.7% probability of achieving all goals."
  ],
  "simulation_timestamp": "2026-01-29T13:36:38.123456",
  "processing_time_ms": 4567.89
}
```

**Implementation:** `app/api/v1/endpoints/simulation.py`

**Flow:**
1. Validate request (allocations sum to 100%)
2. Fetch historical market data (yfinance)
3. Calculate portfolio statistics
4. Run Monte Carlo simulations
5. Calculate success probabilities
6. Generate recommendations
7. Return results

---

## Core Components

### 1. Configuration (`app/core/config.py`)

Manages all application settings using Pydantic Settings.

**Key Settings:**
- `OLLAMA_BASE_URL` - Ollama server URL
- `DEFAULT_MODEL` - LLM model to use
- `DEFAULT_NUM_SIMULATIONS` - Simulation count
- `MARKET_DATA_YEARS` - Historical data period
- `STOCK_TICKER`, `BOND_TICKER`, `CASH_TICKER` - Market tickers

**Usage:**
```python
from app.core.config import settings

print(settings.OLLAMA_BASE_URL)
```

---

### 2. Ollama Client (`app/core/llm/ollama_client.py`)

Handles communication with Ollama for LLM inference.

**Key Methods:**
- `check_health()` - Check Ollama status and available models
- `generate(prompt, model, temperature)` - Generate LLM response

**Usage:**
```python
from app.core.llm import ollama_client

response = await ollama_client.generate(
    prompt="Extract goals from: I want to retire...",
    model="llama3.1:8b"
)
```

---

### 3. Market Data Fetcher (`app/core/data/market_data.py`)

Fetches historical market data using yfinance.

**Key Methods:**
- `fetch_historical_returns(asset_class, years)` - Get returns for stocks/bonds/cash
- `get_portfolio_statistics(allocation, years)` - Calculate portfolio metrics

**Market Data:**
- **Stocks**: SPY (S&P 500)
- **Bonds**: AGG (Aggregate Bond Index)
- **Cash**: ^IRX (13-week Treasury)

**Fallback Strategy:**
If yfinance fails, uses synthetic data based on historical statistics:
- Stocks: 10% annual return, 16% volatility
- Bonds: 4.5% annual return, 6% volatility
- Cash: 3% annual return, 1% volatility

---

### 4. Monte Carlo Simulator (`app/core/simulation/monte_carlo.py`)

Runs Monte Carlo simulations for goal analysis.

**Algorithm:**
1. Get portfolio statistics (mean, std dev)
2. For each simulation:
   - Start with current savings
   - For each month in timeline:
     - Generate random return from distribution
     - Apply return to portfolio
     - Add monthly contribution (inflation-adjusted)
3. Calculate percentiles across all simulations
4. Generate recommendations

**Key Methods:**
- `simulate_goal(goal)` - Run simulations for single goal
- `_run_single_simulation(goal, stats)` - Single simulation path

---

### 5. Goal Parser (`app/core/processing/goal_parser.py`)

Parses LLM output into structured goals.

**Key Methods:**
- `extract_goals(request)` - Main extraction flow
- `extract_json_from_text(text)` - Extract JSON from LLM response

**Process:**
1. Build extraction prompt
2. Call Ollama
3. Parse JSON from response
4. Validate with Pydantic schemas
5. Return structured goals

---

## Schemas

### Goal Schemas (`app/schemas/goal.py`)

**InvestmentGoal:**
- `goal_type` - retirement, house_purchase, education, etc.
- `target_amount` - Dollar amount
- `timeline_years` - Years to achieve
- `risk_tolerance` - conservative, moderate, aggressive
- `priority` - high, medium, low
- `current_savings` - Amount saved
- `monthly_contribution` - Monthly investment

### Simulation Schemas (`app/schemas/simulation.py`)

**PortfolioAllocation:**
- `stocks` - % in stocks (0-100)
- `bonds` - % in bonds (0-100)
- `cash` - % in cash (0-100)

**SimulationConfig:**
- `num_simulations` - Number of Monte Carlo runs
- `confidence_level` - Statistical confidence
- `inflation_rate` - Annual inflation
- `rebalancing_frequency` - Portfolio rebalancing

---

## Setup & Development

### Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Ollama
ollama pull llama3.1:8b
```

### Running Locally

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start FastAPI
python -m app.main

# Or with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

Create `.env` file:
```bash
ENVIRONMENT=development
DEBUG=True
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.1:8b
LOG_LEVEL=INFO
```

---

## Testing

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/api/v1/health | jq

# Extract goals
curl -X POST http://localhost:8000/api/v1/goals/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Save $50k in 5 years"}' | jq

# Run simulation
curl -X POST http://localhost:8000/api/v1/simulation/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "goals": [{
      "goal_id": "test",
      "goal_name": "Test",
      "target_amount": 50000,
      "timeline_years": 5,
      "current_savings": 0,
      "monthly_contribution": 800,
      "allocation": {"stocks": 60, "bonds": 35, "cash": 5}
    }],
    "config": {"num_simulations": 500}
  }' | jq
```

---

## Error Handling

### Custom Exceptions (`app/utils/exceptions.py`)

- `GoalExtractionError` - Goal extraction failures
- `SimulationError` - Simulation failures
- `OllamaConnectionError` - Ollama connectivity issues
- `MarketDataError` - Data fetching failures

### Error Responses

```json
{
  "detail": "Goal extraction failed: model 'llama3.1:8b' not found"
}
```

---

## Logging

Configured in `app/utils/logging.py`

**Log Levels:**
- INFO - Normal operations
- WARNING - Recoverable issues
- ERROR - Failures that affect functionality

**Example Logs:**
```
2026-01-29 13:36:38 - app.api.v1.endpoints.simulation - INFO - Running 1000 simulations for 1 goals
2026-01-29 13:36:38 - app.core.data.market_data - INFO - Fetching stocks data for SPY
2026-01-29 13:36:42 - app.core.simulation.monte_carlo - INFO - Simulating goal: Retirement
```

---

## Performance Considerations

### Optimization Strategies

1. **Caching** - Market data cached for 1 hour
2. **Batch Processing** - Multiple goals simulated efficiently
3. **Async Operations** - Non-blocking LLM calls
4. **Vectorized Computation** - NumPy for simulations

### Bottlenecks

- **LLM Generation** - 2-5 seconds (model dependent)
- **Market Data Fetch** - 1-3 seconds per ticker
- **Monte Carlo** - Scales with num_simulations × timeline

---

## Security

### Current Implementation

- Input validation via Pydantic
- CORS configured (all origins allowed in dev)
- No authentication (add for production)
- No rate limiting (add for production)

### Production Recommendations

- Add API key authentication
- Implement rate limiting
- Configure specific CORS origins
- Add request logging
- Use HTTPS/TLS

---

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Config

```python
# Production settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

---

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused

### Adding New Endpoints

1. Create endpoint file in `app/api/v1/endpoints/`
2. Define route with `@router.post()` or `@router.get()`
3. Add Pydantic schemas in `app/schemas/`
4. Import and include router in `app/api/v1/api.py`

**Example:**
```python
# app/api/v1/endpoints/my_endpoint.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-route")
async def my_route():
    return {"message": "Hello"}

# app/api/v1/api.py
from app.api.v1.endpoints import my_endpoint
api_router.include_router(my_endpoint.router, prefix="/custom", tags=["Custom"])
```

---

## Troubleshooting

### Common Issues

**Ollama not responding:**
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart
ollama serve
```

**Import errors:**
```bash
# Ensure running from project root
pwd  # Should show mycroft-goal-simulator

# Reinstall dependencies
pip install -r requirements.txt
```

**Market data failures:**
- System automatically uses synthetic data
- Check network connectivity
- Verify yfinance is up to date

---

**Backend Documentation | Mycroft Goal Simulator**
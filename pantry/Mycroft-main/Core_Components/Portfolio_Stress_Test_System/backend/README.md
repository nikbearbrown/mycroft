# Portfolio Stress Testing System — Layers 1–4

FastAPI + Streamlit system that analyzes portfolio risk through four analytical lenses: regime-dependent diversification, historical crash simulation, factor exposure decomposition, and regime-specific performance analysis.

---

## Layers Overview

- **Layer 1** ✓ — Regime-Dependent Diversification
- **Layer 2** ✓ — Historical Crash Simulation
- **Layer 3** ✓ — Factor Exposure Decomposition
- **Layer 4** ✓ — Regime-Specific Performance Analysis

---

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Start the API (serves all four layers)
python -m app.main

# Start the Streamlit UI (separate terminal)
streamlit run streamlit_app.py
```

- API: `http://localhost:8001`
- Streamlit: `http://localhost:8501`
- Swagger docs: `http://localhost:8001/docs`

---

## Sample Portfolio CSV

A 12-holding diversified portfolio for testing all four layers:

```csv
ticker,shares,weight
MSFT,40,0.10
JPM,50,0.10
JNJ,45,0.09
XOM,60,0.09
AMZN,15,0.09
UNH,20,0.08
LMT,18,0.08
NEE,80,0.08
PG,55,0.08
GLD,35,0.08
BRK-B,25,0.07
TLT,70,0.06
```

---

## Layer 1: Regime-Dependent Diversification

Analyzes how portfolio correlation structure changes across three market volatility regimes and quantifies how much diversification degrades under stress.

### Regimes
- **Low VIX (<15)**: Calm markets
- **Medium VIX (15–25)**: Normal volatility
- **High VIX (>25)**: Stress periods

### How It Works

**1. Data Collection** — `app/services/data_fetcher.py`
- Fetches historical prices from Yahoo Finance via `yfinance`
- Fetches VIX data for the same period
- Applies 5-day rolling average to VIX to reduce noise

**2. Regime Classification** — `app/services/regime_classifier.py`
- Classifies each trading day into low/medium/high regime
- Filters out short regime periods (< 20 days) to avoid single-day spikes

**3. Returns Calculation** — `app/services/returns_calculator.py`
- Converts prices to log returns: `r_t = ln(P_t / P_{t-1})`

**4. Correlation Analysis** — `app/services/correlation_analyzer.py`
- Calculates Pearson correlation matrix per regime
- Strips timezone info from both indexes before alignment to prevent pandas misalignment errors
- Metrics per regime:
  - Average pairwise correlation (portfolio-weighted)
  - Max/min correlation
  - Effective number of assets: `N_eff = 1 / Σ(w_i × w_j × ρ_ij)`

**5. Risk Analysis** — `app/services/risk_analyzer.py`
- Compares low vs high VIX metrics to calculate degradation
- Risk flags: `SEVERE_CORRELATION_SPIKE`, `MAJOR_DIVERSIFICATION_LOSS`, `EXTREME_STRESS_CORRELATION`, `ILLUSION_OF_DIVERSIFICATION`

**6. Visualization** — `app/services/visualization.py`
- Side-by-side correlation heatmaps for each regime
- Degradation bar chart

### API

**Endpoint:** `POST /api/v1/analyze`

```bash
curl -X POST "http://localhost:8001/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": [
      {"ticker": "AAPL", "shares": 100, "weight": 0.4},
      {"ticker": "MSFT", "shares": 75,  "weight": 0.3},
      {"ticker": "GOOGL","shares": 50,  "weight": 0.3}
    ],
    "params": {
      "lookback_days": 756,
      "vix_low_threshold": 15.0,
      "vix_high_threshold": 25.0
    }
  }'
```

---

## Layer 2: Historical Crash Simulation

Time-travels current portfolio holdings through past market crashes to reveal structural vulnerabilities before they appear in live performance.

### Key Insight
A portfolio that "held up relatively well" means it tracked the crash — not that it avoided loss. Flags fire on both relative underperformance vs benchmark and absolute drawdown severity.

### Predefined Crash Periods

| Key | Name | Period | Benchmark | Context |
|---|---|---|---|---|
| `covid_2020` | COVID Crash | Feb 19 – Mar 23, 2020 | SPY | S&P fell ~34% in 33 days |
| `tech_selloff_2022` | Tech Selloff 2022 | Jan 3 – Oct 12, 2022 | QQQ | NASDAQ fell ~33% over 9 months |
| `q4_selloff_2018` | Q4 Selloff 2018 | Sep 20 – Dec 24, 2018 | SPY | Fed tightening + trade war fears |
| `flash_crash_2015` | Flash Crash 2015 | Aug 1 – Aug 24, 2015 | SPY | China slowdown, S&P fell ~12% |

Custom date ranges are also supported via the UI or API.

### How It Works

**1. Data Fetching** — `app/services/data_fetcher.py`
- Fetches crash window prices with a 5-day pre-period buffer for day-1 return calculation
- Fetches up to 2 years of post-crash data for recovery measurement

**2. Simulation** — `app/services/crash_simulator.py`
- Computes portfolio daily log returns weighted by position sizes
- Calculates cumulative return: `exp(Σ log_returns) - 1`
- Computes drawdown series: `(wealth - running_max) / running_max`
- Measures recovery: first day post-crash where portfolio recoups full loss
- Non-fatal: individual crash periods are skipped with a warning if data is unavailable

**3. Loss Attribution** — `app/services/loss_analyzer.py`
- Decomposes portfolio loss by holding: `contribution_i = weight_i × return_i`
- Calculates each holding's share of total portfolio loss
- Generates per-crash and cross-crash risk flags

**4. Visualization** — `app/services/crash_visualization.py`
- Drawdown paths: portfolio vs benchmark curves per crash
- Loss attribution: horizontal bar chart of per-holding contributions
- Summary heatmap: holdings × crashes matrix

### Risk Flags

| Flag | Condition |
|---|---|
| `SEVERE_DRAWDOWN` | Max drawdown < -20% |
| `SIGNIFICANT_UNDERPERFORMANCE` | Portfolio > 5% worse than benchmark |
| `SLOW_RECOVERY` | Recovery took > 120 trading days |
| `NOT_YET_RECOVERED` | Not recovered within 2-year observation window |
| `CONCENTRATED_LOSS_DRIVER:<TICKER>` | Single holding drove > 15% of total loss |
| `CONSISTENTLY_SEVERE_DRAWDOWNS` | Severe drawdown in 2+ crashes |
| `CONSISTENT_UNDERPERFORMANCE_VS_BENCHMARK` | Underperformed benchmark in 2+ crashes |
| `REPEAT_LOSS_CONCENTRATION` | Same ticker drove concentrated losses in 2+ crashes |

### API

**Endpoint:** `POST /api/v1/crash-simulation`

```bash
curl -X POST "http://localhost:8001/api/v1/crash-simulation" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": [...],
    "selected_crashes": ["covid_2020", "tech_selloff_2022"],
    "custom_crash": {
      "key": "svb_2023",
      "name": "SVB Crisis",
      "start": "2023-03-01",
      "end": "2023-05-04",
      "benchmark_ticker": "SPY",
      "description": "Regional banking crisis triggered by SVB collapse"
    }
  }'
```

---

## Layer 3: Factor Exposure Decomposition

Reveals the hidden factor bets driving portfolio returns using the Fama-French 5-factor model extended with momentum. Runs three regression modes: static (full period), rolling (time-varying), and regime-conditional (per VIX environment).

### The Six Factors

| Factor | What It Measures |
|---|---|
| **MKT** | Market beta — sensitivity to broad market moves |
| **SMB** | Size premium — small-cap vs large-cap tilt |
| **HML** | Value premium — high book-to-market vs growth tilt |
| **RMW** | Profitability — high vs low operating profitability |
| **CMA** | Investment — conservative vs aggressive reinvestment |
| **UMD** | Momentum — recent winners vs recent losers |

### Model

```
(R_p - R_f) = α + β_MKT·MKT + β_SMB·SMB + β_HML·HML
                + β_RMW·RMW + β_CMA·CMA + β_UMD·UMD + ε
```

All factor data sourced free from the Kenneth French Data Library.

### How It Works

**1. Factor Data** — `app/services/factor_fetcher.py`
- Downloads FF5 + momentum daily ZIPs from the French library
- Parses and merges into a single DataFrame (MKT, SMB, HML, RMW, CMA, UMD, RF)
- Caches to `app/data/factor_cache/factor_data.parquet`, refreshes weekly
- Falls back to stale cache if download fails
- French library typically lags 4–6 weeks — portfolio returns are automatically clipped to factor data availability

**2. Static Regression** — `app/services/factor_regression.py`
- Full-period OLS regression with statsmodels
- Returns β coefficients, t-stats, p-values, R², adjusted R², annualised alpha
- Factor contribution to variance: `β²_factor × Var(F) / Var(R_p)`

**3. Rolling Regression** — `app/services/factor_regression.py`
- 252-day rolling OLS window, one regression per trading day
- DataFrame slices preserve column names for correct parameter extraction
- Drift flag fires when beta range > 0.4 over the window

**4. Regime-Conditional Regression** — `app/services/factor_regression.py`
- Separate OLS per VIX regime (low/medium/high)
- Minimum 15 observations required; skipped regimes shown as N/A in heatmap
- Reveals how factor loadings shift between calm and stress environments

### Risk Flags

| Flag | Condition |
|---|---|
| `HIGH_MARKET_BETA:<value>` | MKT β > 1.3 |
| `SIGNIFICANT_LONG/SHORT_<FACTOR>_TILT` | \|β\| > 0.3 and p < significance level |
| `HIGH_UNEXPLAINED_VARIANCE:<pct>` | R² < 0.60 |
| `SIGNIFICANT_POSITIVE/NEGATIVE_ALPHA:<value>` | Annualised \|α\| > 5% and p < 0.05 |
| `CONCENTRATED_<FACTOR>_EXPOSURE:<pct>_OF_VARIANCE` | Single factor > 50% of explained variance |
| `FACTOR_DRIFT:<FACTOR>:range=<value>` | Rolling beta range > 0.4 |
| `REGIME_BETA_SHIFT:<FACTOR>:<low→high>` | \|β_high_vix - β_low_vix\| > 0.4 for MKT, UMD, or SMB |

### API

**Endpoint:** `POST /api/v1/factor-exposure`

```bash
curl -X POST "http://localhost:8001/api/v1/factor-exposure" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": [...],
    "params": {
      "lookback_days": 756,
      "rolling_window": 252,
      "significance_level": 0.05
    }
  }'
```

---

## Layer 4: Regime-Specific Performance Analysis

Measures portfolio performance statistics separately for each VIX regime, detects regime transitions, and computes forward returns after each transition type. Closes the analytical loop: Layer 1 showed correlation structure, Layer 2 showed crash damage, Layer 3 showed factor mechanics — Layer 4 shows the performance consequence.

### How It Works

**1. Per-Regime Statistics** — `app/services/regime_performance.py`
- Annualised return, volatility, and Sharpe ratio per regime
- Max drawdown and average drawdown within each regime
- Win rate (fraction of positive days) and best/worst single day
- Cumulative return over all regime days

**2. Regime Transition Analysis** — `app/services/regime_performance.py`
- Detects every day the portfolio crosses from one VIX regime to another
- Computes forward portfolio returns over 5 and 20 trading days after each transition
- Summarises by transition type (Low→High, Med→High, etc.)
- Flags dangerous transitions where average 5-day forward return is negative

**3. Cumulative Return Series** — `app/services/regime_performance.py`
- Full equity curve with each data point tagged by active VIX regime
- Used for colour-coded equity curve chart

**4. Risk-Free Rate** — sourced from the Fama-French RF column in the existing factor cache, consistent with Layer 3 Sharpe calculations. Falls back to zero RF if cache unavailable.

**5. Visualization** — `app/services/regime_performance_viz.py`
- **Regime stats bar chart**: return, volatility, Sharpe, and max drawdown side by side per regime
- **Win rate chart**: win rate, best day, worst day per regime
- **Transition heatmap**: avg 5-day and 20-day forward returns for each transition type, N/A on diagonal
- **Equity curve**: full cumulative return coloured segment-by-segment by active VIX regime

### Risk Flags

| Flag | Condition |
|---|---|
| `NEGATIVE_SHARPE:<REGIME>_VIX:<value>` | Sharpe < 0 in any regime |
| `LOW_SHARPE:<REGIME>_VIX:<value>` | Sharpe < 0.5 in any regime |
| `REGIME_RETURN_GAP:<gap>pp` | Low vs high VIX annualised return differs by > 10pp |
| `VOL_SPIKE_IN_STRESS:<multiplier>x` | High VIX volatility > 1.5× low VIX volatility |
| `LOW_WIN_RATE_HIGH_VIX:<rate>` | Win rate < 45% during high VIX periods |
| `DANGEROUS_TRANSITION:LOW_TO_HIGH:avg_5d=<return>` | Avg 5-day return after Low→High transition < -2% |
| `DANGEROUS_TRANSITION:MED_TO_HIGH:avg_5d=<return>` | Avg 5-day return after Med→High transition < -2% |

### API

**Endpoint:** `POST /api/v1/regime-performance`

```bash
curl -X POST "http://localhost:8001/api/v1/regime-performance" \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": [...],
    "params": {
      "lookback_days": 756,
      "vix_low_threshold": 15.0,
      "vix_high_threshold": 25.0,
      "transition_windows": [5, 20]
    }
  }'
```

**Response includes:** per-regime stats, all transition events, transition summaries, full cumulative series, risk flags, recommendations, base64 visualizations.

---

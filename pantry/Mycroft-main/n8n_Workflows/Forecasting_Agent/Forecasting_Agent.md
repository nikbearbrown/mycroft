 ## Forecasting Agent Workflow

An advanced **n8n workflow** that generates stock price forecasts by combining **market data (Alpha Vantage)** with **FinBERT-based sentiment analysis**.  
The agent computes **optimistic, realistic, and pessimistic scenarios**, applies **risk scoring**, and stores results in **PostgreSQL** for downstream dashboards and reporting.

---

## 🚀 Features
- **Market Data Integration** – Fetches OHLC price data via Alpha Vantage API
- **Sentiment Analysis** – Integrates FinBERT for domain-specific sentiment scoring
- **Scenario Forecasting** – Produces optimistic, realistic, and pessimistic values
- **Volatility Analysis** – Detects risk levels (low, medium, high) from price fluctuations
- **Backtesting** – Tracks error metrics (MAPE, RMSE) for forecast validation
- **Database Storage** – Persists results into PostgreSQL for historical analysis
- **Multi-Symbol Support** – Runs forecasts for multiple tickers in a single execution
- **Alerting (Optional)** – Email/Slack notifications for low-confidence predictions

---

## 🎯 System Architecture (Diagram)
<img width="426" height="157" alt="image" src="https://github.com/user-attachments/assets/86f5ada0-1569-4915-89ca-fac13c6b7ab2" />

---

## 📊 Workflow Design (n8n)
- **Manual Trigger** – Starts the workflow
- **Code Node (Symbols)** – Defines tickers (AAPL, MSFT, TSLA, etc.)
- **Alpha Vantage Node** – Fetches OHLC data (TIME_SERIES_DAILY)
- **Historical Data Node** – Cleans and formats market data
- **FinBERT Node** – Generates sentiment scores (positive, neutral, negative)
- **Merge Node** – Combines sentiment and historical data
- **Code Node (Feature Engineering)** – Calculates volatility, momentum, and trends
- **Code Node (Forecast Engine)** – Generates scenarios and assigns confidence
- **If Node** – Applies thresholds for alerts
- **PostgreSQL Insert** – Persists forecasts in database
- **Optional Notifications** – Email/Slack alerts for high-risk cases

---

## ⚙️ Setup Instructions

### 1. Database Setup
Create results table:
```sql
CREATE TABLE forecasting_results (
    id SERIAL PRIMARY KEY,
    timestamp timestamptz NOT NULL,
    symbol text NOT NULL,
    optimistic_value numeric,
    realistic_value numeric,
    pessimistic_value numeric,
    overall_confidence numeric,
    volatility_level text,
    mape numeric,
    rmse numeric,
    created_at timestamptz DEFAULT now()
);
```

### 2. API Configuration
Update your Configuration/Code node with your Alpha Vantage key and ticker list:
```json
{
  "alpha_vantage_key": "your_api_key_here",
  "symbols": ["AAPL", "MSFT", "TSLA"]
}
```
> **Note:** Alpha Vantage free tier allows only **5 calls/minute**. For larger workloads, consider Polygon.io or TwelveData.

### 3. Workflow Import
- Import the `Forecasting_Agent.json` file into n8n  
- Configure environment variables (API keys, DB credentials)  
- Run manually or schedule via cron

---

## 📈 Example Output
```json
[
  {
    "timestamp": "2025-10-03T17:15:35.653Z",
    "symbol": "AAPL",
    "optimistic_value": 323.92,
    "realistic_value": 297.56,
    "pessimistic_value": 273.34,
    "overall_confidence": 0.672,
    "volatility_level": "medium",
    "mape": 4.93,
    "rmse": 24.65
  },
  {
    "timestamp": "2025-10-03T17:15:35.653Z",
    "symbol": "MSFT",
    "optimistic_value": 556.11,
    "realistic_value": 529.07,
    "pessimistic_value": 503.35,
    "overall_confidence": 0.705,
    "volatility_level": "low",
    "mape": 4.55,
    "rmse": 22.73
  },
  {
    "timestamp": "2025-10-03T17:15:35.653Z",
    "symbol": "TSLA",
    "optimistic_value": 742.05,
    "realistic_value": 627.89,
    "pessimistic_value": 531.29,
    "overall_confidence": 0.598,
    "volatility_level": "high",
    "mape": 5.83,
    "rmse": 29.15
  }
]
```

---

## 📝 Notes
- **API Limitations** – Alpha Vantage free tier is restricted to 5 calls/minute
- **Current Scope** – Supports multiple tickers in one run
- **Customizable Assumptions** – Risk thresholds and sentiment weights can be tuned per industry

---

## 🔮 Future Extensions
- Expand to more tickers with higher-rate APIs (Polygon.io, TwelveData)
- Real-time dashboards in Grafana/Power BI
- Include R² and MAE scoring for stronger validation
- Expand sentiment feeds (Reddit, Twitter, SEC filings)
- Integrate reinforcement learning for adaptive forecasts

---

## 🙌 Acknowledgments
- **n8n** – Workflow automation platform
- **Alpha Vantage** – Market data provider
- **Hugging Face (FinBERT)** – Sentiment model
- **PostgreSQL** – Storage backend

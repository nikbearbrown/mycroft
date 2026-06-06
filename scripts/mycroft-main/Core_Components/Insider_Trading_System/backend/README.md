# Congressional Trading Analysis - Backend

FastAPI backend for scraping and analyzing congressional stock trades.

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

## Architecture

```
backend/
├── main.py              # FastAPI app, routes, background tasks
├── database.py          # SQLAlchemy models (Trade, Analysis)
├── scraper.py           # Capitol Trades scraper (Selenium)
├── analyzer.py          # Stock price analysis (yfinance)
└── congressional_trades.db  # SQLite database
```

## Key Endpoints

**POST /scrape** - Scrape trades from Capitol Trades (background task)
**POST /analyze** - Analyze trades with stock data (background task)
**GET /trades** - Get all trades (filters: politician, ticker, analyzed)
**GET /analyses** - Get all analyses
**GET /stats** - Dashboard statistics

## How It Works

1. **Scraper** (`scraper.py`)
   - Selenium scrapes Capitol Trades website
   - Filters: filed within 45 days, >$5K trades, has ticker
   - Stores in `trades` table

2. **Analyzer** (`analyzer.py`)
   - Fetches stock data from Yahoo Finance (yfinance)
   - Calculates metrics: price changes (30d before/after), volatility
   - Prepares chart data (prices, volumes, dates)
   - Stores in `analyses` table with JSON chart data

3. **Database** (`database.py`)
   - **trades**: Raw trade data from scraper
   - **analyses**: Analysis results with metrics and chart data

## Database Schema

**trades**
- trade_id, politician, party, ticker, transaction_type
- traded_date, published, analyzed (boolean)

**analyses**
- trade_id, ticker, politician, party
- metrics (JSON): trade_price, change_to_trade, change_after_trade, volatility
- chart_data (JSON): dates, prices, volumes, trade_date_index

## Notes

- Background tasks run asynchronously
- Stock data cached in `stock_data_cache/`
- Charts rendered dynamically on frontend (no static files)
# Congressional Trading Analysis System

> **Developed by:** Darshan Rajopadhye (rajopadhye.d@northeastern.edu)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/therrshan)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/therrshan)

A full-stack application for tracking, analyzing, and visualizing congressional stock trades to detect potential insider trading patterns.

## Why This Matters

Members of Congress have access to non-public information that could influence stock prices. By analyzing their trading patterns and comparing stock performance before and after trades, we can:

- **Detect suspicious patterns**: Identify trades made before significant price movements
- **Increase transparency**: Make congressional trading data accessible and analyzable
- **Support accountability**: Provide data-driven insights into potential conflicts of interest
- **Monitor compliance**: Track filing delays and trade disclosure patterns

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Congressional Trading                     │
│                     Analysis System                          │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
         ┌──────▼──────┐            ┌──────▼──────┐
         │   BACKEND   │            │  FRONTEND   │
         │  (FastAPI)  │◄───────────┤   (React)   │
         └─────────────┘   REST API └─────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼────┐ ┌───▼────┐ ┌───▼────┐
│Scraper │ │Analyzer│ │Database│
│        │ │        │ │(SQLite)│
└────────┘ └────────┘ └────────┘
    │           │
    │           │
┌───▼────┐ ┌───▼────┐
│Capitol │ │ Yahoo  │
│Trades  │ │Finance │
└────────┘ └────────┘
```

## Data Flow

```
1. SCRAPING
   Capitol Trades → Scraper → Database (trades table)
   
2. ANALYSIS
   Database → Analyzer → Yahoo Finance → Calculate Metrics
   → Database (analyses table with chart_data JSON)
   
3. VISUALIZATION
   Frontend → API (GET /trades, /analyses)
   → Display tables → Expand row
   → Render charts from chart_data JSON
```

## Usage

### 1. Scrape Trades
- Click "Scrape" button in dashboard
- Scraper fetches recent trades from Capitol Trades
- Filters and stores in database
- Background task completes in ~30 seconds

### 2. Analyze Trades
- Click "Analyze" button in dashboard
- Analyzer processes unanalyzed trades
- Fetches stock data and calculates metrics
- Stores chart data as JSON
- Background task completes in ~20-30 seconds

### 3. View Results
**Trades Tab:**
- Search for specific politicians or tickers
- Filter by Buy/Sell transactions
- Click "View" to expand analysis

**Politicians Tab:**
- See all politicians sorted by trade count
- Click politician to expand their trades
- View individual trade analyses

### 4. Interpret Analysis
- **Pre-Trade Change**: Stock movement 30 days before trade
  - Positive = Stock went up before they bought (good timing)
  - Negative = Stock went down before they bought (potential opportunity)
  
- **Post-Trade Change**: Stock movement 30 days after trade
  - Positive after buy = Profitable trade
  - Negative after sell = Good exit timing
  
- **Volatility**: Price fluctuation indicator
  - High volatility = Risky stock
  - Low volatility = Stable stock

- **Charts**: Visual confirmation of timing and patterns

## Key Features

✅ **Automated Scraping**: Selenium-based scraper with filtering
✅ **Stock Analysis**: Historical price data with 30-day windows
✅ **Interactive Charts**: Dynamic rendering with Recharts
✅ **Dual Views**: Chronological trades + politician grouping
✅ **Real-time Stats**: Dashboard with success rates
✅ **Search & Filter**: Find specific trades or patterns
✅ **Background Tasks**: Non-blocking scraping and analysis
✅ **Modular Design**: Easy to extend and maintain


## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Selenium**: Web scraping automation
- **yfinance**: Yahoo Finance API wrapper
- **pandas**: Data manipulation
- **SQLite**: Lightweight database

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Chart library
- **Lucide React**: Icon library


## Performance & Scalability

- **Caching**: Stock data cached locally to reduce API calls
- **Background Tasks**: Long-running operations don't block UI
- **Pagination**: API supports limit/offset for large datasets
- **Indexing**: Database indexed on common query fields
- **Modular**: Easy to swap SQLite for PostgreSQL if needed

## Future Enhancements

- [ ] Add portfolio tracking (aggregate holdings)
- [ ] Implement anomaly detection algorithms
- [ ] Export reports to PDF/CSV
- [ ] Email alerts for suspicious patterns
- [ ] Historical trend analysis
- [ ] Comparison with market indices
- [ ] Integration with SEC filings
- [ ] User authentication and saved searches

## Legal & Ethical Considerations

This tool is designed for transparency and accountability:
- All data is publicly available from Capitol Trades
- Analysis is objective and data-driven
- No private or confidential information is accessed
- Tool supports democratic oversight of public officials

## License

MIT License - See LICENSE file for details


## Acknowledgments

- Data source: [Capitol Trades](https://www.capitoltrades.com)
- Stock data: Yahoo Finance via yfinance
- Built with modern open-source tools
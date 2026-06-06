# Congressional Trading Analysis - Frontend

React dashboard for monitoring congressional stock trades.

## Setup

```bash
npm install
npm run dev
```

App runs at `http://localhost:3000`

## Architecture

```
frontend/src/
├── App.jsx                    # Main app, state management
├── api.js                     # API calls to backend
└── components/
    ├── StatsCards.jsx         # Dashboard statistics
    ├── TradesTable.jsx        # All trades view
    ├── PoliticiansView.jsx    # Grouped by politician
    ├── PoliticianCard.jsx     # Individual politician
    ├── AnalysisDetails.jsx    # Metrics display
    └── StockChart.jsx         # Interactive charts (Recharts)
```

## Features

### Trades Tab
- View all trades chronologically
- Search by politician or ticker
- Filter by transaction type (Buy/Sell)
- Expand rows to see analysis details

### Politicians Tab
- Trades grouped by politician
- Aggregate stats per politician
- Expandable to show all trades

### Analysis Display
- Price at trade date
- Pre-trade change (30 days before)
- Post-trade change (30 days after)
- Volatility metrics
- Interactive price/volume charts

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Charts
- **Lucide React** - Icons

## Key Components

**App.jsx** - Main component with tabs, search, filters
**TradesTable.jsx** - Table with expandable analysis rows
**PoliticiansView.jsx** - Groups trades by politician
**StockChart.jsx** - Line chart (price) + bar chart (volume)
**AnalysisDetails.jsx** - Metrics cards + chart display

## API Integration

All API calls in `api.js`:
- `fetchStats()` - Dashboard stats
- `fetchTrades()` - All trades
- `fetchAnalyses()` - All analyses
- `startScrape()` - Trigger scraping
- `startAnalysis()` - Trigger analysis

## Notes

- Charts render client-side from JSON data
- Background tasks auto-refresh after 5 seconds
- Modular component structure for easy editing
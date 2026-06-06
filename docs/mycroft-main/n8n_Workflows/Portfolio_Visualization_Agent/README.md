# 🤖 AI Investment Portfolio Tracker

A real-time portfolio tracking system built with n8n that monitors AI stock investments with live prices, visualizations, and analytics.

![Portfolio Dashboard](https://img.shields.io/badge/Status-Active-success)
![n8n](https://img.shields.io/badge/n8n-Automation-blue)
## 📊 Overview

This project is an AI-powered investment portfolio tracker built entirely in n8n workflows. It fetches live stock prices, calculates gains/losses, and displays everything in a beautiful web dashboard.

**Live Features:**
- 💰 Real-time portfolio value tracking
- 📈 Gain/loss calculations with color coding
- 🥧 Interactive pie chart showing allocation
- 📋 Detailed holdings table
- 🔄 One-click refresh
- 📱 Mobile responsive design

## 🚀 Quick Start

### Prerequisites
- n8n installed (Docker, npm, or n8n Cloud)
- Basic understanding of n8n workflows

### Installation

1. **Install n8n** (choose one):
```bash
# Docker
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n

# npm
npm install n8n -g
n8n start

# Or use n8n Cloud: https://n8n.io/cloud
```

2. **Import Workflows**
   - Create two new workflows in n8n
   - Copy the workflow JSON from sections below
   - Paste into n8n

3. **Configure Portfolio**
   - Edit Workflow 1, Node 2 (Code node)
   - Update the `portfolio` array with your stocks

4. **Activate Workflow 2**
   - Toggle the "Active" switch in Workflow 2
   - Access dashboard via webhook URL

## 📁 Project Structure
```
AI Portfolio Tracker
├── Workflow 1: Portfolio Price Fetcher
│   ├── Manual Trigger
│   ├── Code (Portfolio Definition)
│   ├── HTTP Request (Fetch Prices)
│   ├── Code (Calculate Metrics)
│   └── Code (Aggregate Summary)
│
└── Workflow 2: Portfolio Dashboard
    ├── Webhook (GET /portfolio)
    ├── Execute Workflow (Run Workflow 1)
    ├── Code (Generate HTML)
    └── Respond to Webhook
```

## 🔧 Configuration

### Customize Your Portfolio

Edit the portfolio array in **Workflow 1, Node 2**:
```javascript
const portfolio = [
  { ticker: 'NVDA', shares: 50, buyPrice: 450 },
  { ticker: 'MSFT', shares: 30, buyPrice: 350 },
  { ticker: 'GOOGL', shares: 40, buyPrice: 140 },
  { ticker: 'META', shares: 25, buyPrice: 320 },
  { ticker: 'AMD', shares: 60, buyPrice: 120 }
];
```

### Change Refresh Interval

In Workflow 1, replace Manual Trigger with Schedule Trigger:
- Set to run every 1 hour for auto-updates

## 📊 Dashboard Features

### Summary Cards
- **Portfolio Value**: Current total value
- **Total Cost**: Your initial investment
- **Total Gain/Loss**: Profit/loss with percentage
- **Holdings**: Number of stocks tracked

### Visualizations
- **Pie Chart**: Portfolio allocation by stock
- **Holdings Table**: Detailed view with:
  - Ticker symbol
  - Number of shares
  - Buy price
  - Current price
  - Current value
  - Gain/Loss ($ and %)

### Status Indicator
- Green badge when portfolio is UP
- Red badge when portfolio is DOWN

## 🛠️ Technical Details

### Data Source
- **Yahoo Finance API**: Real-time stock prices
- No API key required
- Free tier with rate limits

### Technologies
- **n8n**: Workflow automation
- **JavaScript**: Data processing and calculations
- **Chart.js**: Interactive visualizations
- **HTML/CSS**: Dashboard interface

### Key Calculations

**Current Value**:
```javascript
currentValue = shares × currentPrice
```

**Gain/Loss**:
```javascript
gainLoss = currentValue - (shares × buyPrice)
gainLossPercent = (gainLoss / costBasis) × 100
```

**Portfolio Total**:
```javascript
totalValue = sum(all currentValues)
totalReturn = ((totalValue - totalCost) / totalCost) × 100
```

## 🎨 Customization

### Change Color Theme

Edit the CSS in Workflow 2, Node 3:
```css
/* Current gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Alternative themes */
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); /* Pink */
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); /* Blue */
background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); /* Green */
```

### Add More Stocks

Simply add more entries to the portfolio array:
```javascript
{ ticker: 'AAPL', shares: 100, buyPrice: 150 },
{ ticker: 'TSLA', shares: 20, buyPrice: 250 }
```

## 📈 Roadmap

### Completed ✅
- [x] Real-time price fetching
- [x] Gain/loss calculations
- [x] Portfolio visualization
- [x] Web dashboard
- [x] Mobile responsive design

### Planned 🎯
- [ ] Historical performance charts
- [ ] S&P 500 benchmark comparison
- [ ] Risk metrics (volatility, VaR, beta)
- [ ] Email/SMS alerts
- [ ] News monitoring for holdings
- [ ] Stop-loss recommendations
- [ ] Scenario simulator

## 🐛 Troubleshooting

### Dashboard shows "No Data"
**Solution**: Run Workflow 1 manually first:
1. Go to Workflow 1
2. Click "Execute Workflow"
3. Wait for completion
4. Refresh dashboard

### Webhook not working
**Solution**: Activate Workflow 2:
1. Toggle "Inactive" to "Active" at top of workflow
2. Use Production URL instead of Test URL

### Stock prices not updating
**Solution**: Yahoo Finance rate limits:
- Wait 60 seconds between refreshes
- Reduce number of stocks if hitting limits

### "Fetch is not defined" error
**Solution**: Use n8n 1.0+ or use $http.get() instead of fetch()

## 📊 Performance

- **Load Time**: 2-5 seconds
- **Data Refresh**: Real-time on page load
- **API Calls**: 5 calls per refresh (one per stock)
- **Rate Limit**: ~100 requests/hour (Yahoo Finance)

## 🔐 Security Notes

- No API keys stored (Yahoo Finance is public)
- Webhook URL is public by default
- Add authentication in n8n if needed
- Don't commit real portfolio values to public repos

## 📝 Version History

### v1.0.0 (2025-11-17)
- Initial release
- Real-time portfolio tracking
- Basic visualizations
- Web dashboard

## 🤝 Contributing

This is a personal learning project, but suggestions welcome:

1. Fork the repository
2. Create feature branch
3. Make improvements
4. Submit pull request

## 📧 Contact

- **Project**: AI Portfolio Tracker
- **Framework**: Mycroft Investment Intelligence
- **Built with**: n8n workflow automation

## 📄 License

MIT License - Feel free to use for personal projects

## 🙏 Acknowledgments

- **n8n**: For the amazing automation platform
- **Yahoo Finance**: For free stock data API
- **Chart.js**: For beautiful visualizations
- **Claude (Anthropic)**: For AI assistance in building this

---

## 📸 Screenshots

### Dashboard Overview
```
┌─────────────────────────────────────────────────────┐
│  🤖 AI Investment Portfolio                         │
│  Real-time tracking • Powered by n8n                │
├─────────────────────────────────────────────────────┤
│  Portfolio Value  │  Total Cost  │  Gain/Loss       │
│    $65,436.95    │  $53,800.00  │  +$11,636.95    │
├─────────────────────────────────────────────────────┤
│  📈 Portfolio is UP $11,636.95 (+21.63%)           │
├─────────────────────────────────────────────────────┤
│  [Pie Chart]              │  [Holdings Table]       │
│  Portfolio Allocation     │  NVDA  50  $450  $186   │
│                          │  MSFT  30  $350  $507   │
│                          │  GOOGL 40  $140  $285   │
│                          │  META  25  $320  $602   │
│                          │  AMD   60  $120  $241   │
└─────────────────────────────────────────────────────┘
```

## 🔗 Useful Links

- [n8n Documentation](https://docs.n8n.io/)
- [Yahoo Finance API](https://www.yahoofinanceapi.com/)
- [Chart.js Docs](https://www.chartjs.org/docs/)
- [Mycroft Framework](https://github.com/yourusername/mycroft-framework)

---

**Built as part of the Mycroft AI Investment Intelligence Framework**

*An educational project exploring AI-powered portfolio management*

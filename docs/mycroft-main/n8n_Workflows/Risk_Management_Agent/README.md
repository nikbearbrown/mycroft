# Mycroft Risk Management Agent

An automated AI-powered portfolio risk monitoring system built with n8n that provides institutional-grade risk analysis and actionable recommendations.

## Overview

The Mycroft Risk Management Agent is a core component of the Mycroft Framework - an open-source educational project exploring practical AI applications in investment intelligence. This agent continuously monitors portfolio positions, calculates comprehensive risk metrics, and leverages AI to provide clear, actionable risk assessments.

### Key Features

- **Automated Risk Monitoring**: Runs on schedule or on-demand to analyze portfolio positions
- **Comprehensive Risk Calculations**: Position sizing, stop-loss management, volatility analysis, and multi-factor risk scoring
- **AI-Powered Insights**: Uses Groq's Llama 3.1 to generate plain-English risk narratives and recommendations
- **Historical Logging**: Maintains timestamped audit trail of all risk assessments
- **Real-Time Data**: Integrates with Alpha Vantage for live market prices
- **Fully Customizable**: All risk parameters, scoring weights, and thresholds are configurable

## Architecture

The workflow consists of 8 connected nodes:

1. **Manual Trigger** - Initiates workflow execution (can be changed to schedule trigger)
2. **Get Portfolio from Sheets** - Reads current positions from Google Sheets
3. **Fetch Live Prices** - Retrieves real-time market data via Alpha Vantage API
4. **Calculate Advanced Risk** - Performs comprehensive risk calculations and scoring
5. **Prepare for LLM** - Structures data for AI analysis
6. **Call Groq API** - Generates AI-powered risk narratives and insights
7. **Format Report** - Combines quantitative and qualitative analysis
8. **Log to Sheets** - Appends complete risk assessments to Google Sheets

### Data Flow
```
Portfolio Data (Google Sheets) → Live Prices (Alpha Vantage) → Risk Calculations → AI Analysis (Groq/Llama) → Logging (Google Sheets)
```

## Risk Analysis Components

### Position Sizing
- **Maximum position limit**: 5% of portfolio (configurable)
- **Volatility-adjusted sizing**: Reduces max size for high-volatility stocks
- **Oversized position alerts**: Triggers warnings when limits exceeded

### Stop-Loss Management
- **Base stop-loss**: 8% below cost basis (configurable)
- **Volatility adjustment**: Wider stops for volatile stocks
- **Trailing stop**: 8% below current price
- **Multi-level alerts**: Near stop-loss and below stop-loss warnings

### Risk Scoring System

The system uses a 0-100+ point scale with multiple risk factors:

| Risk Factor | Points | Trigger Condition |
|-------------|--------|-------------------|
| Position severely oversized | 40 | >7.5% of portfolio |
| Position oversized | 20 | >5% of portfolio |
| Below stop-loss | 50 | Price < calculated stop |
| Near stop-loss | 25 | Price within 5% of stop |
| Significant loss | 30 | >15% unrealized loss |
| Moderate loss | 15 | >8% unrealized loss |
| Consider profit taking | 10 | >100% unrealized gain |
| Strong gains | 5 | >50% unrealized gain |
| High volatility | 20 | >50% annualized volatility |

### Alert Levels

- **INFO** (0-19 points): Low risk, routine monitoring
- **MONITOR** (20-39 points): Elevated risk, watch closely
- **WARNING** (40-69 points): Significant risk, consider action
- **CRITICAL** (70+ points): High risk, immediate action recommended

### Action Recommendations

- **HOLD**: Position within acceptable risk parameters
- **TRIM 25%**: Moderately oversized position
- **TRIM 50%**: Severely oversized position
- **SELL**: Stop-loss triggered or extreme risk conditions
- **EVALUATE**: Significant loss requiring review

## Prerequisites

### Required Services

1. **n8n** - Workflow automation platform (Self-hosted recommended or n8n Cloud, Version 1.0+)
2. **Google Account** - For Google Sheets integration with OAuth2 credentials
3. **Alpha Vantage API** - For market data (Free tier: 5 calls/minute, 500 calls/day) - https://www.alphavantage.co/support/#api-key
4. **Groq API** - For AI analysis (Free tier available) - https://console.groq.com/keys

### Technical Requirements

- n8n instance (local or cloud)
- Internet connection for API calls
- Google account with Sheets access
- Basic understanding of JSON and workflow concepts

## Installation & Setup

### Step 1: Clone or Download
```bash
git clone https://github.com/Humanitariansai/Mycroft.git
cd Mycroft/n8n_Workflows/Risk_Management_Agent
```

Or download the workflow JSON file directly from this repository.

### Step 2: Set Up Google Sheets

1. Create a new Google Sheet named "Mycroft Risk Portfolio"

2. Create Portfolio sheet with columns: Ticker | Shares | Avg_Cost | Portfolio_Value

   Example:
```
   NVDA    100    450    100000
   MSFT    150    380    100000
```

3. Create RiskLog sheet with headers: timestamp | ticker | risk_score | alert_level | current_price | position_value | unrealized_pl | risk_factors | action | urgency | position_percent | stop_loss_price | volatility | ai_analysis

### Step 3: Get API Keys

**Alpha Vantage:**
1. Visit https://www.alphavantage.co/support/#api-key
2. Enter your email
3. Copy the API key provided

**Groq:**
1. Visit https://console.groq.com/keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `gsk_`)

### Step 4: Configure Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable Google Sheets API
4. Create OAuth2 credentials:
   - Go to APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Application type: Web application
   - Add redirect URI: `http://localhost:5678/rest/oauth2-credential/callback`
   - Copy Client ID and Client Secret

### Step 5: Import Workflow to n8n

1. Open n8n instance
2. Click menu (three dots) → Import from File
3. Select `risk_management_agent.json`
4. Workflow loads in canvas

### Step 6: Configure Credentials

**Google Sheets OAuth2:**
1. Click "Get Portfolio from Sheets" node
2. Select Credential → Create New Credential
3. Paste Client ID and Client Secret
4. Click "Connect my account"
5. Authorize when prompted
6. Save credential
7. Use same credential for "Log to Sheets" node

**Alpha Vantage API:**
1. Click "Fetch Live Prices" node
2. Replace `YOUR_ALPHA_VANTAGE_KEY` with actual key
3. Save node

**Groq API:**
1. Click "Call Groq API" node
2. In Authorization header, replace `YOUR_GROQ_API_KEY`
3. Format: `Bearer gsk_your_key_here`
4. Save node

### Step 7: Update Google Sheet IDs

1. Open Google Sheet, copy Sheet ID from URL
2. Update both Google Sheets nodes with your Sheet ID

### Step 8: Test the Workflow

1. Click "Execute workflow"
2. Watch nodes execute
3. Check RiskLog for new entries
4. Verify data accuracy

## Usage

### Running the Workflow

**Manual Execution:**
- Click "Execute workflow" button in n8n

**Scheduled Execution:**
1. Replace Manual Trigger with Schedule Trigger
2. Configure interval (recommended: every 4 hours)
3. Activate workflow

### Maintaining Your Portfolio

Update Portfolio sheet when you:
- Buy stock: Add new row
- Sell stock: Delete row or set shares to 0
- Add to position: Update shares and recalculate avg cost
- Sell partial: Update share count

Workflow automatically adapts to changes.

### Reading Risk Assessments

Each RiskLog entry contains:
- **Timestamp**: Analysis time
- **Ticker**: Stock symbol
- **Risk_Score**: 0-100+ rating
- **Alert_Level**: INFO/MONITOR/WARNING/CRITICAL
- **Current_Price**: Latest market price
- **Position_Value**: Current holding value
- **Unrealized_PL**: Profit/loss in dollars
- **Risk_Factors**: Specific conditions identified
- **Action**: HOLD/TRIM/SELL recommendation
- **Urgency**: LOW/MEDIUM/HIGH priority
- **Position_Percent**: Portfolio allocation %
- **Stop_Loss_Price**: Calculated stop level
- **Volatility**: Annualized volatility
- **AI_Analysis**: AI narrative and insights

## Customization

### Adjust Risk Parameters

Edit "Calculate Advanced Risk" node:
```javascript
// Maximum position size (default 5%)
const maxPositionPercent = 5;

// Base stop-loss (default 8%)
const baseStopLoss = 8;

// Adjust scoring weights
if (positionPercent > maxPositionPercent * 1.5) {
  riskScore += 40;  // Modify this value
}
```

### Modify AI Prompt

Edit "Call Groq API" node content field with custom prompt

### Add Email Alerts

1. Add Gmail node after "Format Report"
2. Connect from "Check Alert Level" TRUE path
3. Configure Gmail OAuth credentials
4. Customize alert template

## Troubleshooting

### Common Issues

**Credentials not found:**
- Reconnect Google Sheets OAuth2
- Verify Groq key starts with `gsk_`
- Check Alpha Vantage key valid

**NaN values:**
- Verify column names: Ticker, Shares, Avg_Cost, Portfolio_Value
- Check node modes: "Run Once for Each Item"
- Ensure correct data types

**Only one stock processed:**
- Check Fetch Live Prices output shows all stocks
- Verify Alpha Vantage rate limit (5/minute)
- Check ticker matching logic

**Data not logging:**
- Verify RiskLog headers match field names
- Check Google credentials valid
- Ensure "Map Automatically" enabled

**Rate limits:**
- Alpha Vantage: 5/minute, 500/day
- Add delays or upgrade tier if needed

## API Rate Limits & Costs

**Alpha Vantage (Free):** 5 calls/minute, 500/day - sufficient for 10-20 positions with 4-hour monitoring

**Groq (Free):** Generous tier, Llama 3.1-8b-instant recommended, ~150-200 tokens per assessment

**Google Sheets:** Free for personal use, 500 requests/100 seconds

## Project Structure
```
Risk_Management_Agent/
├── risk_management_agent.json
├── README.md
├── docs/
│   ├── setup_guide.md
│   ├── customization_guide.md
│   └── troubleshooting.md
└── examples/
    ├── sample_portfolio.csv
    └── sample_risk_log.csv
```

## How It Works

### Risk Calculation Logic

1. Position Metrics: Current value, portfolio %, P&L
2. Volatility Analysis: Annualized from daily changes
3. Stop-Loss Levels: Base and volatility-adjusted
4. Risk Scoring: Multi-dimensional weighted score
5. Action Determination: Rule-based recommendations
6. AI Enhancement: Contextual plain-English analysis

### Example Assessment

NVDA (100 shares @ $450, current $187.62):
- Position Value: $18,762
- Portfolio %: 18.76% (exceeds 5% max)
- Unrealized P/L: -$26,238 (-58.4%)
- Risk Score: 120 (CRITICAL)
- Risk Factors: Oversized, below stop-loss, significant loss
- Recommendation: SELL - HIGH urgency
- AI: "High risk due to severely oversized position below stop-loss. Immediate action recommended."

## Roadmap

- [ ] Multi-timeframe volatility
- [ ] Correlation-based portfolio risk
- [ ] Sector concentration monitoring
- [ ] Broker API integration
- [ ] Advanced charting dashboard
- [ ] ML-based risk prediction
- [ ] Integration with other Mycroft agents

## Contributing

Educational project - contributions welcome!

Help with: risk algorithms, new metrics, AI prompts, documentation, bug fixes

Open issue or submit pull request.

## License

MIT License. See LICENSE file.

## Disclaimer

**IMPORTANT: Educational purposes only. NOT financial advice.**

- Conduct own research before investing
- Past performance ≠ future results
- Simplified models may not capture all risks
- Consult qualified financial advisor
- No liability for financial losses

## About Mycroft Framework

Open-source educational experiment in AI-powered investment intelligence. Named after Sherlock Holmes's analytical brother.

### Other Components

- Social Sentiment Agent (active)
- Portfolio Rebalancing Agent (coming soon)
- Diversification Analyzer (coming soon)
- Market Regime Detection (coming soon)

## Support & Community

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **YouTube**: Video tutorials
- **Docs**: Full guides in /docs

## Acknowledgments

Built with:
- [n8n](https://n8n.io/) - Workflow automation
- [Alpha Vantage](https://www.alphavantage.co/) - Market data
- [Groq](https://groq.com/) - AI inference
- [Google Sheets](https://sheets.google.com/) - Data management

## Contact

Open GitHub issue for questions, suggestions, or collaboration.

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: Active Development

---

## Quick Start

1. Clone repository
2. Create Google Sheet (Portfolio + RiskLog tabs)
3. Get API keys (Alpha Vantage, Groq, Google OAuth)
4. Import workflow JSON to n8n
5. Configure credentials
6. Execute workflow
7. Review RiskLog

**Setup time**: 30-45 minutes

See docs/setup_guide.md for details.

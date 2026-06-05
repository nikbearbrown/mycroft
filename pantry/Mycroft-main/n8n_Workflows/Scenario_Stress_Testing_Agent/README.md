# Mycroft Scenario Stress Testing Agent

> **Using AI to Invest in AI - Building to Learn**

An industry-ready n8n workflow that stress tests AI investment portfolios by simulating market shocks and identifying vulnerabilities before they materialize.

![n8n](https://img.shields.io/badge/n8n-workflow-orange)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Status](https://img.shields.io/badge/Status-Production--Ready-green)

## 🎯 What This Does

<img width="475" height="177" alt="image" src="https://github.com/user-attachments/assets/2e1e3a94-4deb-4d17-a3c8-b224220dc76e" />


The Stress Testing Agent answers: **"What happens to my portfolio if...?"**

- Simulates tech crashes, rate hikes, AI regulations, supply shocks
- Tests portfolios against 5 predefined scenarios
- **Natural language custom scenarios** - describe any market event
- Real-time stock data via Alpha Vantage API
- AI-powered scenario interpretation using Groq LLM

### Example

**Input:**
```json
{
  "portfolio": {
    "holdings": [
      {"ticker": "NVDA", "weight": 0.4},
      {"ticker": "MSFT", "weight": 0.3},
      {"ticker": "AMD", "weight": 0.3}
    ]
  },
  "custom_scenario": "China announces 3nm chip breakthrough threatening Nvidia"
}
```

**Output:**
```json
{
  "success": true,
  "data": {
    "scenario_name": "China 3nm Chip Breakthrough",
    "drawdown_pct": -35.2,
    "risk_level": "HIGH",
    "top_losers": [
      {"ticker": "NVDA", "loss": -1800, "shock_pct": -45},
      {"ticker": "AMD", "loss": -1200, "shock_pct": -40}
    ]
  }
}
```

---

## 🚀 Quick Start

### Prerequisites

- [n8n](https://n8n.io/) (v1.21.0+)
- [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key) (free)
- [Groq API Key](https://console.groq.com/) (free)
- Python 3.9+ (for n8n Python nodes)

### Installation

1. **Import the workflow:**
   ```bash
   # Download the JSON file
   # In n8n: Workflows → Import from File → Select JSON
   ```

2. **Configure API credentials:**
   
   **Alpha Vantage:**
   - In n8n: Settings → Credentials → Add Credential
   - Type: Generic Credential Type
   - Name: `Alpha Vantage API`
   - Add field: `apiKey` = YOUR_API_KEY

   **Groq:**
   - In n8n: Settings → Credentials → Add Credential
   - Type: Groq
   - API Key: YOUR_GROQ_API_KEY

3. **Update credential references in workflow:**
   - Click on "Groq Chat Model" node
   - Select your Groq credentials from dropdown
   - Click on "Fetch_Data" node
   - Update Alpha Vantage API key in parameters

4. **Activate the workflow:**
   - Toggle "Active" at the top right
   - Note your webhook URL

---

## 📖 Usage

### Template Scenarios

Test against 5 predefined scenarios:

```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {
      "holdings": [
        {"ticker": "NVDA", "weight": 0.5},
        {"ticker": "MSFT", "weight": 0.5}
      ]
    },
    "scenario_type": "tech_crash"
  }'
```

**Available scenarios:**
- `tech_crash` - Major tech selloff (regulatory/macro)
- `rate_hike` - Aggressive Fed rate increase
- `ai_regulation` - New AI safety regulations
- `chip_shortage` - Semiconductor supply shock
- `black_swan` - Extreme tail-risk event

### Custom Scenarios (Natural Language)

Describe any scenario in plain English:

```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio": {
      "holdings": [
        {"ticker": "NVDA", "weight": 0.4},
        {"ticker": "AMD", "weight": 0.3},
        {"ticker": "MSFT", "weight": 0.3}
      ]
    },
    "custom_scenario": "EU announces strict AI liability law increasing costs for AI deployers"
  }'
```

The LLM will interpret your scenario and generate appropriate market shocks!

---

## 🏗️ Architecture

```
Webhook → Parse Input → Validate Portfolio → Fetch Market Data → Merge
                                                                    ↓
                                                            Custom Scenario?
                                                            ↙              ↘
                                               (TRUE)                      (FALSE)
                                                 ↓                           ↓
                                    Save Portfolio → LLM Parse      Load Template
                                                 ↓                           ↓
                                           Parse Response ← ← ← ← ← ← ← ← ← ←
                                                 ↓
                                            Merge Scenarios
                                                 ↓
                                         Stress Test Engine
                                                 ↓
                                          Respond to Webhook
```

### Key Components

**Data Collection:**
- **Fetch Market Data**: Alpha Vantage API for real-time stock prices
- **Merge**: Combines portfolio + market data

**Scenario Generation:**
- **Custom Scenario? (IF)**: Routes to template or LLM
- **Load Template Scenario**: 5 predefined stress scenarios
- **Save Portfolio Before LLM**: Preserves portfolio through LLM processing
- **Groq Chat Model + Basic LLM Chain**: AI interprets natural language scenarios
- **Parse LLM Response**: Extracts JSON from LLM output

**Stress Calculation:**
- **Stress Test Engine**: Applies compound shocks (market + sector + category)
- **Respond to Webhook**: Returns JSON results

---

## 🧪 How It Works

### Shock Calculation

The engine applies **compound shocks** across multiple dimensions:

**For NVDA in "Tech Crash" scenario:**
```
Market shock:        -15%
Semiconductor:       -35%
AI stocks:           -40%
━━━━━━━━━━━━━━━━━━━━━━━━
Total impact:        -90%
```

**Shock categories:**
- `market` - Overall market movement
- `tech_sector` - Technology sector
- `semiconductor` - Chip manufacturers
- `ai_stocks` - AI-focused companies
- `big_tech` - FAANG companies
- `growth_stocks` - High-growth stocks

### Risk Levels

- **LOW** (<10% drawdown)
- **MODERATE** (10-20% drawdown)
- **HIGH** (20-30% drawdown)
- **CRITICAL** (>30% drawdown)

---

## 📊 Example Scenarios

### 1. Tech Crash
```json
{
  "scenario_type": "tech_crash"
}
```
**Result:** -72.5% drawdown on NVDA-heavy portfolio

### 2. China Chip Breakthrough
```json
{
  "custom_scenario": "China announces 3nm chip manufacturing breakthrough"
}
```
**Result:** LLM generates semiconductor-focused shocks

### 3. AI Regulation
```json
{
  "scenario_type": "ai_regulation"
}
```
**Result:** -25% on AI stocks, -15% on big tech

---

## 🛠️ Customization

### Add New Template Scenarios

Edit the **Load_Template_Scenario** node:

```python
scenarios = {
    'your_scenario': {
        'name': 'Your Scenario Name',
        'description': 'What happens in this scenario',
        'shocks': {
            'market': -0.10,
            'sector_name': -0.20,
            'volatility_spike': 2.0
        }
    }
}
```

### Adjust Shock Calculation

Edit the **Stress_Test_Engine** node to change how shocks stack:

**Current (Additive):**
```python
total_shock = market + sector + category  # Can exceed 100%
```

**Alternative (Maximum):**
```python
total_shock = max(market, sector, category)  # Capped at worst shock
```

### Add More Stocks to Sector Map

Edit sector_map in **Stress_Test_Engine**:

```python
sector_map = {
    'NVDA': 'semiconductor',
    'YOUR_TICKER': 'your_sector',
}
```

---

## 🐛 Troubleshooting

### Alpha Vantage Rate Limit

**Error:** "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute"

**Solution:** Add delays or upgrade to premium ($50/month unlimited)

### Portfolio Not Found

**Error:** "Portfolio not found"

**Cause:** Data not passing through LLM nodes correctly

**Solution:** Verify "Save Portfolio Before LLM" node is connected to both:
1. Basic LLM Chain (for scenario)
2. Parse_LLM_Response (for portfolio retrieval)

### LLM Returns Invalid JSON

**Error:** JSON parsing fails in Parse_LLM_Response

**Solution:** Code already handles this with fallback scenario. Check Groq API key is valid.

---

## 👥 Contributors

Built with ❤️ by the Mycroft community

Special thanks to:
- Professor Nik Bear Brown, PhD, MBA - Project Vision
- Anshika Khandelwal - Implementation & Testing - 
- Anshika Khandelwal - Linkedin- https://www.linkedin.com/in/anshika-khandelwal/

---

**⚠️ Disclaimer**

This tool is for educational and research purposes only. Not financial advice. Always consult with qualified financial professionals before making investment decisions. Past performance and simulated stress tests do not guarantee future results.

---

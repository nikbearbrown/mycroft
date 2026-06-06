# Market Sentiment Analysis Workflow (Part 1)

## 💡 The Idea

An automated market intelligence agent that answers user questions about stock sentiment in real-time. Ask "What's the sentiment on NVDA?" and get a comprehensive analysis combining price data, news headlines, and social media buzz—delivered in seconds.

## 🔄 How It Works

```
User Question → Extract Ticker → Fetch Multi-Source Data → Calculate Sentiment → AI Analysis → Deliver Report
```

**Data Sources:**
- **Price Data:** Real-time prices, volume, changes (Alpha Vantage)
- **News Sentiment:** Recent headlines and analysis (Finnhub)
- **Social Sentiment:** Reddit mentions and community mood (r/wallstreetbets)

**AI Synthesis:** Claude analyzes all data to provide context, identify drivers, and highlight risks/opportunities.

**Delivery:** Results sent via Slack, email, or webhook response.

## 📋 Requirements

### APIs (Free Tiers Available)
- **Alpha Vantage API Key** - [Get it here](https://www.alphavantage.co/support/#api-key)
- **Finnhub API Key** - [Get it here](https://finnhub.io/register)
- **Anthropic API Key** - For Claude AI analysis

### n8n Setup
- n8n instance (self-hosted or cloud)
- Optional: Slack workspace + bot token
- Optional: SMTP email credentials

### Installation
1. Import JSON workflow into n8n
2. Replace API key placeholders in HTTP Request nodes
3. Configure Slack/Email credentials (or disable those nodes)
4. Activate workflow

## 🚀 Usage

**Webhook Endpoint:**
```bash
POST https://your-n8n-instance.com/webhook/market-sentiment
Content-Type: application/json

{
  "question": "What's the sentiment on NVDA?",
  "email": "user@example.com"
}
```

**Supported Question Formats:**
- "What's the sentiment on TSLA?"
- "Why is Bitcoin crashing?"
- "Should I buy AAPL?"
- "How's the market looking for $MSFT?"

## 📊 Sample Output

**Slack/Email Report:**

```
📊 NVDA Market Sentiment Analysis
Updated: February 17, 2026 at 2:34 PM EST

OVERALL SENTIMENT: ⬆️ BULLISH (74/100)

Current Price: $892.45 (+2.3%)

---

NVIDIA sentiment remains strongly bullish driven by continued AI chip 
demand narrative. Social media activity has surged 40% with predominantly 
positive mentions across Reddit communities. Three analyst upgrades this 
week have reinforced institutional confidence, while unusual options 
activity suggests large buyers positioning for upside.

Key drivers include sustained AI infrastructure spending and new data 
center partnerships announced today. However, some profit-taking pressure 
is evident near the $900 resistance level, with valuation concerns 
emerging in technical forums.

Bottom Line: Bullish sentiment across retail and institutional channels, 
supported by fundamental catalysts. Watch for potential consolidation at 
current levels.

---

📈 Sentiment Breakdown:
• News: 78/100 (12 pos, 3 neg)
• Social: 72/100 (35 bullish, 8 bearish)
• Price Action: 70/100

⚠️ Disclaimer: This analysis is for informational purposes only and 
not financial advice. Always do your own research before making 
investment decisions.

Sources: Alpha Vantage, Finnhub News, Reddit
```

## 🎯 Key Features

- ✅ Automatic ticker symbol extraction
- ✅ Multi-source sentiment aggregation (weighted algorithm)
- ✅ AI-powered context and explanation
- ✅ Real-time price and volume analysis
- ✅ News headline scanning
- ✅ Social media sentiment tracking
- ✅ Professional formatted reports
- ✅ Multiple delivery channels

## ⚙️ Customization

**Adjust sentiment weights** in "Aggregate & Calculate Sentiment" node:
```javascript
// Default: 40% price, 30% news, 30% social
const overallSentiment = 
  priceSentimentScore * 0.4 + 
  newsSentimentScore * 0.3 + 
  redditSentimentScore * 0.3;
```

**Add more keywords** for sentiment detection:
- Modify `positiveWords` and `negativeWords` arrays
- Add Twitter API for additional social data
- Include technical indicators (RSI, MACD)

## 🔄 What's Next?

**Part 2** adds AEO (Answer Engine Optimization) to automatically generate and publish SEO-optimized articles from your sentiment analysis, turning private intelligence into public content that ranks in search engines.

---

**Need Help?** Check the n8n community forum or open an issue.
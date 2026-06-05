# Portfolio Intelligence Agent with RAG - Complete Documentation

## 📊 Overview

The **Portfolio Intelligence Agent** is an automated n8n workflow that tracks an AI-focused investment portfolio, calculates performance metrics, uses RAG (Retrieval-Augmented Generation) for context-aware analysis, and generates daily AI-powered insights. Built as part of the Mycroft Investment Intelligence Framework, this agent embodies the philosophy of "Using AI to Invest in AI" while serving as an educational tool for learning portfolio management principles.

---

## 🎯 What It Does

The Portfolio Intelligence Agent automatically:

- **Fetches live stock prices** from Yahoo Finance API
- **Calculates portfolio value** and position weights
- **Analyzes historical patterns** from past performance data
- **Retrieves relevant context** using RAG from knowledge base
- **Generates AI-powered analysis** using Groq's Llama 3.3 70B
- **Learns continuously** by extracting insights and updating knowledge base
- **Stores historical data** in CSV files for pattern analysis
- **Sends daily HTML email reports** with context-aware insights

**Schedule:** Runs automatically Monday–Friday at 5:00 PM (after market close)

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Workflow Engine** | n8n | Orchestrates automation |
| **Data Storage** | CSV Files | Portfolio history & summaries |
| **Market Data** | Yahoo Finance API | Live stock prices (free) |
| **AI Analysis** | Groq (Llama 3.3 70B) | Portfolio insights generation |
| **RAG System** | Custom knowledge base | Context retrieval |
| **Notifications** | Gmail SMTP | Daily email reports |

### Data Flow
```
[Schedule Trigger] → [Read Holdings] → [Fetch Prices] → [Calculate Metrics]
    ↓
[Load History] → [Build Analysis] → [Calculate Returns]
    ↓
[Extract Learnings] → [Update Knowledge Base]
    ↓
[RAG: Retrieve Context] → [Generate AI Summary (Groq)]
    ↓
[Save to CSV Files] → [Send Email Report]
```

---

## 📁 Project Structure
```
mycroft-portfolio/
├── data/
│   ├── holdings.json              # Your stock holdings
│   ├── portfolio_history.csv      # Daily position-level data
│   ├── daily_summaries.csv        # Daily portfolio summaries
│   └── knowledge_base.csv         # RAG memory (auto-growing)
└── reports/                       # (Optional) For exports
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **n8n installed** (Docker or npm)
- **Terminal/Command line access**
- **Groq API key** (free from console.groq.com)
- **Gmail account** with App Password or OAuth2

### Installation Steps

#### 1️⃣ Create Project Directory
```bash
mkdir -p ~/mycroft-portfolio/data
cd ~/mycroft-portfolio/data
```

#### 2️⃣ Create Data Files

**holdings.json:**
```json
[
  { "ticker": "NVDA", "quantity": 10, "sector": "Semiconductors" },
  { "ticker": "MSFT", "quantity": 15, "sector": "Cloud Infrastructure" },
  { "ticker": "GOOGL", "quantity": 8, "sector": "ML Infrastructure" },
  { "ticker": "AMD", "quantity": 12, "sector": "Semiconductors" },
  { "ticker": "META", "quantity": 6, "sector": "Foundation Models" }
]
```

**portfolio_history.csv:**
```csv
date,ticker,quantity,price,value,weight,sector
```

**daily_summaries.csv:**
```csv
date,total_value,daily_return,top_holding,top_holding_weight,ai_summary
```

**knowledge_base.csv:**
```csv
id,date,category,content,relevance_score
1,2024-12-15,pattern,"When NVDA drops more than 3%, portfolio typically recovers within 5 trading days",high
2,2024-12-15,risk_tolerance,"User is comfortable with 10-15% drawdowns, becomes concerned above 15% threshold",high
3,2024-12-15,sector_insight,"Semiconductor sector represents significant portfolio weight, showing 2x volatility versus total market",high
4,2024-12-16,observation,"Microsoft weight drifting upward, user considering rebalancing at 40% threshold",high
5,2024-12-16,user_preference,"User prefers educational insights focused on risk management and learning opportunities",high
6,2024-12-17,market_pattern,"AI stocks demonstrate high correlation, diversification within AI sector provides limited risk reduction",high
7,2024-12-18,recovery_pattern,"V-shaped recoveries occur 70% of time, U-shaped recoveries 30% based on historical data",medium
8,2024-12-19,concentration_risk,"Single position exceeding 35% triggers rebalancing consideration",high
```

#### 3️⃣ Import n8n Workflow

1. Open n8n at `http://localhost:5678`
2. Click **"Import from File"**
3. Select `portfolio-intelligence-agent-rag.json`
4. Workflow loads with all 20 nodes

#### 4️⃣ Configure Workflow

**Update file paths** (6 locations):

| Node | Parameter | Update To |
|------|-----------|-----------|
| Read Holdings File | File Path | `/Users/YOUR_USERNAME/mycroft-portfolio/data/holdings.json` |
| Read Previous Summaries | File Path | `/Users/YOUR_USERNAME/mycroft-portfolio/data/daily_summaries.csv` |
| Read Knowledge Base | File Path | `/Users/YOUR_USERNAME/mycroft-portfolio/data/knowledge_base.csv` |
| Read Portfolio History | File Path | `/Users/YOUR_USERNAME/mycroft-portfolio/data/portfolio_history.csv` |
| Append Portfolio History | File Name | `/Users/YOUR_USERNAME/mycroft-portfolio/data/portfolio_history.csv` |
| Append Daily Summary | File Name | `/Users/YOUR_USERNAME/mycroft-portfolio/data/daily_summaries.csv` |

**Add Groq API key:**
- Node: "Generate AI Summary (Groq)"
- Header: `Authorization` → `Bearer YOUR_GROQ_API_KEY`
- Get free key at: https://console.groq.com/keys

**Configure email:**
- Node: "Send Email Report"
- Set up Gmail App Password or OAuth2

#### 5️⃣ Test the Workflow

1. Click **"Execute Workflow"** button
2. Watch nodes turn green (~30 seconds)
3. Verify:
   - ✅ CSV files updated
   - ✅ Email report arrives
   - ✅ No error nodes

---

## 🧠 RAG (Retrieval-Augmented Generation) System

### What is RAG?

RAG enhances AI responses by retrieving relevant historical context before generating analysis.

**Without RAG:**
> "Your portfolio is worth $17,903. MSFT is 38.5% of holdings."

**With RAG:**
> "Your portfolio is worth $17,903. Microsoft represents 38.5% of holdings, approaching your stated 40% rebalancing threshold. Based on historical patterns, when concentration exceeds 35%, you've previously considered trimming positions to manage risk."

### How RAG Works in This Agent
```
1. Portfolio state analyzed
    ↓
2. Knowledge base searched for relevant insights
    ↓
3. Top 5-7 insights retrieved based on:
   - Concentration risk triggers
   - Large price movements
   - User preferences
   - Historical patterns
    ↓
4. Retrieved context + portfolio data sent to AI
    ↓
5. AI generates context-aware analysis
    ↓
6. New insights extracted and added to knowledge base
```

### Knowledge Base Auto-Learning

The agent **learns and improves over time:**

- **Detects patterns:** "Portfolio gained 3 consecutive days"
- **Identifies risks:** "MSFT concentration at 39.6%"
- **Extracts insights:** From AI's daily analyses
- **Stores learnings:** Appends to knowledge_base.csv
- **Grows smarter:** More data = better context = richer analysis

**Timeline:**
- **Week 1:** 8 seed insights
- **Week 4:** 20+ accumulated insights
- **Week 12:** 50+ personalized portfolio patterns

### RAG Retrieval Rules

**Context retrieval triggers:**
- Large price movements (>2%)
- Concentration risk (position >35%)
- Drawdowns (negative returns)
- Sector concentration (>40%)
- Top holding changes

**Relevance scoring:**
- Base: High = +3, Medium = +2, Low = +1
- Pattern match = +5
- Concentration match = +5
- Ticker mention = +3
- Recovery context = +4
- User preference = +2

**Top 5-7 highest-scored insights are retrieved for each analysis**

---

## 📊 Data Schema

### holdings.json
```json
{
  "ticker": "string",      // Stock symbol
  "quantity": number,      // Shares owned
  "sector": "string"       // AI sector classification
}
```

### portfolio_history.csv

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Trading date (YYYY-MM-DD) |
| ticker | STRING | Stock symbol |
| quantity | DECIMAL | Number of shares |
| price | DECIMAL | Stock price |
| value | DECIMAL | Position value (quantity × price) |
| weight | DECIMAL | Portfolio weight (0.0000-1.0000) |
| sector | STRING | AI sector classification |

### daily_summaries.csv

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Trading date |
| total_value | DECIMAL | Total portfolio value |
| daily_return | DECIMAL | Return vs previous day |
| top_holding | STRING | Largest position ticker |
| top_holding_weight | DECIMAL | Top position weight |
| ai_summary | TEXT | AI analysis (quoted, comma-safe) |

### knowledge_base.csv

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Unique identifier (timestamp-based) |
| date | DATE | When insight was created |
| category | STRING | pattern, observation, risk_tolerance, etc. |
| content | TEXT | The insight content |
| relevance_score | STRING | high, medium, or low |

---

## 🔧 Workflow Components

### Complete Node List (20 Nodes)

#### **Trigger Nodes (2)**
1. Manual Trigger - For testing/one-time runs
2. Schedule Trigger - Automated daily execution (5 PM weekdays)

#### **Data Collection (6)**
3. Read Holdings File - Load portfolio composition
4. Parse JSON Holdings - Convert to workable format
5. Fetch All Prices & Calculate - Yahoo Finance API calls
6. Calculate Portfolio Metrics - Values, weights, sectors
7. Read Portfolio History - Load historical data
8. Parse Portfolio History - Convert CSV to JSON

#### **Performance Analysis (3)**
9. Build Portfolio Analysis - Historical comparisons
10. Read Previous Summaries - Load past daily data
11. Parse Summaries & Calculate Return - Daily return computation

#### **RAG System (3)**
12. Read Knowledge Base - Load insights
13. Parse Knowledge Base - CSV to JSON
14. RAG - Retrieve Context - Intelligent context retrieval

#### **AI Generation (2)**
15. Generate AI Summary (Groq) - LLM API call
16. Extract AI Summary - Parse AI response

#### **Data Storage (4)**
17. Split Holdings for History - Separate positions
18. Convert Holdings to CSV - Format for writing
19. Append Portfolio History - Save position data
20. Convert Summary to CSV - Format summary
21. Append Daily Summary - Save portfolio summary

#### **Reporting (1)**
22. Send Email Report - Gmail delivery

---

## 📧 Email Report Format

### Sample Email

**Subject:** Mycroft Portfolio Report - 2026-01-18

**Body:**
```
📊 Portfolio Intelligence Report
January 18, 2026

PORTFOLIO VALUE
$17,903.66

DAILY RETURN
+0.00%

TOP HOLDING
MSFT
38.5% of portfolio

🤖 AI Analysis

- Your AI-focused portfolio is valued at $17,903.66, with Microsoft 
  representing 38.5% of total holdings, approaching the 40% 
  rebalancing threshold identified in your risk management guidelines.

- The semiconductor sector (NVIDIA + AMD) comprises 25.9% of your 
  portfolio, demonstrating the sector concentration typical of 
  AI-heavy allocations. Based on historical insights, this sector 
  shows 2x volatility versus the broader market.

- Cloud Infrastructure exposure through Microsoft provides stability 
  but creates concentration risk. Historical patterns suggest 
  single positions exceeding 35% warrant rebalancing consideration.

- Educational insight: Portfolio diversification within a single 
  sector (AI) provides limited risk reduction due to high correlation. 
  Consider broader sector diversification to reduce volatility.

🧠 Enhanced with 5 historical insights

---
Mycroft Investment Intelligence Framework
RAG-Enhanced AI Portfolio Analysis
Using AI to Invest in AI: Building and Learning Together
```

---

## 🎓 Current Portfolio Composition

| Ticker | Shares | Sector | Approx. Weight |
|--------|--------|--------|----------------|
| **NVDA** | 10 | Semiconductors | ~11% |
| **MSFT** | 15 | Cloud Infrastructure | ~39% |
| **GOOGL** | 8 | ML Infrastructure | ~14% |
| **AMD** | 12 | Semiconductors | ~15% |
| **META** | 6 | Foundation Models | ~21% |

**Total Portfolio Value:** ~$17,900 (varies with market prices)

### Sector Breakdown
- **Cloud Infrastructure:** 39% (MSFT dominance - concentration risk!)
- **Semiconductors:** 26% (NVDA + AMD combined)
- **Foundation Models:** 21% (META)
- **ML Infrastructure:** 14% (GOOGL)

---

## 📈 Metrics Tracked

### Currently Implemented ✅
- Daily portfolio value
- Daily return percentage
- Position weights (% of total portfolio)
- Top holdings identification
- Sector concentration analysis
- Historical pattern detection
- RAG context retrieval (5-7 insights per day)
- Auto-learning (extracts 2-4 insights daily)

### Planned Enhancements 🔄
- Rolling 7-day and 30-day returns
- Volatility analysis (standard deviation)
- Maximum drawdown tracking
- Automated risk alerts (email when thresholds exceeded)
- Benchmark comparison (vs QQQ, SPY)
- Rebalancing recommendations

---

## 🛠️ Customization Guide

### Change Your Holdings

Edit `data/holdings.json`:
```json
[
  { "ticker": "YOUR_TICKER", "quantity": YOUR_SHARES, "sector": "YOUR_SECTOR" }
]
```

**Supported:** Any US stock available on Yahoo Finance

### Adjust Schedule

Edit **Schedule Trigger** node cron expression:
- **Current:** `0 17 * * 1-5` (5 PM weekdays)
- **Examples:**
  - `0 9 * * 1-5` - 9 AM weekdays
  - `0 16 * * *` - 4 PM every day
  - `0 12 * * 6,0` - Noon weekends

### Customize AI Analysis

Edit **Generate AI Summary (Groq)** node prompt to:
- Focus on specific metrics (volatility, drawdowns)
- Change analysis tone (formal/casual/technical)
- Add custom questions ("Compare to last week")
- Request different output format

### Modify Email Design

Edit **Send Email Report** HTML to:
- Change color scheme
- Add/remove metric sections
- Include additional data tables
- Customize branding/footer

---

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **"File not found"** | Incorrect file path | Verify paths match your username |
| **"Yahoo Finance 404"** | Invalid ticker | Check ticker symbols on finance.yahoo.com |
| **"Groq API error"** | Invalid/missing API key | Verify key at console.groq.com |
| **"Email not sending"** | Missing credentials | Set up Gmail App Password |
| **"Daily return always 0"** | First run, no previous data | Expected - will show real % on day 2 |
| **"Empty email values"** | Wrong node connection | Connect email from Extract AI Summary |
| **"Knowledge base empty"** | No seed data | Create knowledge_base.csv with sample insights |
| **"Cannot find module 'fs'"** | Using fs in Code node | Use Convert to File + Write Binary File instead |

### Debug Steps

1. **Execute nodes individually** - Click each node, find failure point
2. **Check execution logs** - View detailed error messages in Executions tab
3. **Verify file permissions** - Ensure n8n can read/write to data folder
4. **Test API keys** - Confirm Groq and email credentials are valid
5. **Check console output** - Review logs for each node execution

---

## 🔒 Security Best Practices

### API Key Management
- ✅ Never commit API keys to version control
- ✅ Use n8n's credential system (encrypted storage)
- ✅ Rotate keys periodically (every 90 days)
- ✅ Use separate keys for development/production

### Data Privacy
- ✅ CSV files contain personal financial data
- ✅ Keep `mycroft-portfolio/` folder private (chmod 700)
- ✅ Don't share screenshots with real portfolio values
- ✅ Use `.gitignore` if committing to git

**Example `.gitignore`:**
```
data/*.csv
data/holdings.json
*.env
.credentials
```

---

## 📊 Viewing & Analyzing Data

### Command Line
```bash
# View latest summary
tail -1 ~/mycroft-portfolio/data/daily_summaries.csv

# View last 10 portfolio entries
tail -10 ~/mycroft-portfolio/data/portfolio_history.csv

# View knowledge base growth
wc -l ~/mycroft-portfolio/data/knowledge_base.csv

# Check today's holdings
tail -5 ~/mycroft-portfolio/data/portfolio_history.csv
```

### Excel / Google Sheets

1. Open application
2. File → Import/Open
3. Select CSV file
4. Create pivot tables, charts, analysis

### Python Analysis
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
history = pd.read_csv('data/portfolio_history.csv')
summaries = pd.read_csv('data/daily_summaries.csv')

# Calculate cumulative return
summaries['cumulative_return'] = (
    (summaries['total_value'] / summaries['total_value'].iloc[0]) - 1
) * 100

# Plot portfolio value over time
summaries.plot(x='date', y='total_value', 
               title='Portfolio Value Over Time')
plt.show()

# Analyze sector weights
sector_exposure = history.groupby(['date', 'sector'])['weight'].sum()
sector_exposure.unstack().plot(kind='area', stacked=True)
plt.show()
```

---

## 🧠 RAG System Details

### What is RAG?

**Retrieval-Augmented Generation** enhances AI responses by retrieving relevant historical context before generating new content.

**Example Comparison:**

**Traditional AI (No RAG):**
> "Your portfolio is worth $17,903. Daily return: 0%. Microsoft is your top holding."

**RAG-Enhanced AI:**
> "Your portfolio is worth $17,903. Microsoft represents 38.5% of holdings, approaching your stated 40% rebalancing threshold based on risk tolerance preferences in the knowledge base. Historical patterns show positions above 35% warrant consideration for trimming. Your semiconductor exposure (25.9%) shows typical 2x market volatility."

### RAG Workflow
```
Current Portfolio State
    ↓
Knowledge Base Search
    ↓
Relevance Scoring Algorithm
    ↓
Top 5-7 Insights Retrieved
    ↓
Context + Data → AI Model
    ↓
Context-Aware Analysis Generated
    ↓
New Insights Extracted
    ↓
Knowledge Base Updated
```

### RAG Components

**1. Knowledge Base (Storage)**
- CSV file with insights
- Categories: pattern, observation, risk_tolerance, etc.
- Relevance scores: high, medium, low
- Auto-grows with each run

**2. Retrieval Engine (Search)**
- Analyzes current portfolio state
- Scores each knowledge entry for relevance
- Returns top matches

**3. Context Integration (Augmentation)**
- Combines retrieved insights with current data
- Formats for AI model consumption

**4. Auto-Learning (Feedback Loop)**
- Parses AI output for new insights
- Categorizes learnings
- Appends to knowledge base

---

## 🎓 Educational Philosophy

### Learning by Building

This agent teaches through practical implementation:

**Portfolio Management Concepts:**
- Diversification and concentration risk
- Sector exposure analysis
- Daily return calculations
- Position weighting
- Risk tolerance frameworks

**AI/ML Techniques:**
- RAG system architecture
- Knowledge base design
- Context retrieval algorithms
- LLM prompt engineering
- Auto-learning systems

**Software Engineering:**
- Workflow automation (n8n)
- API integration patterns
- Data processing pipelines
- Error handling strategies
- Production deployment

### Learning Outcomes

**After using this agent, you'll understand:**

#### Technical Skills
✅ **Workflow Automation** - n8n orchestration and scheduling
✅ **API Integration** - REST APIs, authentication, rate limiting
✅ **Data Engineering** - CSV processing, data transformations
✅ **RAG Implementation** - Retrieval systems, context management
✅ **LLM Integration** - Prompt design, response parsing

#### Finance Skills
✅ **Portfolio Management** - Allocation, diversification, rebalancing
✅ **Risk Analysis** - Concentration, volatility, drawdowns
✅ **Performance Tracking** - Returns, benchmarking
✅ **Sector Analysis** - Exposure, correlation patterns

#### AI/ML Concepts
✅ **RAG Systems** - How retrieval augments generation
✅ **Knowledge Graphs** - Building structured AI memory
✅ **Prompt Engineering** - Effective LLM communication
✅ **Auto-Learning** - Systems that improve themselves

---

## 🚀 Week-by-Week Progress

### After 1 Week (5 trading days)
- ✅ 5 days of portfolio snapshots
- ✅ Daily return tracking operational
- ✅ Knowledge base: 12-15 entries
- ✅ RAG retrieving relevant context
- ✅ Email reports arriving daily
- ✅ Basic patterns emerging

### After 1 Month (20 trading days)
- ✅ 20+ days of rich historical data
- ✅ Clear performance trends visible
- ✅ Knowledge base: 30-40 insights
- ✅ RAG providing highly targeted context
- ✅ Understanding portfolio volatility
- ✅ Concentration patterns identified

### After 3 Months (60 trading days)
- ✅ 60+ days comprehensive dataset
- ✅ Volatility cycles mapped
- ✅ Drawdown/recovery patterns clear
- ✅ Knowledge base: 70-100+ insights
- ✅ Personalized portfolio playbook
- ✅ Deep behavioral understanding

---

## 🏆 What You've Built

### A Production-Quality AI System

**Features:**
- ✅ Real-time market data integration
- ✅ Historical pattern recognition
- ✅ Intelligent context retrieval (RAG)
- ✅ AI-powered educational analysis
- ✅ Automated daily reporting
- ✅ Continuous self-improvement
- ✅ Email delivery system
- ✅ Data persistence layer

### Demonstrates Professional Skills

**Technical Capabilities:**
- Full-stack workflow automation
- Multi-API orchestration
- Data engineering pipelines
- RAG system implementation
- Production error handling

**Domain Expertise:**
- Financial data processing
- Portfolio analytics
- Risk management frameworks
- Investment decision support

---

## 💼 Portfolio/Resume Value

### Project Description

> "Built a RAG-enhanced AI portfolio intelligence agent using n8n, Groq LLM (Llama 3.3 70B), and custom knowledge base implementation. The system automatically tracks an AI-focused stock portfolio worth ~$18K, performs daily market analysis, uses retrieval-augmented generation to provide context-aware insights, and implements auto-learning to improve recommendations over time. Demonstrates full-stack AI engineering: workflow automation, API integration, RAG architecture, prompt engineering, and educational AI system design."

### Keywords/Technologies

**Core Technologies:**
- n8n (Workflow Automation)
- Groq API (LLM Integration)
- RAG (Retrieval-Augmented Generation)
- Yahoo Finance API
- CSV Data Processing
- SMTP/Gmail Integration

**Concepts Demonstrated:**
- Knowledge Base Design
- Context Retrieval Algorithms
- Auto-Learning Systems
- Educational AI
- Financial Data Engineering
- Production Automation

**Applicable to Roles:**
- AI/ML Engineer
- Data Engineer
- Automation Engineer
- Full-Stack Developer
- FinTech Developer

---

## 🎯 Alignment with Mycroft Framework

### Core Principles Embodied

**"Using AI to Invest in AI"**
- ✅ Uses Groq AI to analyze AI company stocks (NVDA, MSFT, META, GOOGL, AMD)
- ✅ Demonstrates recursive intelligence application
- ✅ Shows practical AI implementation in finance

**"Building to Learn"**
- ✅ Open-source and fully transparent
- ✅ Educational explanations in every summary
- ✅ Invites experimentation and modification
- ✅ Documents what works and what doesn't

**"Discovering What Works"**
- ✅ Tests portfolio tracking methodologies
- ✅ Experiments with RAG retrieval strategies
- ✅ Gathers data to identify effective patterns
- ✅ Iterates based on results

**"Disciplined Investment"**
- ✅ Systematic daily monitoring (no emotional decisions)
- ✅ Structured data collection
- ✅ Foundation for rule-based risk management
- ✅ Evidence-based analysis

---

## ⚠️ Disclaimers

### Educational Purpose

This Portfolio Intelligence Agent is designed for **educational purposes only**. It demonstrates:
- Workflow automation concepts
- RAG system implementation
- AI integration patterns
- Portfolio tracking methodologies

**This is a learning tool, not a financial product.**

### Not Financial Advice

- This tool does NOT provide investment recommendations
- Past performance does not guarantee future results
- All investment decisions carry inherent risk
- The AI analysis is for educational purposes
- Consult qualified financial advisors for personal investment advice
- The creator assumes no liability for investment outcomes

### Data Accuracy

- Yahoo Finance data is provided "as is"
- Stock prices may be delayed (typically 15-20 minutes)
- Always verify critical data from official sources (broker, exchange)
- CSV files are stored locally and not automatically backed up
- File corruption could result in data loss

### AI Analysis Limitations

- Groq's summaries are AI-generated interpretations
- AI can make mistakes or miss important context
- Analysis should be used as one input among many
- Critical investment decisions require human judgment
- AI does not have real-time market awareness beyond data provided
- Knowledge base quality depends on accumulated data

---

## 🔗 Quick Links

- **Get Groq API Key (Free):** https://console.groq.com/keys
- **n8n Documentation:** https://docs.n8n.io/
- **Yahoo Finance:** https://finance.yahoo.com/
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords

---

## 🎓 Sample Data & Demo

### Example Email Report Output

**After first run:**
```
Portfolio Value: $17,903.66
Daily Return: +0.00% (first run)
Top Holding: MSFT (38.5%)

AI Analysis:
- Your AI-focused portfolio demonstrates concentration in Microsoft 
  (38.5%), approaching the 40% rebalancing threshold...
- Semiconductor sector exposure (NVDA + AMD = 25.9%) provides 
  AI chip manufacturing exposure...
- Educational insight: Diversification within a single sector 
  provides limited risk reduction...

🧠 Enhanced with 5 historical insights
```

**After 30 days:**
```
Portfolio Value: $19,234.50
Daily Return: +2.34%
Top Holding: MSFT (39.1%)

AI Analysis:
- Strong performance today (+2.34%), primarily driven by NVIDIA's 
  4.1% surge. Based on historical patterns retrieved from the 
  knowledge base, gains exceeding 2% typically persist for 3-5 days...
- Microsoft concentration stable at 39.1%. You've maintained this 
  just below your 40% threshold for 15 consecutive days, demonstrating 
  disciplined position management...
- Your portfolio's 30-day volatility is 1.8%, consistent with 
  historical norms for AI-heavy allocations...

🧠 Enhanced with 7 historical insights
```








# Mycroft Research Agent v2.0 - Investment Intelligence System

An educational n8n workflow demonstrating AI-powered investment analysis by combining financial metrics, patent intelligence, earnings execution, and competitive benchmarking to evaluate AI companies.

![Mycroft Research Agent 2.0 Workflow](https://github.com/Humanitariansai/Mycroft/blob/main/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.png)

## 🚀 Features

- **Multi-Agent Analysis**: 4 specialized agents (Financial, Patent, Earnings, Competitive)
- **Intelligent Scoring**: 50% innovation + 30% financial + 20% earnings weighting
- **Earnings Intelligence**: Quarterly beat/miss tracking with momentum classification
- **Competitive Benchmarking**: Automated peer rankings and sector comparison
- **Investment Recommendations**: STRONG BUY/BUY/MODERATE BUY/HOLD/SELL with detailed rationale
- **Professional Reports**: Markdown output with tables, grades, and actionable insights

## 🎯 System Architecture
```
Ticker Input → Financial APIs → Patent Search → Earnings Data → Competitive Analysis
     ↓              ↓              ↓               ↓                    ↓
  Set Node    Alpha Vantage   Google Custom   Alpha Vantage      Curated Peer
              (Overview,          Search        (Earnings)          Database
              Income Stmt)      (AI Patents)                            ↓
                  ↓               ↓               ↓              Multi-Dimensional
            Processing & Normalization                              Rankings
                              ↓                                        ↓
                    Multi-Agent Scoring (50/30/20)            Sector Benchmarks
                              ↓                                        ↓
                         Final Report (Markdown)
```

## 📊 Key Components

### 1. Data Collection
- **Alpha Vantage**: Financial overview, income statements, quarterly earnings
- **Google Custom Search**: AI patent portfolio intelligence
- **Curated Database**: 70+ companies with pre-mapped peer groups

### 2. Multi-Agent Scoring

**Innovation Score (50% weight)**:
- R&D intensity (30pts) + Patent portfolio (40pts) + AI focus (30pts)

**Financial Score (30% weight)**:
- Profitability (25pts) + Valuation (20pts) + Scale (20pts) + Efficiency (15pts)

**Earnings Score (20% weight)**:
- Latest quarter (40%) + Consistency (40%) + Average surprise (20%)

**Overall**: Weighted combination → Letter grade + recommendation

### 3. Competitive Intelligence
- Peer group rankings across 4 dimensions
- Sector average benchmarking
- 8-10 automated competitive insights
- Percentile positioning

### 4. Report Generation
- 14 comprehensive sections
- Professional markdown format
- Tables, metrics, visualizations
- 10-15 page detailed analysis

## 🔧 Installation & Setup

### Prerequisites
- n8n instance (download from https://n8n.io)
- Alpha Vantage API key (free tier available)
- Google Custom Search API key + Search Engine ID

### Step 1: Install n8n

**Option A - Desktop (Easiest)**:
```bash
# Download from https://n8n.io/download
# Install and launch
```

**Option B - npm**:
```bash
npm install -g n8n
n8n start
# Access at http://localhost:5678
```

**Option C - Docker**:
```bash
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### Step 2: Get API Keys

**Alpha Vantage API Key** (Required):

1. Visit https://www.alphavantage.co/support/#api-key
2. Click "GET YOUR FREE API KEY TODAY"
3. Fill form and submit
4. Copy API key from email
5. **Free tier**: 25 calls/day (~8 company analyses)

**Google Custom Search API** (Required):

1. **Create API Key**:
   - Go to https://console.cloud.google.com
   - Create new project
   - Enable "Custom Search API"
   - Create Credentials → API Key
   - Copy the key

2. **Create Search Engine ID**:
   - Visit https://programmablesearchengine.google.com
   - Click "Add" → Create new search engine
   - Configure: "Search the entire web"
   - Copy Search Engine ID (cx parameter)

3. **Free tier**: 100 queries/day

### Step 3: Import & Configure Workflow

1. **Import**:
   - Download workflow JSON from repository
   - Open n8n → Click "Import from File"
   - Select the JSON file

2. **Configure API Keys**:
   
   **For Alpha Vantage nodes** (Get Financial Overview, Get Income Statement, Get Earnings Data):
   - Click each node → Parameters tab
   - Find `apikey` parameter
   - Replace `YOUR_API_KEY` with your Alpha Vantage key
   
   **For Google Patent Search node**:
   - Click node → Parameters tab
   - Replace `key` parameter with your Google API key
   - Replace `cx` parameter with your Search Engine ID

3. **Test**:
   - Set ticker to "NVDA" in Company Input
   - Click "Execute Workflow"
   - Verify all nodes complete successfully
   - Download report from Investment Report node

### Step 4: Run Analysis
```javascript
// In Company Input node:
{ "ticker": "NVDA" }  // Change to any supported ticker

// Execute workflow
// Wait 5-15 seconds
// Download markdown report
```

## 📈 Sample Output

### Scoring Example (NVDA)
```
Innovation: 70/100 (B) - Strong patents, low R&D intensity
Financial: 82/100 (A-) - Exceptional margins and efficiency  
Earnings: 74/100 (B) - Perfect 4/4 beats, +6.2% avg surprise

Overall: 74/100 (B)
Recommendation: MODERATE BUY
Confidence: HIGH

Competitive Position: #4 of 5 (40th percentile)
Key Insight: "Leads in financial/earnings but lags in R&D investment (7.82% vs 16.6% sector avg)"
```

### Report Sections
1. Executive Summary (recommendation, scores, risk)
2. Company Information (sector, industry, description)
3. Scoring Breakdown (weights and percentiles)
4. Financial Analysis (complete metrics)
5. Innovation & R&D (patents and research intensity)
6. Earnings Performance (quarterly results, momentum)
7. **Competitive Landscape** (rankings, sector comparison) ← NEW
8. Investment Thesis (5-7 points)
9. Key Insights (actionable observations)
10. Risk Factors & Growth Opportunities
11. Methodology & Data Quality

## 🎓 Educational Use Cases

**Learning Objectives**:
- Multi-agent system design
- API integration and data processing
- Investment analysis frameworks
- Workflow automation
- Report generation

**Customization Ideas**:
- Adjust scoring weights for different strategies (growth vs value)
- Add sentiment analysis or insider trading data
- Expand to 10+ competitors
- Create portfolio-level analysis
- Build historical tracking database

## ⚠️ Limitations & Disclaimers

**Technical**:
- Educational tool only - not financial advice
- API rate limits: 25 Alpha Vantage calls/day on free tier
- Patent data uses search-based estimates
- Competitive data includes simulated peer scores

**Important**: This is for learning workflow automation and investment frameworks. Always consult qualified financial professionals before making investment decisions.

## 🐛 Troubleshooting

**"No output data" from API nodes**:
- Cause: Rate limit exceeded (25/day)
- Solution: Wait for reset (midnight EST) or upgrade API tier

**"Score is unexpectedly low"**:
- Cause: API returned empty data
- Check: Verify API keys and rate limits

**"Competitive section missing"**:
- Cause: Ticker not in database
- Solution: Adds automatically via sector fallback

**"Earnings not available"**:
- Normal: Uses 65/35 weighting when earnings data unavailable

## 🚀 Future Enhancements

- Real-time parallel competitor analysis
- Social sentiment integration
- Historical tracking database
- Interactive dashboards
- ML-based predictions
- Portfolio optimization

## 📊 Workflow Nodes (15 Total)

**Main Analysis** (12 nodes):
1. Company Input
2. Get Financial Overview (Alpha Vantage)
3. Get Income Statement (Alpha Vantage)
4. Get Earnings Data (Alpha Vantage)
5. Process Company Data
6. Google Patent Search
7. Process Patent Data
8. Process Financial Data
9. Process Earnings Data
10. Merge (3 inputs)
11. Generate Analysis
12. Generate Final Report

**Competitive Analysis** (3 nodes):
13. Generate Competitive Analysis
14. Merge Competitive Analysis
15. Investment Report (Python)

## 🌟 What Makes This Unique

### Multi-Agent Intelligence Example

**NVDA Analysis**:
```
Financial Agent: "82/100 - Strong margins, great ROE"
Earnings Agent: "74/100 - Perfect 4/4 beats"
Innovation Agent: "70/100 - Warning: Low R&D (7.82%)"
Competitive Agent: "#4 of 5 - R&D gap vs peers"

Result: MODERATE BUY
Insight: "Strong execution today, but underinvesting in R&D may impact future competitiveness"
```

**This emergent insight requires all 4 agents - no single dimension would catch it!**

## 📝 License

Educational use only. Not intended for actual investment decisions.


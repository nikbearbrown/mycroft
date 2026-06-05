# Mycroft Research Agent - Investment Intelligence System

An educational n8n workflow that demonstrates AI-powered investment analysis by combining financial metrics with patent intelligence to evaluate AI companies.

![Mycroft Research Agent Workflow](https://github.com/Humanitariansai/Mycroft/blob/main/n8n_Workflows/Research_Analytics_Agent/n8n_workflow.png)

## 🚀 Features

- **Multi-Source Financial Analysis**: Integrates Alpha Vantage API for comprehensive company financials
- **Patent Intelligence**: Google Custom Search integration for AI patent portfolio assessment
- **Intelligent Scoring System**: 65% innovation + 35% financial health weighting
- **Risk Assessment Engine**: Multi-factor evaluation with confidence ratings
- **Investment Recommendations**: STRONG BUY/BUY/HOLD/SELL with detailed rationale
- **Multi-Format Reports**: JSON, formatted text, and CSV outputs
- **Letter Grade System**: A+ to F ratings across all evaluation categories

## 🎯 System Architecture

```
Ticker Input → Financial APIs → Patent Search → Data Processing → Scoring Engine → Report Generation
     ↓              ↓              ↓               ↓                 ↓              ↓
  Set Node    Alpha Vantage   Google Custom    Function Nodes   Innovation &   JSON/Text/CSV
              Overview/Income     Search        Normalization    Financial      Professional
              Statement Data    AI Patents     Calculations      Scoring        Reports
```

## 📊 Key Components

### 1. Data Collection Layer
- **Alpha Vantage Integration**: Company overview and income statement data
- **Google Custom Search**: Patent intelligence gathering
- **Financial Metrics**: Market cap, revenue, profitability, valuation ratios
- **Patent Data**: AI-related patent counts, portfolio strength, innovation moat

### 2. Processing Engine
- **Company Name Normalization**: Removes corporate suffixes, handles special cases
- **Financial Calculations**: R&D intensity, profit margins, ROE, market cap classification
- **Patent Analysis**: AI patent ratio, portfolio quality scoring, competitive moat assessment
- **Data Validation**: Safe parsing with missing data handling

### 3. Scoring & Analysis
- **Innovation Score (0-100)**: R&D intensity (30pts) + Patent portfolio (40pts) + AI focus (30pts)
- **Financial Score (0-100)**: Profitability (25pts) + Valuation (20pts) + Scale (20pts) + Efficiency (15pts)
- **Overall Score**: Weighted combination (65% innovation + 35% financial)
- **Risk Classification**: LOW/MEDIUM/HIGH based on multiple factors
- **Confidence Rating**: HIGH/MODERATE/LOW based on data quality

### 4. Report Generation
- **Executive Summary**: Key recommendations and scores
- **Financial Analysis**: Complete financial breakdown with letter grades
- **Innovation Analysis**: Patent portfolio and R&D assessment
- **Investment Thesis**: Detailed rationale based on strengths
- **Risk & Opportunity Factors**: Comprehensive market analysis
- **Technical Metadata**: Data sources and methodology notes

## 🛠️ Technology Stack

- **Workflow Engine**: n8n (Visual workflow automation)
- **Financial Data**: Alpha Vantage API
- **Patent Intelligence**: Google Custom Search API
- **Processing**: JavaScript Function Nodes
- **Report Generation**: Python Code Node
- **Output Formats**: JSON, Markdown-style text, CSV

## 🔧 Installation & Setup

### Prerequisites
- n8n instance (local or cloud)
- Alpha Vantage API key (free tier available)
- Google Custom Search API key + Search Engine ID
- Basic understanding of n8n workflow concepts

### 1. Required Credentials

**Alpha Vantage API Key** (Required for Nodes 2 & 3):
1. Visit https://www.alphavantage.co/support/#api-key
2. Sign up for free API key (no credit card required)
3. Copy API key for use in workflow
4. **Nodes requiring this credential:**
   - Node 2: Get Financial Overview
   - Node 3: Get Income Statement

**Google Custom Search API** (Required for Node 5):
1. Visit Google Cloud Console: https://console.cloud.google.com
2. Create a new project or select existing one
3. Enable "Custom Search API"
4. Go to "Credentials" → Create API Key
5. Copy the API key
6. **Node requiring this credential:**
   - Node 5: Google Patent Search

**Google Custom Search Engine ID** (Required for Node 5):
1. Visit https://programmablesearchengine.google.com
2. Click "Add" to create new search engine
3. Configure: "Search the entire web"
4. Copy the Search Engine ID (cx parameter)
5. **Node requiring this credential:**
   - Node 5: Google Patent Search

### 2. Workflow Import
```bash
# Download workflow JSON
# Import into n8n instance
# Configure credentials in the following nodes:
#   - Node 2: Get Financial Overview (Alpha Vantage API key)
#   - Node 3: Get Income Statement (Alpha Vantage API key)
#   - Node 5: Google Patent Search (Google API key + Search Engine ID)
```

### 3. Node Configuration

**Node 1: Company Input (Set Node)**:
```json
{
  "ticker": "NVDA"  // Change to analyze different companies
}
```
**Credentials Required**: None

**Node 2: Get Financial Overview (HTTP Request)**:
- **Credential Required**: Alpha Vantage API key
- Add API key as query parameter: `apikey=YOUR_API_KEY`
- Method: GET
- URL: `https://www.alphavantage.co/query?function=OVERVIEW&symbol={{$json.ticker}}&apikey=YOUR_API_KEY`

**Node 3: Get Income Statement (HTTP Request)**:
- **Credential Required**: Alpha Vantage API key
- Add same API key as Node 2
- Method: GET
- URL: `https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={{$json.ticker}}&apikey=YOUR_API_KEY`

**Node 4: Process Company Data (Function Node)**:
- **Credentials Required**: None
- Pure JavaScript processing, no external API calls

**Node 5: Google Patent Search (HTTP Request)**:
- **Credentials Required**: 
  - Google Custom Search API key
  - Google Search Engine ID (cx parameter)
- Method: GET
- URL: `https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_SEARCH_ENGINE_ID&q={{$json.searchQuery}}`

**Nodes 6-10: Processing & Report Generation**:
- **Credentials Required**: None
- All processing done locally in Function/Code nodes

## 📈 Usage

### Running Analysis
1. **Manual Execution**: 
   - Open workflow in n8n
   - Change ticker symbol in Set Node
   - Click "Execute Workflow"

2. **Batch Analysis**:
   - Modify Set Node to include multiple tickers
   - Loop through companies sequentially

3. **Scheduled Runs**:
   - Add Schedule Trigger node
   - Set up daily/weekly analysis runs

### Understanding Output

#### Investment Recommendations
- **STRONG BUY** (85-100): Exceptional opportunity, strong fundamentals
- **BUY** (70-84): Solid investment with good growth potential
- **HOLD** (50-69): Adequate performance, monitor for changes
- **SELL** (<50): Underperforming, consider divesting

#### Risk Levels
- **LOW**: Strong financials, established patent portfolio, stable market position
- **MEDIUM**: Mixed indicators, some volatility or competitive concerns
- **HIGH**: Financial stress, limited innovation, significant market challenges

#### Letter Grades
- **A+/A** (90-100): Outstanding performance
- **B+/B** (80-89): Above average
- **C+/C** (70-79): Average/Satisfactory
- **D+/D** (60-69): Below average
- **F** (<60): Poor performance

## 📊 Sample Output

### Executive Summary
```json
{
  "company": "NVIDIA Corporation",
  "ticker": "NVDA",
  "overall_score": 88.5,
  "overall_grade": "A",
  "recommendation": "STRONG BUY",
  "risk_level": "LOW",
  "confidence": "HIGH"
}
```

### Innovation Analysis
```json
{
  "innovation_score": 92,
  "innovation_grade": "A",
  "rd_intensity": "28.5%",
  "total_patents": 11000,
  "ai_patent_ratio": "65%",
  "patent_quality_score": 95,
  "competitive_moat": "Very Strong"
}
```

### Financial Health
```json
{
  "financial_score": 82,
  "financial_grade": "B+",
  "market_cap": "$3.2T",
  "market_cap_category": "Mega Cap",
  "profit_margin": "53.4%",
  "pe_ratio": 62.5,
  "roe": "123.4%"
}
```

## 🎓 Educational Use Cases

### Learning Objectives
- **API Integration**: Understand multi-source data collection
- **Data Processing**: Learn normalization and calculation techniques
- **Scoring Algorithms**: Implement multi-factor decision models
- **Report Generation**: Create professional output formats
- **Workflow Design**: Build complex automation pipelines

### Customization Ideas
- Modify scoring weights based on investment strategy
- Add additional data sources (social sentiment, insider trading)
- Implement industry-specific scoring criteria
- Create comparative analysis across multiple companies
- Build portfolio-level aggregation reports

## 🔒 Limitations & Disclaimers

- **Educational Purpose**: Not financial advice, for learning automation only
- **Data Accuracy**: Relies on third-party API data quality
- **Patent Estimates**: Uses search-based approximations, not official counts
- **Market Timing**: Does not account for market conditions or timing
- **Risk Factors**: Simplified risk model, real investment requires deeper analysis

## 🚀 Future Enhancements

- **Real-time Market Data**: Live stock price integration
- **Social Sentiment**: Twitter/Reddit sentiment analysis
- **Competitor Analysis**: Side-by-side company comparisons
- **Historical Tracking**: Database storage for trend analysis
- **Visualization Dashboard**: Charts and graphs for reports
- **Advanced AI Models**: ML-based prediction improvements
- **Portfolio Management**: Multi-company portfolio analysis

## 📚 Node-by-Node Breakdown

### Node 1: Company Input (Set Node)
- **Purpose**: Entry point for ticker symbols
- **Configuration**: Sets `ticker` variable (default: "NVDA")
- **Customization**: Change ticker to analyze different companies

### Node 2: Get Financial Overview (HTTP Request)
- **API**: Alpha Vantage OVERVIEW function
- **Data Retrieved**: Market cap, revenue, margins, P/E ratio, sector info
- **Output**: Company financial overview JSON

### Node 3: Get Income Statement (HTTP Request)
- **API**: Alpha Vantage INCOME_STATEMENT function
- **Data Retrieved**: Annual reports, R&D spending, revenue breakdowns
- **Output**: Financial statement data with time series

### Node 4: Process Company Data (Function Node)
- **Processing**: Name normalization, suffix removal, special case handling
- **Example**: "NVIDIA Corporation" → "NVIDIA"
- **Output**: Clean company name for patent search

### Node 5: Google Patent Search (HTTP Request)
- **API**: Google Custom Search
- **Query**: "[Company] patents AI artificial intelligence machine learning recent 2023 2024"
- **Output**: Patent-related search results

### Node 6: Process Patent Data (Function Node)
- **Analysis**: Patent count estimation, AI ratio calculation
- **Scoring**: Quality assessment, competitive moat evaluation
- **Output**: Patent intelligence metrics

### Node 7: Process Financial Data (Function Node)
- **Calculations**: R&D intensity, margins, ROE, market cap category
- **Safety**: Handles missing data gracefully
- **Output**: Processed financial metrics

### Node 8: Generate Analysis (Function Node)
- **Core Logic**: Combines innovation + financial scores
- **Algorithm**: Weighted scoring (65/35 split)
- **Output**: Overall score, recommendation, risk assessment

### Node 9: Generate Final Report (Function Node)
- **Formatting**: Professional report structure
- **Components**: Executive summary, analysis, thesis, risks/opportunities
- **Output**: Complete investment report JSON

### Node 10: Report Download (Python Code Node)
- **Formatting**: Text report with emojis, CSV data export
- **Instructions**: Download guidance for both formats
- **Output**: Multi-format reports ready for download

## 📝 License

Educational use only. Not intended for actual investment decisions.

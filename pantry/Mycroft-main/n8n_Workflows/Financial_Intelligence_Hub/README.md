# Financial Intelligence Hub 

> **Developed by:** Darshan Rajopadhye (rajopadhye.d@northeastern.edu)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/darshanrr)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/therrshan)


### [![LinkedIn](https://img.shields.io/badge/Youtube_Demo-red?style=flat&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=zgWUwwgSJWE&t=9s)

## 🎯 Overview

The **Mycroft Intelligence Hub** is an AI-powered orchestration system that provides comprehensive financial and patent intelligence through natural language queries. It intelligently routes queries to specialized analysis workflows, aggregates results, and generates actionable insights using local LLMs.

### Key Features

- 🤖 **Natural Language Interface** - Chat-based interaction powered by Ollama LLMs
- 🎯 **Intelligent Query Routing** - AI automatically determines which analysis workflows to call
- 📊 **Multi-Source Intelligence** - Combines SEC filings and USPTO patent data
- 💡 **AI-Generated Insights** - Synthesizes data into executive summaries and recommendations
- 📁 **Persistent Storage** - All analysis results saved with comprehensive logging
- 🔄 **Real-time Monitoring** - Complete execution tracking and progress logging

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  MYCROFT INTELLIGENCE HUB                    │
│                    (Orchestrator Layer)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
         ┌──────────▼──────────┐  ┌────▼────────────────┐
         │  SEC Filings Agent  │  │  Patent Intel Agent │
         │   (Financial Data)  │  │   (Innovation Data) │
         └─────────────────────┘  └─────────────────────┘
                    │                   │
         ┌──────────▼──────────┐  ┌────▼────────────────┐
         │   SEC EDGAR API     │  │  USPTO PatentsView  │
         │   (Primary Source)  │  │   (Primary Source)  │
         └─────────────────────┘  └─────────────────────┘
```

### Data Flow

```
User Query → LLM Router → Route Decision → Call Workflows → 
Aggregate Results → LLM Analyst → Insights Report → User
```



### Installation Steps

#### 1. Import Workflows

1. Download the three workflow JSON files:
   - `Mycroft - Intelligence Hub Orchestrator.json`
   - `Mycroft - SEC_Filings_Analysis_Enhanced.json`
   - `Mycroft - Patent_Intelligence_System_Enhanced.json`

2. In n8n, go to **Workflows** → **Import from File**

3. Import all three workflows

#### 2. Configure SEC Workflow

1. Open **SEC Filings Analysis Enhanced** workflow
2. Locate the **Webhook** node (first node)
3. Set path: `sec-analysis`
4. Set response mode: `lastNode`
5. **Activate the workflow** (toggle switch ON)
6. Copy the **Production URL** (e.g., `http://localhost:5678/webhook/sec-analysis`)

#### 3. Configure Patent Workflow

1. Open **Patent Intelligence Enhanced** workflow
2. Locate the **Webhook** node (first node)
3. Set path: `patent-analysis`
4. Set response mode: `lastNode`
5. **Activate the workflow** (toggle switch ON)
6. Copy the **Production URL** (e.g., `http://localhost:5678/webhook/patent-analysis`)

#### 4. Configure Intelligence Hub

1. Open **Intelligence Hub Orchestrator** workflow
2. Update the **HTTP Request** nodes with your webhook URLs:

   **Call SEC Workflow node:**
   ```
   URL: http://localhost:5678/webhook/sec-analysis
   Method: POST
   ```

   **Call Patent Workflow node:**
   ```
   URL: http://localhost:5678/webhook/patent-analysis
   Method: POST
   ```

3. Verify Ollama settings in both LLM Chain nodes:
   ```
   Model: llama3.2:3b
   URL: http://localhost:11434
   ```

4. **Activate the workflow**



## 💬 Usage

### Starting a Chat Session

1. Open the **Intelligence Hub Orchestrator** workflow in n8n
2. Click the **"Chat"** button in the top right
3. A chat interface will open
4. Start typing your queries!

### Example Queries

**Simple Queries:**
```
Analyze Apple
Show me Tesla's financials
What patents did NVIDIA file recently?
```

**Time-Specific Queries:**
```
Show patent trends from the last 3 months
Analyze Microsoft's recent SEC filings
Get me innovation data from the past week
```

**Comprehensive Analysis:**
```
What's Tesla doing in innovation and how are their financials?
Compare Apple's R&D spending to their patent output
Analyze Google's AI strategy - show me patents and financial performance
```

**Vague Queries (AI figures it out):**
```
Tell me about Apple
What's happening with Tesla?
NVIDIA trends
```

### Understanding the Response

The hub returns a formatted report with:

```
🎯 MYCROFT INTELLIGENCE REPORT

📋 Query: [Your query]
⏱️ Execution Time: [Time in ms]
📊 Data Sources: [SEC EDGAR, USPTO PatentsView]

---

[AI-Generated Analysis with:]
- Executive Summary
- Key Findings (with specific numbers)
- Strategic Recommendations
- Risk Factors
- Opportunities

---

🆔 Execution ID: [Unique ID]
📁 Full log: /tmp/mycroft_logs/hub_[ID].json
```

---


## 📊 Examples

### Example 1: Single Company Financial Analysis

**Query:** `"Analyze Apple's financials"`

**Router Output:**
```json
{
  "tools_to_call": ["analyze_sec_filings"],
  "parameters": {
    "analyze_sec_filings": {"ticker": "AAPL"}
  }
}
```

**Response:**
```
🎯 MYCROFT INTELLIGENCE REPORT

📋 Query: Analyze Apple's financials
⏱️ Execution Time: 4523ms
📊 Data Sources: SEC EDGAR

---

**Executive Summary**
Apple's latest 10-K filing shows strong financial performance with 
$383B in annual revenue (↑8% YoY). Gross margins maintained at 43.3% 
despite supply chain headwinds.

**Key Findings**
• Revenue: $383.29B (↑8% YoY)
• Net Income: $96.99B (↑5% YoY)
• Operating Margin: 29.8%
• Cash & Equivalents: $62.6B
• R&D Spending: $26.25B (6.8% of revenue)

**Strategic Recommendations**
1. Monitor Services segment growth - highest margin contributor
2. Watch international revenue mix (60% of total)
3. Track R&D efficiency: $146M revenue per $1M R&D
...
```

### Example 2: Patent Trend Analysis

**Query:** `"Show AI patent trends from last 3 months"`

**Router Output:**
```json
{
  "tools_to_call": ["analyze_patents"],
  "parameters": {
    "analyze_patents": {"days_back": 90}
  }
}
```

**Response:**
```
📊 Data Sources: USPTO PatentsView

**Executive Summary**
342 AI-related patents filed in last 90 days (27.4% of total filings).
Google, Microsoft, and IBM lead with focus on neural networks and 
machine learning applications.

**Key Findings**
• Total Patents: 1,247
• AI-Related: 342 (27.4%)
• Top Filer: Google (45 patents)
• Primary CPC Class: G06N (Neural Networks)
• Patent Velocity: 3.8 patents/day

**Strategic Recommendations**
1. Track Google's on-device ML patent activity
2. Monitor Microsoft's AI infrastructure patents
3. Watch for cross-licensing opportunities in G06N space
...
```

### Example 3: Comprehensive Analysis

**Query:** `"What's Tesla doing in innovation and financials?"`

**Router Output:**
```json
{
  "tools_to_call": ["analyze_sec_filings", "analyze_patents"],
  "parameters": {
    "analyze_sec_filings": {"ticker": "TSLA"},
    "analyze_patents": {"days_back": 100}
  }
}
```

**Response:**
```
📊 Data Sources: SEC EDGAR, USPTO PatentsView

**Executive Summary**
Tesla filed 89 patents in last 100 days (focus: autonomous driving, 
battery tech) while maintaining 17% gross margins. R&D spending at 
$3.1B (4.2% of revenue) shows aggressive innovation investment.

**Key Findings**
• Revenue: $73.5B (↑18% YoY)
• Patent Filings: 89 (32% AI-related)
• R&D to Revenue: 4.2% (industry avg: 3.5%)
• Patent Focus: Autonomous systems (G05D), Battery tech (H01M)
• Operating Cash Flow: $8.9B

**Strategic Recommendations**
1. Assess R&D ROI: Patent output suggests focused innovation strategy
2. Monitor autonomous driving patent portfolio growth
3. Compare patent velocity to legacy automakers
4. Track correlation between R&D spend and patent quality
5. Watch for strategic partnerships in battery technology

**Opportunities**
• Patent portfolio could enable technology licensing revenue
• Strong innovation pipeline supports premium positioning
• Vertical integration reflected in manufacturing process patents
...
```

---



## 🙏 Acknowledgments

- **n8n** - Workflow automation platform
- **Ollama** - Local LLM inference
- **SEC EDGAR** - Financial data source
- **USPTO PatentsView** - Patent data API

---

*Last Updated: November 14, 2025*
# AI Talent Intelligence Agent

An automated n8n workflow that monitors AI research papers, news, and generates comprehensive intelligence reports about AI companies and researchers.

<img width="380" height="150" alt="image" src="https://github.com/user-attachments/assets/454bb3f8-77d1-4d71-b73f-ff3cb32c4b78" />


## Overview

This system automatically:
- 📚 Monitors ArXiv for AI research papers
- 📰 Tracks news about AI researcher movements
- 🤖 Analyzes data using Groq AI (free alternative to OpenAI)
- 📊 Generates investment signals and trend analysis
- 📧 Sends formatted HTML email reports

**Status**: MVP/Prototype - Production-ready architecture with real news data

## Features

✅ **Real Data Sources**:
- Serper News API (real-time AI researcher news)
- ArXiv API (research papers)
- Extensible database integration

✅ **AI Analysis**:
- Groq LLM for entity extraction and sentiment analysis
- Significance scoring and filtering
- Automated trend detection

✅ **Professional Reports**:
- HTML email reports with executive summary
- Investment signals (STRONG_BUY, BUY, HOLD)
- Top researchers rankings
- Key trends and priority alerts

## Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   ArXiv API │────▶│              │     │             │
├─────────────┤     │              │     │   Groq AI   │
│  Serper API │────▶│    MERGE     │────▶│  Analysis   │
├─────────────┤     │              │     │             │
│  Database   │────▶│              │     └─────────────┘
└─────────────┘     └──────────────┘            │
                                                 ▼
                                         ┌──────────────┐
                                         │    FILTER    │
                                         │ (significance)│
                                         └──────────────┘
                                                 │
                                                 ▼
                                         ┌──────────────┐
                                         │  AGGREGATE   │
                                         │  Statistics  │
                                         └──────────────┘
                                                 │
                                                 ▼
                                         ┌──────────────┐
                                         │   Generate   │
                                         │    Report    │
                                         └──────────────┘
                                                 │
                                                 ▼
                                         ┌──────────────┐
                                         │ Email Report │
                                         └──────────────┘
```

## Prerequisites

- **n8n** (self-hosted or cloud)
- **Groq API Key** (free): https://console.groq.com
- **Serper API Key** (free tier): https://serper.dev
- **Email SMTP** credentials (Gmail, etc.)

## Setup Instructions

### 1. Get API Keys

**Groq (Free)**:
1. Go to https://console.groq.com
2. Sign up and create an API key
3. Copy your API key

**Serper (Free)**:
1. Go to https://serper.dev
2. Sign up for free account
3. Copy your API key from dashboard

### 2. Import Workflow to n8n

1. Download `ai-talent-intelligence-workflow.json` from this repository
2. Open your n8n instance
3. Click **Import from File**
4. Select the JSON file

### 3. Configure Credentials

**Groq Credentials**:
- Node: "Basic LLM Chain"
- Type: API Key
- Add your Groq API key

**Serper Credentials**:
- Node: "SOURCE 2: News Search"
- Type: Header Auth
- Header Name: `X-API-KEY`
- Header Value: Your Serper API key

**Email Credentials**:
- Node: "Send Email Report"
- Type: SMTP
- Configure your email provider settings

### 4. Customize Configuration

**Update email addresses** in "Send Email Report" node:
```javascript
fromEmail: "your-email@gmail.com"
toEmail: "recipient@gmail.com"
```

**Adjust search queries** in "SOURCE 2: News Search":
```javascript
q: "YOUR SEARCH QUERY HERE"
num: 20  // Number of results
```

**Modify significance threshold** in "FILTER" node:
```javascript
// Current: significance > 5
// Adjust as needed
```

## Usage

### Manual Execution

1. Open the workflow in n8n
2. Click **"Execute workflow"** button
3. Wait for completion (~30-60 seconds)
4. Check your email for the report

### Scheduled Execution

Add a **Schedule Trigger** node:
```
Cron: 0 9 * * 1  // Every Monday at 9 AM
```

## Data Sources

### SOURCE 1: ArXiv Papers
- **Status**: API connected, using demo data for parsing
- **Real Implementation**: Parse actual XML response from ArXiv
- **Categories**: cs.AI, cs.LG, cs.CL

### SOURCE 2: News Search (Serper)
- **Status**: ✅ **100% Real Data**
- **Query**: AI researcher movements and hiring news
- **Results**: 10-20 recent articles

### SOURCE 3: Researcher Database
- **Status**: Mock data (demonstration)
- **Real Implementation**: Connect to PostgreSQL or use Google Scholar API
- **Sample Data**: Top AI researchers (Ilya Sutskever, Dario Amodei, etc.)

## Key Components Explained

### Groq AI Analysis
Uses Groq's free LLM API (30 req/min) instead of OpenAI:
```javascript
// Analyzes each item and extracts:
{
  "companies": ["OpenAI", "Anthropic"],
  "researchers": ["Researcher Name"],
  "technologies": ["GPT-4", "Claude"],
  "sentiment": "positive",
  "significance": 8
}
```

### Filter Node
Filters items by significance score:
- **True branch**: significance > 5 (high priority)
- **False branch**: significance ≤ 5 (filtered out)

### Aggregate Node
Combines filtered items into summary statistics:
```javascript
{
  all_companies: [...],
  all_researchers: [...],
  avg_significance: 8.2,
  total_signals: 5
}
```

### Report Generator
Creates comprehensive intelligence report with:
- Executive summary metrics
- Investment signals (STRONG_BUY/BUY/HOLD)
- Top researchers table
- Key trends analysis
- Priority alerts

## Sample Output

**Email Report Includes**:
- 📊 Executive Summary (companies tracked, avg significance)
- 🎯 Investment Signals with scores
- 👥 Top Researchers rankings
- 🔥 Key Trends
- ⚠️ Priority Alerts

<img width="335" height="203" alt="image" src="https://github.com/user-attachments/assets/f5b8e4c1-61d1-4276-b888-339febb4adb8" />


**Report Structure**:
```
🚀 AI Talent Intelligence Report
Generated: 1/23/2026, 5:06 PM

📊 Executive Summary
- Companies Tracked: 5
- Top Researchers: 8
- Avg Signal Strength: 8.0/10

🎯 Investment Signals
- OpenAI: STRONG_BUY (92/100)
- Anthropic: STRONG_BUY (88/100)
- Google DeepMind: BUY (85/100)
...
```

## Contributing

Contributions welcome! Areas for improvement:
- Real ArXiv XML parsing implementation
- Additional data source integrations
- Enhanced AI analysis prompts
- Dashboard visualization

## Resources

- **n8n Documentation**: https://docs.n8n.io
- **Groq API Docs**: https://console.groq.com/docs
- **Serper API Docs**: https://serper.dev/api
- **ArXiv API**: https://arxiv.org/help/api


## Author

**[Anshika Khandelwal]**
- LinkedIn: https://www.linkedin.com/in/anshika-khandelwal/
- Humanitarians AI Fellow

---

**Built with ❤️ as part of Humanitarians AI Fellowship Program**

🔗 **Connect with Humanitarians AI**:
- Website: https://www.humanitarians.ai/
- YouTube: https://www.youtube.com/@humanitariansai
- GitHub: https://github.com/Humanitariansai/

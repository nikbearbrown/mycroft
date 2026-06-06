# Mycroft Orchestrator
A multi-agent orchestration system that intelligently routes user queries to specialized financial and patent intelligence workflows using natural language processing.
## Overview
The Orchestrator serves as the central dispatcher for the Mycroft intelligence platform. It uses a local LLM (Llama 3) to analyze natural language queries and automatically route them to the appropriate specialized agent.
## Architecture
```
User Query → Chat Interface → LLM Analyzer → Validator → HTTP Router → Specialized Agent
```
## Available Tools
### 1. Patent Monitor
Monitors and analyzes recent patent filings from the USPTO.
**Parameters:**
- `days_back` (integer, required) - Number of days to look back
- `email` (string, optional) - Email for report delivery
**Example:** *"Show me patents from the last 7 days"*
---
### 2. Financial Metrics
Analyzes SEC filings (10-K, 10-Q) for financial insights.
**Parameters:**
- `ticker` (string, required) - Stock ticker (e.g., "AAPL", "TSLA")
- `narrative` (boolean, required) - Include narrative analysis
**Example:** *"Get financial metrics for AAPL"*
---
### 3. News Sentiment
Aggregates news and performs sentiment analysis using FinBERT.
**Parameters:**
- `company` (string, required) - Company name
- `email` (string, optional) - Email for report delivery
**Example:** *"Analyze news sentiment for Microsoft"*
---
### 4. Forecasting
Generates price forecasts using market data and sentiment.
**Parameters:**
- `ticker` (string, required) - Stock ticker
- `email` (string, required) - Email for results
- `horizon` (integer, optional, default: 30) - Forecast days
**Example:** *"Forecast NVDA for the next 45 days"*
## How It Works
1. **Query Analysis** - LLM determines the appropriate tool and parameters
2. **Validation** - Parameters are type-checked against schema
3. **Routing** - HTTP request dispatched to the agent webhook
4. **Response** - Agent processes request and returns results
## Example Queries
```
"Monitor patents from the last 30 days"
"Get detailed analysis for TSLA"
"What's the sentiment on Amazon lately?"
"Forecast NVDA for 60 days"
```
## Key Features
- Natural language interface
- Intelligent tool routing
- Type-safe validation
- Local LLM processing
- Extensible design
- Comprehensive error handling
## Setup Requirements
- n8n instance
- Ollama with Llama 3
- Agent workflows deployed
- Network connectivity
## Future Enhancements
- Multi-tool queries (sequential or parallel execution)
- User session management and context preservation
- Tool result caching and optimization
- Enhanced natural language understanding
- Query analytics and performance monitoring
- Additional tool integrations (market data, regulatory filings)
- Intent confidence scoring for ambiguous queries
---
## Version Status
**Current Version: 1.0** - Active

**Version 2.0** - In development (v2-dev version)

### What's Coming in v2:
- **Persistent Data Storage** - Complete request/response logging using n8n Data Store with tool-specific organization and time-series analytics tracking
- **Automated Notifications** - Email alerts when queries complete, including request summaries, performance metrics, and data store references
- **Performance Monitoring** - Response time tracking, tool usage analytics by date/hour, and query pattern analysis for optimization insights

---
**Status:** v1.0 Active | v2-dev In Progress  
**Last Updated:** October 2025
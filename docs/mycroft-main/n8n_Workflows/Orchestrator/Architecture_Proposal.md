# Mycroft Orchestrator: Architecture Evolution

## Executive Summary

This document outlines the current limitations of the Mycroft Orchestrator v1.0 and proposes a domain-specific intelligence architecture (v2.0+) that enables meaningful data aggregation and strategic decision-making across heterogeneous financial intelligence tools.

---

## Current Architecture (v1.0)

### System Design
```
User Query → Chat Interface → LLM Analyzer → Validator → HTTP Router → Specialized Agent
                                                                              ↓
                                                                        Tool Execution
                                                                              ↓
                                                                       Direct Response
```

### Available Tools
1. **Patent Monitor** - USPTO filing analysis
2. **Financial Metrics** - SEC filing analysis (10-K, 10-Q)
3. **News Sentiment** - FinBERT-powered sentiment analysis
4. **Forecasting** - Price prediction with market data

### Current Status
- ✅ v1.0 is functional and operational
- ✅ Natural language query routing works
- ✅ All four specialized tools are integrated
- ✅ Basic validation and error handling in place

---

## Problem Statement

### The Abstraction Challenge

**Core Issue**: Attempting to create unified data storage and aggregation at the orchestrator level fails because the tools operate in fundamentally different semantic domains.

#### Why Standardization Fails Here

**Semantic Heterogeneity**:
- **Patents**: Structured legal documents with classifications, citations, assignees, temporal filing patterns
- **Financials**: Numerical metrics with ratios, trends, balance sheets, cash flows
- **Sentiment**: Qualitative signals with scores, volume, source credibility, narrative themes
- **Forecasting**: Probabilistic predictions with confidence intervals, scenarios, time horizons

**Example of the Problem**:
```json
// Attempting unified schema - semantically meaningless
{
  "tool": "patent_monitor",
  "result": "127 patents filed",  // What does this mean strategically?
  "timestamp": "2025-11-07"
}

{
  "tool": "financial_metrics", 
  "result": "Revenue: $89B, P/E: 24.5",  // How does this relate to patents?
  "timestamp": "2025-11-07"
}
```

**The fundamental question**: How do you aggregate patent filing counts with P/E ratios and sentiment scores in a meaningful way? You can't—at least not at this abstraction level.

### Why This Matters

Without domain-specific intelligence layers:
- ❌ Raw data sits without interpretation
- ❌ No strategic insights generated
- ❌ Cannot correlate across domains meaningfully
- ❌ No decision support capability
- ❌ Each tool remains siloed

The v1.0 system successfully routes queries and executes tools, but lacks the intelligence layer to make the outputs strategically useful.

---

## Proposed Solution: Domain Intelligence Architecture

### Architectural Philosophy

**Key Insight**: Build intelligence at the semantic level where aggregation is meaningful, then compose those insights for strategic decision-making.

### New Architecture (v2.0+)

```
                            User Query
                                ↓
                         Orchestrator
                      (Query Routing)
                                ↓
                 ┌──────────────┼──────────────┐
                 ↓              ↓              ↓              ↓
           Patent Tool    Financial Tool  Sentiment Tool  Forecast Tool
                 ↓              ↓              ↓              ↓
         [Raw Data Store] [Raw Data Store] [Raw Data Store] [Raw Data Store]
                 ↓              ↓              ↓              ↓
    ┌────────────────────────────────────────────────────────────┐
    │              DOMAIN INTELLIGENCE LAYER                      │
    ├────────────┬────────────┬────────────┬───────────────────┤
    │   Patent   │ Financial  │ Sentiment  │   Forecasting     │
    │Intelligence│Intelligence│Intelligence│  Intelligence     │
    └────────────┴────────────┴────────────┴───────────────────┘
                                ↓
                    ┌───────────────────────┐
                    │ CENTRAL INTELLIGENCE  │
                    │  (Strategic Layer)    │
                    └───────────────────────┘
                                ↓
                    Cross-Domain Correlation
                    Investment Decisions
                    Risk Assessment
```

---

## Domain Intelligence Layers

The solution requires building **four independent intelligence hubs**. These hubs could process raw tool outputs and generate domain-specific insights.

## Possible Data Storage Strategy

### Three-Tier Hierarchy

**Tier 1: Raw Tool Data** (Current v2-dev)
```
/data/raw/{tool_name}/{timestamp}
- Complete request/response logs
- Performance metrics
- Error tracking
```

**Tier 2: Domain Intelligence** (New)
```
/data/intelligence/{domain}/{company}/{period}
- Processed insights
- Trend analysis
- Comparative metrics
```

**Tier 3: Strategic Signals** (New)
```
/data/strategic/{portfolio}/{timestamp}
- Cross-domain correlations
- Investment recommendations
- Risk assessments
```

### Benefits of Hierarchical Storage
- **Granularity**: Debug at tool level
- **Abstraction**: Analyze at intelligence level
- **Decision Support**: Act at strategic level
- **Traceability**: Trace strategic decision → domain insight → raw data


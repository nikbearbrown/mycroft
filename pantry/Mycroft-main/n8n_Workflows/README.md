# n8n workflows 

## AI News Sentiment Workflow
Daily workflow that monitors AI news and alerts on negative sentiment. Uses NewsAPI to fetch headlines, applies keyword-based sentiment analysis with embedded Python, stores results in Airtable, and sends email notifications for negative articles only. Simple yet effective implementation showing n8n's ability to combine visual workflow design with custom code.

> ⚠️ Note: This version is a starting point.

➡️ For full technical documentation, check out the [AI News Sentiment.md](./AI_NEWS_SENTIMENT/AI%20News%20Sentiment.md) file.

➡️ A more advanced Phase 2 version is also available, which uses FinBERT-based sentiment analysis, multi-factor risk scoring, PostgreSQL storage, and real-time alerts. 
For full technical documentation, check out the [Mycroft News Intelligence Agent.md](./AI_NEWS_SENTIMENT/Mycroft%20News%20Intelligence%20Agent.md) file.

## Financial Metrics Analysis Workflow
Tool that analyzes SEC financial filings for publicly traded companies. Executes a Python script to retrieve official financial data, calculates key metrics and ratios, and generates comprehensive reports with both structured JSON output and human-readable summaries. Currently manual but designed for future automation as part of a larger financial intelligence orchestration system.

➡️ For full technical documentation, check out the [README.md](./SEC_FINANCIAL_METRICS/README.md) file.

## Patent Intelligence System Workflow
Automated patent monitoring and AI classification system that tracks recent USPTO patent filings. Extracts patent metadata from PatentsView API using cursor-based pagination, processes records to identify AI-related innovations through keyword matching and CPC code analysis, normalizes company names, and generates intelligence reports with confidence scoring. Delivers CSV data and metrics JSON via email for competitive intelligence and technology scouting.

➡️ For full technical documentation, check out the [README.md](./Patent_Intelligence_Agent/README.md) file.

## Forecasting Agent Workflow

An n8n workflow that generates stock price forecasts by combining market data (Alpha Vantage) with FinBERT-based sentiment analysis.  
The agent computes optimistic, realistic, and pessimistic scenarios, applies volatility-based risk scoring, and stores results in PostgreSQL for downstream dashboards.

📄 For full technical documentation, check out the [README.md](./Forecasting_Agent/Forecasting_Agent.md) file.

## Research Agent Workflow
Educational AI-powered investment analysis workflow that evaluates AI companies by combining financial metrics with patent intelligence. Named after Sherlock Holmes's analytical brother, the system fetches live financial data from Alpha Vantage, performs Google patent searches, calculates innovation and financial health scores, and generates comprehensive investment recommendations with risk assessments. Outputs professional reports in multiple formats (JSON, text, CSV) with letter grades, investment thesis, and confidence ratings.

➡️ For full technical documentation, check out the [Mycroft Research Agent.md](./Research_Analytics_Agent/Mycroft%20Research%20Agent.md) file.

## Funding Intelligence Agent
Automated workflow that monitors AI startup funding announcements from TechCrunch and VentureBeat. Filters funding-related articles, classifies them by industry using keyword matching, stores data in PostgreSQL and Google Sheets, and sends daily email digests. Saves 10+ hours per week in manual research.

📊 For full technical documentation, check out the [README.md](./Funding_Intelligence_Agent/README.md) file.


## Research Agent - Earnings & Competitor Analysis Workflow
Educational AI-powered investment analysis workflow that evaluates AI companies through a multi-agent intelligence framework, the system combines four specialized agents: **Financial Analysis** (Alpha Vantage metrics), **Patent Intelligence** (Google patent searches), **Earnings Execution** (quarterly beat/miss tracking with momentum analysis), and **Competitive Benchmarking** (peer rankings and sector comparison). The workflow calculates weighted scores, generates comprehensive investment recommendations with risk assessments, and produces professional markdown reports.

➡️ For full technical documentation, check out the [README.md](./Research_Analytics_Agent/README.md) file.

## Investor Intelligence Agent

AI-powered workflow that analyzes relationships between investors, startups, and AI-sector funding activity using PostgreSQL and natural-language query parsing. Automatically classifies user questions (e.g., investor profiles, startup investors, recent deals, top investors), routes them to optimized SQL workflows, and returns structured insights via an interactive HTML chatbot interface. Enables rapid exploration of investor networks, deal histories, and sector trends.

📄 For full technical documentation, check out the [Readme.md](./Investor_Intelligence/Readme.md) file.

# Regulatory Intelligence QA Agent for Investment Firms

## Overview

A conversational AI agent that transforms regulatory monitoring into actionable investment intelligence. Built as an extension to Mycroft’s existing Regulatory Intelligence Agent, this QA layer enables portfolio managers, analysts, and compliance officers to ask natural language questions about regulatory changes and receive instant, cited answers focused on portfolio impact and investment decisions.

This agent is part of the broader Mycroft AI Agent ecosystem, working alongside other specialized agents to provide comprehensive intelligence capabilities.

## The Vision

Imagine an agent where instead of reading through hundreds of regulatory documents, investment teams can simply ask questions and get precise, portfolio-aware answers in seconds.

**Traditional Workflow:**

- Compliance alert arrives about new SEC rule
- Analyst spends 2-4 hours reading 300-page document
- Manual cross-reference with portfolio holdings
- Write memo for portfolio managers
- Decision made 2-3 days later

**With Regulatory QA Agent:**

- Same alert arrives
- Portfolio manager asks: “How does this affect our top 10 holdings?”
- Receives answer in 30 seconds with specific impact analysis
- Decision made same day

The agent doesn’t just retrieve documents—it understands context, analyzes implications, and presents answers through the lens of investment risk and opportunity.

## Problem Statement for Investment Firms

Investment firms face unique challenges that corporate compliance systems don’t address:

**Portfolio Risk Assessment**: When the SEC announces new climate disclosure rules, which holdings are affected? Which sectors face the highest compliance costs? Which companies might gain competitive advantage?

**Investment Due Diligence**: Evaluating an acquisition target requires understanding their regulatory exposure. What new requirements were introduced in their sector over the past 6 months? What compliance obligations would be inherited?

**Market Timing**: Regulatory momentum often precedes market movements. Can teams identify when a sector faces regulatory headwinds versus tailwinds? How have similar regulatory patterns correlated with performance historically?

**Client Communication**: Investors need clear explanations of how regulatory changes affect their portfolios, not 50-page legal analyses.

Unlike corporate compliance (which asks “are we compliant?”), investment firms ask “how does this affect portfolio value and strategy?”

## Use Cases

### Portfolio Impact Analysis

A portfolio manager receives an alert about new SEC enforcement disclosure rules and asks the agent:

**Query**: *“How will the new SEC climate disclosure rules affect our energy sector holdings?”*

**Agent Response**: The agent analyzes the regulatory documents, cross-references with portfolio holdings, and responds that 15 of 23 energy holdings will be affected. It identifies three high-impact positions: one company with significant Scope 3 exposure facing material costs, another already compliant with competitive advantage, and notes that smaller holdings under $1B market cap are exempt until 2026. The response includes specific recommendation to review holdings over $700M within 48 hours, all backed by citations to the actual regulatory text.

**Value**: Immediate, actionable intelligence that would traditionally take 2-3 days of analyst work.

### Investment Due Diligence

An investment team is evaluating acquisition of a fintech company and needs rapid regulatory risk assessment.

**Query**: *“What regulatory changes in the past 6 months affect digital payment processors? What compliance requirements would we inherit?”*

**Agent Response**: The agent identifies three major developments: enhanced AML requirements with September 2024 deadline (4 months post-query), new open banking data sharing rules with tight implementation windows, and 5 new state licensing requirements. It flags that the FINRA deadline might require pre-close remediation and estimates compliance costs. The analysis includes specific regulatory citations and implementation timelines.

**Value**: Comprehensive regulatory risk profile generated in minutes rather than days, enabling faster M&A decisions.

### Sector Rotation Strategy

An analyst is planning quarterly portfolio positioning and needs regulatory trend analysis.

**Query**: *“What regulatory trends suggest opportunities or risks for healthcare vs. financial services sectors?”*

**Agent Response**: The agent analyzes recent regulatory activity and identifies diverging trajectories. Healthcare shows favorable trends with FDA expedited pathways, increased reimbursement rates, and lower enforcement frequency. Financial services faces headwinds with rising enforcement actions, new capital requirements, and enhanced cybersecurity rules. The agent notes that similar regulatory divergence historically preceded significant sector outperformance and provides supporting data.

**Value**: Data-driven sector allocation insights based on regulatory momentum analysis.

## Solution Architecture

### Building on Mycroft’s Regulatory Intelligence Agent

This agent extends Mycroft’s existing Regulatory Intelligence Agent rather than replacing it. The Regulatory Intelligence Agent already handles RSS feed monitoring, document ingestion, urgency scoring, and database storage. The QA layer adds conversational intelligence on top.

**Mycroft’s Regulatory Intelligence Agent (Already Built)**:

- Daily monitoring of SEC, FINRA, CFTC, Federal Register feeds
- Document classification and urgency scoring
- PostgreSQL storage with metadata
- Email alerts for priority items

**New QA Agent Layer (To Build)**:

- Vector database for semantic search
- RAG pipeline for context-aware retrieval
- LLM integration for answer generation
- Portfolio context integration
- Web interface for natural language queries

### How The Agent Works

The agent follows a retrieval-augmented generation workflow. When a user asks a question, their query is converted into a vector embedding and used to search the database of regulatory documents. The most relevant documents are retrieved based on semantic similarity, filtered by metadata like date ranges or agencies, and optionally enhanced with portfolio context. These documents are then passed to a language model along with the original question to generate a comprehensive answer with citations.

The key innovation is portfolio-aware retrieval. When enabled, the agent considers which regulatory changes affect holdings in the portfolio, prioritizing information about sectors and companies that are actually invested in.

### Technology Stack

**Frontend**: React with TypeScript for a responsive chat interface, supporting features like portfolio context toggles, date filters, and citation displays.

**Backend**: FastAPI providing REST API endpoints for queries, document search, and portfolio analysis with async request handling.

**Vector Store**: ChromaDB or similar local vector database for fast semantic search over regulatory documents without requiring external dependencies.

**Embeddings**: Sentence transformers for converting documents and queries into vector representations, enabling semantic similarity search.

**LLM Integration**: Ollama for local model deployment, supporting models like LLaMA-3, Mistral, or other open-source options for cost-efficient inference.

**Database**: Extended PostgreSQL schema building on Mycroft’s existing database, adding vector columns and portfolio holdings tables.

## Contact

**Developer**: Darshan Rajopadhye  
**Email**: rajopadhye.d@northeastern.edu  
**LinkedIn**: [darshanrajopadhye](https://linkedin.com/in/darshanrajopadhye)  
**GitHub**: [Humanitariansai](https://github.com/Humanitariansai)

## License

MIT License

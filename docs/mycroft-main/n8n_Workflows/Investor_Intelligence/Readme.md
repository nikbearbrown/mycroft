# Mycroft Investor Intelligence Agent

An automated n8n workflow that analyzes investors, startups, and AI-sector funding relationships using PostgreSQL and a lightweight chat UI.

Overview

<img width="468" height="222" alt="image" src="https://github.com/user-attachments/assets/2acdf22d-e0e6-4b6d-ae6b-3fab4dfe3569" />



<img width="468" height="230" alt="image" src="https://github.com/user-attachments/assets/515e69e1-3ece-48e2-8160-d4097d2ba458" />


The Investor Intelligence Agent allows users to ask natural-language questions such as:

“Who invested in OpenAI?”

“Tell me about Sequoia Capital”

“Top AI investors this month”

“Show recent funding deals in Robotics”

It connects n8n → PostgreSQL → HTML Chat UI to form a complete investor intelligence system.

<img width="472" height="126" alt="image" src="https://github.com/user-attachments/assets/75c57599-4e05-4297-be08-6643a7a273bf" />

<img width="474" height="239" alt="image" src="https://github.com/user-attachments/assets/c62198cf-79ad-4d91-b96b-71800b993675" />



## 🚀 Features
### 🧠 Natural Language Query Parsing

Detects query type automatically:

Investor profile

Startup → Investor mapping

Recent deals

Top investors

## 🔀 Smart Routing Engine

Each parsed query is routed to the correct SQL node in n8n.

🗄 SQL-Driven Insights

Runs optimized queries on PostgreSQL tables:

investor_links

recent_deals

investor_profiles

## 💬 HTML Chat UI

Includes a simple UI (investor.html) for local testing using webhook responses.

🛡 Graceful Fallbacks

Handles missing data (e.g., OpenAI investor dataset not loaded yet) with friendly messages.

⚙ Two-Part Workflow Architecture

Part 1: Parsing, routing, formatting

Part 2: SQL queries for all investor endpoints

## 🧩 System Architecture
User Query
    ↓
HTML Chat UI (investor.html)
    ↓
Webhook → Parse Question
    ↓
Route by Query Type

    ├── Investor Profile SQL
    
    ├── Startup Investors SQL
    
    ├── Recent Deals SQL
    
    └── Top Investors SQL
            ↓
Format Chatbot Response
            ↓
Return JSON → UI

# 📁 Files Included
# File	Description
Part1-Investor_Agent.json	Workflow for parsing, routing, and formatting
Investor agent – part 2.json	SQL queries + investor intelligence logic
investor.html	Chat interface for local testing
📝 Sample Output
1. Query: “Tell me about Sequoia Capital”
Here is the investor intelligence profile for Sequoia Capital.

Firm: Sequoia Capital
Tier: N/A
Total Investments: 0
Last Activity: N/A
Focus Sectors: N/A

2. Query: “Who invested in OpenAI?”
I don't yet have structured investor data for OpenAI.
Once the ingestion workflows cover this company, this endpoint will list its top investors and deal history.

🛠 What We Built in Sprint 1
1️⃣ Investor Intelligence Chatbot

End-to-end system including:

Natural language parsing

Query classification

SQL routing

Formatted responses

Error handling and fallback messages

2️⃣ SQL Intelligence Engine

Custom queries for:

Investor profiles

Startup’s investors

Top AI investors

Most recent deals

3️⃣ Local Development UI

A clear, easy-to-test HTML interface for debugging and demos.

▶ How to Use
1. Import the workflows into n8n
Part1-Investor_Agent.json
Investor agent – part 2.json

2. Start n8n
n8n start

3. Copy the webhook URL to investor.html

Example:

http://localhost:5670/webhook/investor-chat

4. Open investor.html in your browser

Enter questions like:

“Top AI investors”

“Show deals in Robotics”

“Tell me about Sequoia Capital”

## 🔮 Future Enhancements

Full investor database ingestion pipeline

Tier classification engine

Sector-based investor clustering

Deal timeline analysis

Power BI / Sheets dashboards

Improved LLM query understanding

Fuzzy entity matching

#  🤝 Contributors

Mycroft Project – Humanitarians.AI

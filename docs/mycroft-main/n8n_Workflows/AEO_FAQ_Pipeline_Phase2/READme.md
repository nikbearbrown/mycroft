Market Monitoring Phase 2 — AEO Predictive FAQ Engine

Transforms real-time AI market intelligence into predictive Q&A content structured for answer engines like ChatGPT, Perplexity, and Google AI Overviews.


Overview
Phase 2 is the AEO (Answer Engine Optimization) layer of the Market Monitoring platform. It sits on top of Phase 1 and consumes synthesized topic clusters to predict what questions people will start asking about AI developments in the next 48 hours — then generates authoritative answers before those questions trend.
The result is a continuously growing library of pre-answered questions that are structured for discovery and citation by AI-powered search engines.

What is AEO?
Answer Engine Optimization is the practice of structuring content so that AI-powered answer engines cite it as an authoritative source. Unlike traditional SEO which optimizes for search ranking, AEO optimizes for being the direct answer.
Answer engines favor content that is:

Structured as explicit question-answer pairs
Written in clear, authoritative prose
Backed by multiple corroborating sources
Published before the question peaks in search volume

Phase 2 automates all four of these requirements at scale.

How It Connects to Phase 1
Phase 1 monitors the AI landscape and produces topic clusters — synthesized summaries of what is happening right now across news, community discussions, and research. Each cluster is stored in PostgreSQL with phase2_status = 'pending'.
Phase 2 wakes up automatically when new pending clusters exist. It never re-fetches raw data — it works entirely from Phase 1's synthesized output.
Phase 1 Output (topic clusters)
        ↓
Phase 2 Input (pending clusters)
        ↓
Search intent data fetched
        ↓
Claude predicts 5 questions per cluster
        ↓
Claude generates authoritative answers
        ↓
FAQ pairs stored + published

Architecture
Workflow C — FAQ Generation
StepNodeDescription1Postgres TriggerWatches topic_clusters for phase2_status = pending2Fetch Search IntentPulls People Also Ask data from SerpAPI for each topic3Fetch Historical PatternsQueries past FAQ spikes from the database4Merge ContextCombines cluster summary + search intent + historical data5Claude — Predict QuestionsGenerates 5 predicted questions per cluster6Claude — Generate AnswersWrites authoritative answers for each question7Format OutputStructures FAQ pairs as AEO-ready JSON8Filter Low ConfidenceRemoves pairs below confidence threshold9Store FAQsWrites to predicted_faqs table in PostgreSQL10Update Cluster StatusSets phase2_status = done on processed cluster11PublishSends FAQ pairs to CMS or dashboard via webhook

Data Sources
Inherited from Phase 1

TechCrunch AI RSS
VentureBeat RSS
HackerNews RSS
ArXiv cs.AI RSS
Reddit (r/artificial, r/MachineLearning, r/OpenAI)

Added in Phase 2
SourceTypePurposeSerpAPI People Also AskSearch intentReal questions being typed into Google about the topicAnswerThePublic APISearch intentQuestion variations and related searchesPostgreSQL (Phase 1 DB)Historical patternsPast question clusters from similar eventsQuora AI topicsCommunity questionsLong-form questions from AI practitionersStack Overflow AI tagsDeveloper questionsTechnical questions spiking around similar events

Database Schema
New Table — predicted_faqs
sqlCREATE TABLE predicted_faqs (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER REFERENCES topic_clusters(id),
    question TEXT,
    answer TEXT,
    source_urls TEXT,
    confidence_score INTEGER,
    topic_tag TEXT,
    aeo_status TEXT DEFAULT 'draft',
    created_date TIMESTAMPTZ DEFAULT NOW(),
    published_date TIMESTAMPTZ
);
Updated Field in topic_clusters
sql-- phase2_status transitions:
-- pending   → Phase 1 just wrote this cluster, Phase 2 not yet started
-- in_progress → Phase 2 is currently generating FAQs for this cluster
-- done      → Phase 2 has completed FAQ generation for this cluster

FAQ Output Format
Each generated FAQ pair is structured for maximum AEO discoverability:
json{
  "question": "What does OpenAI's $110B funding round mean for enterprise AI pricing?",
  "answer": "OpenAI's record funding round is likely to accelerate enterprise product development while maintaining competitive pricing pressure on rivals. The $730B valuation signals investor confidence in sustained AI demand, though enterprise customers may see new premium tier offerings emerge within 6-12 months as the company deploys capital toward infrastructure.",
  "source_urls": ["https://techcrunch.com/...", "https://venturebeat.com/..."],
  "confidence_score": 8,
  "topic_tag": "funding",
  "cluster_id": 42,
  "created_date": "2026-02-27T14:00:00Z"
}

Claude Prompting Strategy
Question Prediction Prompt
Given this AI industry development and the search questions people are already asking,
predict the 5 questions that will trend in the next 48 hours.

Focus on questions from: developers, enterprise buyers, investors, regulators.
Avoid questions already answered in mainstream press.
Return as JSON array of strings only.
Answer Generation Prompt
Write an authoritative answer to this question based on the provided intelligence cluster.

Requirements:
- Answer the question directly in the first sentence
- Support with 2-3 sentences of context and implications
- Cite sources by domain name
- Avoid speculation beyond what sources support
- Aim for 80-120 words

Prerequisites

Phase 1 fully operational with data flowing into PostgreSQL
n8n instance (cloud or self-hosted)
Anthropic API key with available credits
SerpAPI key (free tier: 100 searches/month)
PostgreSQL database (same instance as Phase 1)


Setup
1. Run Database Migration
sqlCREATE TABLE predicted_faqs (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER REFERENCES topic_clusters(id),
    question TEXT,
    answer TEXT,
    source_urls TEXT,
    confidence_score INTEGER,
    topic_tag TEXT,
    aeo_status TEXT DEFAULT 'draft',
    created_date TIMESTAMPTZ DEFAULT NOW(),
    published_date TIMESTAMPTZ
);
2. Add API Credentials in n8n
CredentialWhere to GetAnthropic API Keyconsole.anthropic.comSerpAPI Keyserpapi.com/dashboardPostgresSame credential as Phase 1
3. Import Workflow

Copy workflow-c-faq-generation.json
In n8n: Settings → Import from file
Attach all credentials to their respective nodes
Set the Postgres Trigger to watch topic_clusters where phase2_status = pending

4. Activate
Toggle the workflow to Active. Phase 2 will fire automatically each time Phase 1 completes a new cycle.

Environment Variables
ANTHROPIC_API_KEY=sk-ant-...
SERPAPI_KEY=your-serpapi-key
POSTGRES_HOST=your-db-host
POSTGRES_PORT=5432
POSTGRES_DB=your-database
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
N8N_WEBHOOK_URL=https://your-n8n-domain/webhook/faq-output

Project Structure
mycroft-phase2-aeo-engine/
├── README.md
├── workflows/
│   └── workflow-c-faq-generation.json
├── database/
│   └── migration.sql
├── prompts/
│   ├── question-prediction.txt
│   └── answer-generation.txt
└── dashboard/
    └── phase2-dashboard.html

Related

Market Monitoring Phase 1 — Market Monitor


Built With

n8n — Workflow automation
PostgreSQL — Data storage
Anthropic Claude — AI synthesis and generation
SerpAPI — Search intent data
AnswerThePublic — Question research


License
MIT
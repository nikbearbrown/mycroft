# Market Sentiment Analysis - Part 1

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (4 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (1 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/market-sentiment-analysis-part-1.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `market-sentiment-analysis-part-1__fetch-price-data`. Labor: AI. Script called: `scripts/ingest/market-sentiment-analysis-part-1__fetch-price-data.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `market-sentiment-analysis-part-1__fetch-news-headlines`. Labor: AI. Script called: `scripts/ingest/market-sentiment-analysis-part-1__fetch-news-headlines.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `market-sentiment-analysis-part-1__fetch-reddit-mentions`. Labor: AI. Script called: `scripts/ingest/market-sentiment-analysis-part-1__fetch-reddit-mentions.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `market-sentiment-analysis-part-1__parse-question-extract-tickers`. Labor: AI. Script called: `scripts/gigo/market-sentiment-analysis-part-1__parse-question-extract-tickers.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `market-sentiment-analysis-part-1__webhook-trigger`. Labor: AI. Script called: `scripts/tools/market-sentiment-analysis-part-1__webhook-trigger.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `market-sentiment-analysis-part-1__aggregate-calculate-sentiment`. Labor: AI. Script called: `scripts/tools/market-sentiment-analysis-part-1__aggregate-calculate-sentiment.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `market-sentiment-analysis-part-1__ai-analysis-synthesis`. Labor: AI. Script called: `scripts/tools/market-sentiment-analysis-part-1__ai-analysis-synthesis.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `market-sentiment-analysis-part-1__send-to-slack`. Labor: AI. Script called: `scripts/tools/market-sentiment-analysis-part-1__send-to-slack.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/market-sentiment-analysis-part-1/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/market-sentiment-analysis-part-1-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Webhook Trigger | `webhook` | tool |
| 2 | Parse Question & Extract Tickers | `code` | gigo |
| 3 | Fetch Price Data | `httpRequest` | ingest |
| 4 | Fetch News Headlines | `httpRequest` | ingest |
| 5 | Fetch Reddit Mentions | `httpRequest` | ingest |
| 6 | Aggregate & Calculate Sentiment | `code` | tool |
| 7 | AI Analysis & Synthesis | `lmChatAnthropic` | tool |
| 8 | Format Response | `code` | conductor |
| 9 | Send to Slack | `slack` | tool |
| 10 | Send Email | `emailSend` | report |
| 11 | Webhook Response | `respondToWebhook` | report |

## Script Index

- `scripts/ingest/market-sentiment-analysis-part-1__fetch-price-data.py`
- `scripts/ingest/market-sentiment-analysis-part-1__fetch-news-headlines.py`
- `scripts/ingest/market-sentiment-analysis-part-1__fetch-reddit-mentions.py`
- `scripts/gigo/market-sentiment-analysis-part-1__parse-question-extract-tickers.py`
- `scripts/tools/market-sentiment-analysis-part-1__webhook-trigger.py`
- `scripts/tools/market-sentiment-analysis-part-1__aggregate-calculate-sentiment.py`
- `scripts/tools/market-sentiment-analysis-part-1__ai-analysis-synthesis.py`
- `scripts/tools/market-sentiment-analysis-part-1__send-to-slack.py`

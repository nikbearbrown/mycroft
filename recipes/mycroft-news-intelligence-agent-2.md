# Mycroft - News Intelligence Agent

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (4 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (2 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (4 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (5 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroft-news-intelligence-agent-2.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroft-news-intelligence-agent-2__newsapikey`. Labor: AI. Script called: `scripts/ingest/mycroft-news-intelligence-agent-2__newsapikey.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroft-news-intelligence-agent-2__http-request`. Labor: AI. Script called: `scripts/ingest/mycroft-news-intelligence-agent-2__http-request.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroft-news-intelligence-agent-2__http-request1`. Labor: AI. Script called: `scripts/ingest/mycroft-news-intelligence-agent-2__http-request1.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroft-news-intelligence-agent-2__normalizenewsapi`. Labor: AI. Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__normalizenewsapi.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroft-news-intelligence-agent-2__xml`. Labor: AI. Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__xml.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroft-news-intelligence-agent-2__processnewdata`. Labor: AI. Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__processnewdata.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroft-news-intelligence-agent-2__insert-rows-in-a-table`. Labor: AI. Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__insert-rows-in-a-table.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroft-news-intelligence-agent-2__riskcalculator`. Labor: AI. Script called: `scripts/tools/mycroft-news-intelligence-agent-2__riskcalculator.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `mycroft-news-intelligence-agent-2__webhook`. Labor: AI. Script called: `scripts/tools/mycroft-news-intelligence-agent-2__webhook.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-news-intelligence-agent-2/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroft-news-intelligence-agent-2-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Company List | `code` | conductor |
| 2 | Build Query | `code` | conductor |
| 3 | Merge | `merge` | conductor |
| 4 | normalizenewsapi | `code` | gigo |
| 5 | NewsApiKey | `httpRequest` | ingest |
| 6 | HTTP Request | `httpRequest` | ingest |
| 7 | XML | `xml` | gigo |
| 8 | ProcessNewData | `code` | gigo |
| 9 | Edit Fields | `set` | conductor |
| 10 | HTTP Request1 | `httpRequest` | ingest |
| 11 | RiskCalculator | `code` | tool |
| 12 | Insert rows in a table | `postgres` | gigo |
| 13 | Alert Generator Code Node | `code` | report |
| 14 | Send email | `emailSend` | report |
| 15 | DailyGeneratorCode | `code` | report |
| 16 | Webhook | `webhook` | tool |
| 17 | Respond to Webhook | `respondToWebhook` | report |
| 18 | Set Variables | `set` | conductor |

## Script Index

- `scripts/ingest/mycroft-news-intelligence-agent-2__newsapikey.py`
- `scripts/ingest/mycroft-news-intelligence-agent-2__http-request.py`
- `scripts/ingest/mycroft-news-intelligence-agent-2__http-request1.py`
- `scripts/gigo/mycroft-news-intelligence-agent-2__normalizenewsapi.py`
- `scripts/gigo/mycroft-news-intelligence-agent-2__xml.py`
- `scripts/gigo/mycroft-news-intelligence-agent-2__processnewdata.py`
- `scripts/gigo/mycroft-news-intelligence-agent-2__insert-rows-in-a-table.py`
- `scripts/tools/mycroft-news-intelligence-agent-2__riskcalculator.py`
- `scripts/tools/mycroft-news-intelligence-agent-2__webhook.py`

# Contradiction_detection_agent

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (7 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (7 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (2 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/contradiction-detection-agent.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `contradiction-detection-agent__db-fetch-earnings-guidance-signals`. Labor: AI. Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-earnings-guidance-signals.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `contradiction-detection-agent__db-fetch-risk-admissions`. Labor: AI. Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-risk-admissions.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `contradiction-detection-agent__db-fetch-qa-pressure-map`. Labor: AI. Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-qa-pressure-map.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `contradiction-detection-agent__db-fetch-news-signals`. Labor: AI. Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-news-signals.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `contradiction-detection-agent__db-fetch-tech-stack-signals`. Labor: AI. Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-tech-stack-signals.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `contradiction-detection-agent__execute-a-sql-query2`. Labor: AI. Script called: `scripts/ingest/contradiction-detection-agent__execute-a-sql-query2.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `contradiction-detection-agent__http-request`. Labor: AI. Script called: `scripts/ingest/contradiction-detection-agent__http-request.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `contradiction-detection-agent__process-groq-response`. Labor: AI. Script called: `scripts/gigo/contradiction-detection-agent__process-groq-response.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `contradiction-detection-agent__db-insert-contradiction-flag`. Labor: AI. Script called: `scripts/gigo/contradiction-detection-agent__db-insert-contradiction-flag.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `contradiction-detection-agent__execute-a-sql-query`. Labor: AI. Script called: `scripts/gigo/contradiction-detection-agent__execute-a-sql-query.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `contradiction-detection-agent__execute-a-sql-query1`. Labor: AI. Script called: `scripts/gigo/contradiction-detection-agent__execute-a-sql-query1.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: `contradiction-detection-agent__execute-a-sql-query3`. Labor: AI. Script called: `scripts/gigo/contradiction-detection-agent__execute-a-sql-query3.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
13. Step name: `contradiction-detection-agent__process-news-response`. Labor: AI. Script called: `scripts/gigo/contradiction-detection-agent__process-news-response.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
14. Step name: `contradiction-detection-agent__db-save-news-signals`. Labor: AI. Script called: `scripts/gigo/contradiction-detection-agent__db-save-news-signals.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
15. Step name: `contradiction-detection-agent__build-groq-prompt`. Labor: AI. Script called: `scripts/tools/contradiction-detection-agent__build-groq-prompt.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
16. Step name: `contradiction-detection-agent__groq-analyse-contradictions`. Labor: AI. Script called: `scripts/tools/contradiction-detection-agent__groq-analyse-contradictions.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
17. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/contradiction-detection-agent/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/contradiction-detection-agent-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Manual Trigger | `manualTrigger` | conductor |
| 2 | Set Company Input | `set` | conductor |
| 3 | DB: Fetch Earnings Guidance Signals | `postgres` | ingest |
| 4 | DB: Fetch Risk Admissions | `postgres` | ingest |
| 5 | DB: Fetch QA Pressure Map | `postgres` | ingest |
| 6 | DB: Fetch News Signals | `postgres` | ingest |
| 7 | DB: Fetch Tech Stack Signals | `postgres` | ingest |
| 8 | Aggregate All Signals | `code` | conductor |
| 9 | Run Pattern Detection Engine | `code` | conductor |
| 10 | Build Groq Prompt | `code` | tool |
| 11 | LLM Needed? | `if` | conductor |
| 12 | Groq: Analyse Contradictions | `httpRequest` | tool |
| 13 | Process Groq Response | `code` | gigo |
| 14 | No-Flag Passthrough | `code` | conductor |
| 15 | DB: Insert Contradiction Report | `postgres` | report |
| 16 | Fan Out Flags | `code` | conductor |
| 17 | DB: Insert Contradiction Flag | `postgres` | gigo |
| 18 | Build Final Report | `code` | report |
| 19 | Execute a SQL query | `postgres` | gigo |
| 20 | Execute a SQL query1 | `postgres` | gigo |
| 21 | Execute a SQL query2 | `postgres` | ingest |
| 22 | Execute a SQL query3 | `postgres` | gigo |
| 23 | HTTP Request | `httpRequest` | ingest |
| 24 | Process News Response | `code` | gigo |
| 25 | DB: Save News Signals | `postgres` | gigo |
| 26 | Merge | `merge` | conductor |

## Script Index

- `scripts/ingest/contradiction-detection-agent__db-fetch-earnings-guidance-signals.py`
- `scripts/ingest/contradiction-detection-agent__db-fetch-risk-admissions.py`
- `scripts/ingest/contradiction-detection-agent__db-fetch-qa-pressure-map.py`
- `scripts/ingest/contradiction-detection-agent__db-fetch-news-signals.py`
- `scripts/ingest/contradiction-detection-agent__db-fetch-tech-stack-signals.py`
- `scripts/ingest/contradiction-detection-agent__execute-a-sql-query2.py`
- `scripts/ingest/contradiction-detection-agent__http-request.py`
- `scripts/gigo/contradiction-detection-agent__process-groq-response.py`
- `scripts/gigo/contradiction-detection-agent__db-insert-contradiction-flag.py`
- `scripts/gigo/contradiction-detection-agent__execute-a-sql-query.py`
- `scripts/gigo/contradiction-detection-agent__execute-a-sql-query1.py`
- `scripts/gigo/contradiction-detection-agent__execute-a-sql-query3.py`
- `scripts/gigo/contradiction-detection-agent__process-news-response.py`
- `scripts/gigo/contradiction-detection-agent__db-save-news-signals.py`
- `scripts/tools/contradiction-detection-agent__build-groq-prompt.py`
- `scripts/tools/contradiction-detection-agent__groq-analyse-contradictions.py`

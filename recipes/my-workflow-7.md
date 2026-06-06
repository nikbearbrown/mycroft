# My workflow 7

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (13 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (7 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/my-workflow-7.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `my-workflow-7__fetch-all-signals-for-summary`. Labor: AI. Script called: `scripts/ingest/my-workflow-7__fetch-all-signals-for-summary.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `my-workflow-7__db-insert-earnings-call`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-insert-earnings-call.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `my-workflow-7__process-section-response`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__process-section-response.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `my-workflow-7__db-insert-transcript-section`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-insert-transcript-section.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `my-workflow-7__process-guidance-response`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__process-guidance-response.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `my-workflow-7__process-qa-response`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__process-qa-response.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `my-workflow-7__db-insert-guidance-signal`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-insert-guidance-signal.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `my-workflow-7__db-insert-risk-admission`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-insert-risk-admission.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `my-workflow-7__db-insert-qa-pressure`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-insert-qa-pressure.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `my-workflow-7__db-log-agent-run`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-log-agent-run.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `my-workflow-7__process-summary-response`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__process-summary-response.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: `my-workflow-7__db-insert-call-summary`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-insert-call-summary.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
13. Step name: `my-workflow-7__db-mark-call-complete`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__db-mark-call-complete.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
14. Step name: `my-workflow-7__execute-a-sql-query`. Labor: AI. Script called: `scripts/gigo/my-workflow-7__execute-a-sql-query.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
15. Step name: `my-workflow-7__webhook-receive-transcript`. Labor: AI. Script called: `scripts/tools/my-workflow-7__webhook-receive-transcript.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
16. Step name: `my-workflow-7__process-risk-response`. Labor: AI. Script called: `scripts/tools/my-workflow-7__process-risk-response.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
17. Step name: `my-workflow-7__groq-generate-call-summary`. Labor: AI. Script called: `scripts/tools/my-workflow-7__groq-generate-call-summary.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
18. Step name: `my-workflow-7__groq-parse-transcript-sections`. Labor: AI. Script called: `scripts/tools/my-workflow-7__groq-parse-transcript-sections.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
19. Step name: `my-workflow-7__groq-extract-guidance-signals`. Labor: AI. Script called: `scripts/tools/my-workflow-7__groq-extract-guidance-signals.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
20. Step name: `my-workflow-7__groq-extract-risk-admissions`. Labor: AI. Script called: `scripts/tools/my-workflow-7__groq-extract-risk-admissions.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
21. Step name: `my-workflow-7__groq-map-qa-pressure`. Labor: AI. Script called: `scripts/tools/my-workflow-7__groq-map-qa-pressure.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
22. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/my-workflow-7/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/my-workflow-7-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Webhook: Receive Transcript | `webhook` | tool |
| 2 | Validate Input | `code` | conductor |
| 3 | DB: Insert earnings_call | `postgres` | gigo |
| 4 | Set Call Context | `set` | conductor |
| 5 | Process Section Response | `code` | gigo |
| 6 | DB: Insert transcript_section | `postgres` | gigo |
| 7 | Route by Section Type | `switch` | conductor |
| 8 | Process Guidance Response | `code` | gigo |
| 9 | Process Risk Response | `code` | tool |
| 10 | Process QA Response | `code` | gigo |
| 11 | DB: Insert guidance_signal | `postgres` | gigo |
| 12 | DB: Insert risk_admission | `postgres` | gigo |
| 13 | DB: Insert qa_pressure | `postgres` | gigo |
| 14 | DB: Log Agent Run | `postgres` | gigo |
| 15 | Fetch All Signals for Summary | `postgres` | ingest |
| 16 | Process Summary Response | `code` | gigo |
| 17 | DB: Insert call_summary | `postgres` | gigo |
| 18 | DB: Mark Call Complete | `postgres` | gigo |
| 19 | Final Response | `code` | conductor |
| 20 | Webhook Response | `respondToWebhook` | report |
| 21 | Groq: Generate Call Summary | `httpRequest` | tool |
| 22 | Groq: Parse Transcript Sections | `httpRequest` | tool |
| 23 | Groq: Extract Guidance Signals | `httpRequest` | tool |
| 24 | Groq: Extract Risk Admissions | `httpRequest` | tool |
| 25 | Groq: Map QA Pressure | `httpRequest` | tool |
| 26 | Execute a SQL query | `postgres` | gigo |

## Script Index

- `scripts/ingest/my-workflow-7__fetch-all-signals-for-summary.py`
- `scripts/gigo/my-workflow-7__db-insert-earnings-call.py`
- `scripts/gigo/my-workflow-7__process-section-response.py`
- `scripts/gigo/my-workflow-7__db-insert-transcript-section.py`
- `scripts/gigo/my-workflow-7__process-guidance-response.py`
- `scripts/gigo/my-workflow-7__process-qa-response.py`
- `scripts/gigo/my-workflow-7__db-insert-guidance-signal.py`
- `scripts/gigo/my-workflow-7__db-insert-risk-admission.py`
- `scripts/gigo/my-workflow-7__db-insert-qa-pressure.py`
- `scripts/gigo/my-workflow-7__db-log-agent-run.py`
- `scripts/gigo/my-workflow-7__process-summary-response.py`
- `scripts/gigo/my-workflow-7__db-insert-call-summary.py`
- `scripts/gigo/my-workflow-7__db-mark-call-complete.py`
- `scripts/gigo/my-workflow-7__execute-a-sql-query.py`
- `scripts/tools/my-workflow-7__webhook-receive-transcript.py`
- `scripts/tools/my-workflow-7__process-risk-response.py`
- `scripts/tools/my-workflow-7__groq-generate-call-summary.py`
- `scripts/tools/my-workflow-7__groq-parse-transcript-sections.py`
- `scripts/tools/my-workflow-7__groq-extract-guidance-signals.py`
- `scripts/tools/my-workflow-7__groq-extract-risk-admissions.py`
- `scripts/tools/my-workflow-7__groq-map-qa-pressure.py`

# Mycroft - Financial Regulatory Intelligence System - Enhanced

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (3 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (7 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (4 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroft-financial-regulatory-intelligence-system-enhanced.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__normalize-data`. Labor: AI. Script called: `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__normalize-data.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__mark-email-sent`. Labor: AI. Script called: `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__mark-email-sent.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__insert-data-into-db`. Labor: AI. Script called: `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__insert-data-into-db.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__federal-register-securities`. Labor: AI. Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__federal-register-securities.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__sec-press-releases`. Labor: AI. Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__sec-press-releases.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__finra-enforcement-news`. Labor: AI. Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__finra-enforcement-news.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__cftc-regulations`. Labor: AI. Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__cftc-regulations.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__investment-advisor-rules`. Labor: AI. Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__investment-advisor-rules.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__read-write-files-from-disk`. Labor: AI. Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__read-write-files-from-disk.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `mycroft-financial-regulatory-intelligence-system-enhanced__keyword-analysis-urgency-scoring`. Labor: AI. Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__keyword-analysis-urgency-scoring.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-financial-regulatory-intelligence-system-enhanced/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroft-financial-regulatory-intelligence-system-enhanced-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Federal Register - Securities | `rssFeedRead` | tool |
| 2 | SEC Press Releases | `rssFeedRead` | tool |
| 3 | FINRA Enforcement News | `rssFeedRead` | tool |
| 4 | CFTC Regulations | `rssFeedRead` | tool |
| 5 | Investment Advisor Rules | `rssFeedRead` | tool |
| 6 | Merge All Sources | `merge` | conductor |
| 7 | Normalize Data | `code` | gigo |
| 8 | Filter Valid Content | `if` | conductor |
| 9 | Generate HTML Report | `code` | report |
| 10 | High Priority Filter | `if` | conductor |
| 11 | Send Email Alert | `emailSend` | report |
| 12 | Read/Write Files from Disk | `readWriteFile` | tool |
| 13 | If | `if` | conductor |
| 14 | Send email | `emailSend` | report |
| 15 | Schedule Every Day | `scheduleTrigger` | conductor |
| 16 | Generate Email | `code` | report |
| 17 | Mark email sent | `postgres` | gigo |
| 18 | Keyword Analysis & Urgency Scoring | `code` | tool |
| 19 | Insert data into DB | `postgres` | gigo |
| 20 | Prepare Data | `code` | conductor |
| 21 | Code in JavaScript | `code` | conductor |
| 22 | If2 | `if` | conductor |

## Script Index

- `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__normalize-data.py`
- `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__mark-email-sent.py`
- `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__insert-data-into-db.py`
- `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__federal-register-securities.py`
- `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__sec-press-releases.py`
- `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__finra-enforcement-news.py`
- `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__cftc-regulations.py`
- `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__investment-advisor-rules.py`
- `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__read-write-files-from-disk.py`
- `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__keyword-analysis-urgency-scoring.py`

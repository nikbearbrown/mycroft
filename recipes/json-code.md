# Json_code

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (5 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (1 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Risk_Management_Agent/Json_code.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/json-code.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `json-code__fetch-live-prices`. Labor: AI. Script called: `scripts/ingest/json-code__fetch-live-prices.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `json-code__get-portfolio-from-sheets`. Labor: AI. Script called: `scripts/tools/json-code__get-portfolio-from-sheets.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `json-code__calculate-advanced-risk`. Labor: AI. Script called: `scripts/tools/json-code__calculate-advanced-risk.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `json-code__prepare-for-llm`. Labor: AI. Script called: `scripts/tools/json-code__prepare-for-llm.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `json-code__call-groq-api`. Labor: AI. Script called: `scripts/tools/json-code__call-groq-api.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `json-code__log-to-sheets`. Labor: AI. Script called: `scripts/tools/json-code__log-to-sheets.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/json-code/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/json-code-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Risk_Management_Agent/Json_code.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Manual Trigger | `manualTrigger` | conductor |
| 2 | Get Portfolio from Sheets | `googleSheets` | tool |
| 3 | Fetch Live Prices | `httpRequest` | ingest |
| 4 | Calculate Advanced Risk | `code` | tool |
| 5 | Prepare for LLM | `code` | tool |
| 6 | Call Groq API | `httpRequest` | tool |
| 7 | Format Report | `code` | report |
| 8 | Log to Sheets | `googleSheets` | tool |

## Script Index

- `scripts/ingest/json-code__fetch-live-prices.py`
- `scripts/tools/json-code__get-portfolio-from-sheets.py`
- `scripts/tools/json-code__calculate-advanced-risk.py`
- `scripts/tools/json-code__prepare-for-llm.py`
- `scripts/tools/json-code__call-groq-api.py`
- `scripts/tools/json-code__log-to-sheets.py`

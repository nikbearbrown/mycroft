# FORECASTING

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (9 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Forecasting_Agent/Forecasting_Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/forecasting.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `forecasting__alpha-vantage-market-data`. Labor: AI. Script called: `scripts/ingest/forecasting__alpha-vantage-market-data.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `forecasting__execute-a-sql-query`. Labor: AI. Script called: `scripts/gigo/forecasting__execute-a-sql-query.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `forecasting__insert-rows-in-a-table`. Labor: AI. Script called: `scripts/gigo/forecasting__insert-rows-in-a-table.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `forecasting__finbert`. Labor: AI. Script called: `scripts/tools/forecasting__finbert.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/forecasting/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/forecasting-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Forecasting_Agent/Forecasting_Agent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Alpha Vantage Market Data | `httpRequest` | ingest |
| 2 | Configuration | `set` | conductor |
| 3 | FinBert | `httpRequest` | tool |
| 4 | Merge | `merge` | conductor |
| 5 | Code1 | `code` | conductor |
| 6 | If | `if` | conductor |
| 7 | Code2 | `code` | conductor |
| 8 | Execute a SQL query | `postgres` | gigo |
| 9 | Edit Fields | `set` | conductor |
| 10 | When clicking ‘Execute workflow’ | `manualTrigger` | conductor |
| 11 | Insert rows in a table | `postgres` | gigo |
| 12 | Send email | `emailSend` | report |
| 13 | Historical data | `code` | conductor |
| 14 | Code | `code` | conductor |

## Script Index

- `scripts/ingest/forecasting__alpha-vantage-market-data.py`
- `scripts/gigo/forecasting__execute-a-sql-query.py`
- `scripts/gigo/forecasting__insert-rows-in-a-table.py`
- `scripts/tools/forecasting__finbert.py`

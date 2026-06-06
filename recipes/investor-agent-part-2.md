# Investor agent - part 2

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (4 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/investor-agent-part-2.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `investor-agent-part-2__insert-or-update-rows-in-a-table`. Labor: AI. Script called: `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `investor-agent-part-2__execute-a-sql-query`. Labor: AI. Script called: `scripts/gigo/investor-agent-part-2__execute-a-sql-query.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `investor-agent-part-2__insert-or-update-rows-in-a-table1`. Labor: AI. Script called: `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table1.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `investor-agent-part-2__execute-a-sql-query1`. Labor: AI. Script called: `scripts/gigo/investor-agent-part-2__execute-a-sql-query1.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `investor-agent-part-2__rss-read`. Labor: AI. Script called: `scripts/tools/investor-agent-part-2__rss-read.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/investor-agent-part-2/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/investor-agent-part-2-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | When clicking ‘Execute workflow’ | `manualTrigger` | conductor |
| 2 | RSS Read | `rssFeedRead` | tool |
| 3 | Extract Funding Deals | `code` | conductor |
| 4 | Insert or update rows in a table | `postgres` | gigo |
| 5 | extract investor | `code` | conductor |
| 6 | Execute a SQL query | `postgres` | gigo |
| 7 | Build Investor Links | `code` | conductor |
| 8 | Insert or update rows in a table1 | `postgres` | gigo |
| 9 | Execute a SQL query1 | `postgres` | gigo |

## Script Index

- `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table.py`
- `scripts/gigo/investor-agent-part-2__execute-a-sql-query.py`
- `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table1.py`
- `scripts/gigo/investor-agent-part-2__execute-a-sql-query1.py`
- `scripts/tools/investor-agent-part-2__rss-read.py`

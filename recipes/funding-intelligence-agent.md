# Funding Intelligence Agent

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (5 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (3 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (5 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/funding-intelligence-agent.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `funding-intelligence-agent__zyte-techcrunch-scraper`. Labor: AI. Script called: `scripts/ingest/funding-intelligence-agent__zyte-techcrunch-scraper.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `funding-intelligence-agent__zyte-venturebeat`. Labor: AI. Script called: `scripts/ingest/funding-intelligence-agent__zyte-venturebeat.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `funding-intelligence-agent__filter-and-split-vb`. Labor: AI. Script called: `scripts/gigo/funding-intelligence-agent__filter-and-split-vb.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `funding-intelligence-agent__filter-and-split-tech-crunch`. Labor: AI. Script called: `scripts/gigo/funding-intelligence-agent__filter-and-split-tech-crunch.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `funding-intelligence-agent__filter-funding-keywords`. Labor: AI. Script called: `scripts/gigo/funding-intelligence-agent__filter-funding-keywords.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `funding-intelligence-agent__execute-a-sql-query`. Labor: AI. Script called: `scripts/gigo/funding-intelligence-agent__execute-a-sql-query.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `funding-intelligence-agent__insert-rows-in-a-table`. Labor: AI. Script called: `scripts/gigo/funding-intelligence-agent__insert-rows-in-a-table.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `funding-intelligence-agent__html`. Labor: AI. Script called: `scripts/tools/funding-intelligence-agent__html.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `funding-intelligence-agent__html1`. Labor: AI. Script called: `scripts/tools/funding-intelligence-agent__html1.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `funding-intelligence-agent__append-row-in-sheet`. Labor: AI. Script called: `scripts/tools/funding-intelligence-agent__append-row-in-sheet.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/funding-intelligence-agent/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/funding-intelligence-agent-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Schedule Trigger | `scheduleTrigger` | conductor |
| 2 | Zyte_TechCrunch_Scraper | `httpRequest` | ingest |
| 3 | HTML | `html` | tool |
| 4 | Zyte_VentureBeat | `httpRequest` | ingest |
| 5 | Decode_VB | `code` | conductor |
| 6 | Decode_TC | `code` | conductor |
| 7 | HTML1 | `html` | tool |
| 8 | Merge | `merge` | conductor |
| 9 | Filter and split VB | `code` | gigo |
| 10 | Filter and split tech_crunch | `code` | gigo |
| 11 | Filter_Funding_Keywords | `code` | gigo |
| 12 | Classify_Industry | `code` | conductor |
| 13 | Execute a SQL query | `postgres` | gigo |
| 14 | Insert rows in a table | `postgres` | gigo |
| 15 | Send email | `emailSend` | report |
| 16 | Append row in sheet | `googleSheets` | tool |

## Script Index

- `scripts/ingest/funding-intelligence-agent__zyte-techcrunch-scraper.py`
- `scripts/ingest/funding-intelligence-agent__zyte-venturebeat.py`
- `scripts/gigo/funding-intelligence-agent__filter-and-split-vb.py`
- `scripts/gigo/funding-intelligence-agent__filter-and-split-tech-crunch.py`
- `scripts/gigo/funding-intelligence-agent__filter-funding-keywords.py`
- `scripts/gigo/funding-intelligence-agent__execute-a-sql-query.py`
- `scripts/gigo/funding-intelligence-agent__insert-rows-in-a-table.py`
- `scripts/tools/funding-intelligence-agent__html.py`
- `scripts/tools/funding-intelligence-agent__html1.py`
- `scripts/tools/funding-intelligence-agent__append-row-in-sheet.py`

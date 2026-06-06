# Mycroft - SEC_Filings_Analysis

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (8 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (7 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroft-sec-filings-analysis.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroft-sec-filings-analysis__setup-github-repo`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__setup-github-repo.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroft-sec-filings-analysis__setup-python-enviornment-and-output-directories`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__setup-python-enviornment-and-output-directories.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroft-sec-filings-analysis__edgar-fetcher`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__edgar-fetcher.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroft-sec-filings-analysis__financial-analyzer`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__financial-analyzer.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroft-sec-filings-analysis__narrative-parser`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__narrative-parser.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroft-sec-filings-analysis__validate-financial-metrics`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__validate-financial-metrics.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroft-sec-filings-analysis__cleanup-temp-directories`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__cleanup-temp-directories.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroft-sec-filings-analysis__cleanup`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis__cleanup.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-sec-filings-analysis/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroft-sec-filings-analysis-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | When clicking 'Execute workflow' | `manualTrigger` | conductor |
| 2 | If | `if` | conductor |
| 3 | Set Variables | `set` | conductor |
| 4 | Setup Github Repo | `executeCommand` | tool |
| 5 | Set Path Variables | `code` | conductor |
| 6 | Setup Python Enviornment and Output Directories | `executeCommand` | tool |
| 7 | Edgar_Fetcher | `executeCommand` | tool |
| 8 | Validate Fetcher | `code` | conductor |
| 9 | Financial Analyzer | `executeCommand` | tool |
| 10 | Narrative Parser | `executeCommand` | tool |
| 11 | Validate Financial Metrics | `code` | tool |
| 12 | Validate Narrative Content | `code` | conductor |
| 13 | Cleanup Temp Directories | `executeCommand` | tool |
| 14 | Error Handling | `code` | conductor |
| 15 | Cleanup  | `executeCommand` | tool |

## Script Index

- `scripts/tools/mycroft-sec-filings-analysis__setup-github-repo.py`
- `scripts/tools/mycroft-sec-filings-analysis__setup-python-enviornment-and-output-directories.py`
- `scripts/tools/mycroft-sec-filings-analysis__edgar-fetcher.py`
- `scripts/tools/mycroft-sec-filings-analysis__financial-analyzer.py`
- `scripts/tools/mycroft-sec-filings-analysis__narrative-parser.py`
- `scripts/tools/mycroft-sec-filings-analysis__validate-financial-metrics.py`
- `scripts/tools/mycroft-sec-filings-analysis__cleanup-temp-directories.py`
- `scripts/tools/mycroft-sec-filings-analysis__cleanup.py`

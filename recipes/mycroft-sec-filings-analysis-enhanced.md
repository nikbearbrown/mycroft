# Mycroft - SEC_Filings_Analysis_Enhanced

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (20 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroft-sec-filings-analysis-enhanced.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroft-sec-filings-analysis-enhanced__initialize-logging`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__initialize-logging.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroft-sec-filings-analysis-enhanced__setup-github-repo`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-github-repo.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroft-sec-filings-analysis-enhanced__log-repo-cloned`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-repo-cloned.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroft-sec-filings-analysis-enhanced__setup-python-enviornment-and-output-directories`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-python-enviornment-and-output-directories.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroft-sec-filings-analysis-enhanced__log-python-setup`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-python-setup.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroft-sec-filings-analysis-enhanced__edgar-fetcher`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__edgar-fetcher.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroft-sec-filings-analysis-enhanced__log-fetcher-complete`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-fetcher-complete.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroft-sec-filings-analysis-enhanced__financial-analyzer`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__financial-analyzer.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `mycroft-sec-filings-analysis-enhanced__narrative-parser`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__narrative-parser.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `mycroft-sec-filings-analysis-enhanced__validate-financial-metrics`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__validate-financial-metrics.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `mycroft-sec-filings-analysis-enhanced__log-financial-complete`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-financial-complete.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: `mycroft-sec-filings-analysis-enhanced__log-narrative-complete`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-narrative-complete.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
13. Step name: `mycroft-sec-filings-analysis-enhanced__log-merge-complete`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-merge-complete.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
14. Step name: `mycroft-sec-filings-analysis-enhanced__save-to-database`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__save-to-database.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
15. Step name: `mycroft-sec-filings-analysis-enhanced__log-saved`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-saved.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
16. Step name: `mycroft-sec-filings-analysis-enhanced__cleanup-temp-directories`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-temp-directories.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
17. Step name: `mycroft-sec-filings-analysis-enhanced__log-completion`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-completion.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
18. Step name: `mycroft-sec-filings-analysis-enhanced__log-error`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-error.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
19. Step name: `mycroft-sec-filings-analysis-enhanced__cleanup-on-error`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-on-error.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
20. Step name: `mycroft-sec-filings-analysis-enhanced__webhook`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__webhook.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
21. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-sec-filings-analysis-enhanced/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroft-sec-filings-analysis-enhanced-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Set Variables | `set` | conductor |
| 2 | Initialize Logging | `executeCommand` | tool |
| 3 | Setup Github Repo | `executeCommand` | tool |
| 4 | Log: Repo Cloned | `executeCommand` | tool |
| 5 | Set Path Variables | `code` | conductor |
| 6 | Setup Python Enviornment and Output Directories | `executeCommand` | tool |
| 7 | Log: Python Setup | `executeCommand` | tool |
| 8 | Edgar_Fetcher | `executeCommand` | tool |
| 9 | Validate Fetcher | `code` | conductor |
| 10 | Log: Fetcher Complete | `executeCommand` | tool |
| 11 | If | `if` | conductor |
| 12 | Financial Analyzer | `executeCommand` | tool |
| 13 | Narrative Parser | `executeCommand` | tool |
| 14 | Validate Financial Metrics | `code` | tool |
| 15 | Validate Narrative Content | `code` | conductor |
| 16 | Log: Financial Complete | `executeCommand` | tool |
| 17 | Log: Narrative Complete | `executeCommand` | tool |
| 18 | Merge Results | `code` | conductor |
| 19 | Log: Merge Complete | `executeCommand` | tool |
| 20 | Save to Database | `executeCommand` | tool |
| 21 | Log: Saved | `executeCommand` | tool |
| 22 | Cleanup Temp Directories | `executeCommand` | tool |
| 23 | Log Completion | `executeCommand` | tool |
| 24 | Error Handling | `code` | conductor |
| 25 | Log Error | `executeCommand` | tool |
| 26 | Cleanup On Error | `executeCommand` | tool |
| 27 | Webhook | `webhook` | tool |
| 28 | Respond to Webhook | `respondToWebhook` | report |
| 29 | Code in JavaScript | `code` | conductor |

## Script Index

- `scripts/tools/mycroft-sec-filings-analysis-enhanced__initialize-logging.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-github-repo.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-repo-cloned.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-python-enviornment-and-output-directories.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-python-setup.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__edgar-fetcher.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-fetcher-complete.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__financial-analyzer.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__narrative-parser.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__validate-financial-metrics.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-financial-complete.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-narrative-complete.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-merge-complete.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__save-to-database.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-saved.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-temp-directories.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-completion.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-error.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-on-error.py`
- `scripts/tools/mycroft-sec-filings-analysis-enhanced__webhook.py`

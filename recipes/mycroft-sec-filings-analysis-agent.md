# Mycroft - SEC Filings Analysis Agent

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (9 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (6 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroft-sec-filings-analysis-agent.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroft-sec-filings-analysis-agent__parse-results`. Labor: AI. Script called: `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-results.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroft-sec-filings-analysis-agent__parse-both-results`. Labor: AI. Script called: `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-both-results.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroft-sec-filings-analysis-agent__setup-github-repo`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__setup-github-repo.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroft-sec-filings-analysis-agent__setup-python-enviornment-and-output-directories`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__setup-python-enviornment-and-output-directories.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroft-sec-filings-analysis-agent__edgar-fetcher`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__edgar-fetcher.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroft-sec-filings-analysis-agent__financial-analyzer`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__financial-analyzer.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroft-sec-filings-analysis-agent__narrative-parser`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__narrative-parser.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroft-sec-filings-analysis-agent__cleanup`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__cleanup.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `mycroft-sec-filings-analysis-agent__webhook`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__webhook.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `mycroft-sec-filings-analysis-agent__read-write-files-from-disk`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `mycroft-sec-filings-analysis-agent__read-write-files-from-disk1`. Labor: AI. Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk1.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-sec-filings-analysis-agent/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroft-sec-filings-analysis-agent-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | If | `if` | conductor |
| 2 | Set Variables | `set` | conductor |
| 3 | Setup Github Repo | `executeCommand` | tool |
| 4 | Set Path Variables | `code` | conductor |
| 5 | Setup Python Enviornment and Output Directories | `executeCommand` | tool |
| 6 | Edgar_Fetcher | `executeCommand` | tool |
| 7 | Validate Fetcher | `code` | conductor |
| 8 | Financial Analyzer | `executeCommand` | tool |
| 9 | Narrative Parser | `executeCommand` | tool |
| 10 | Error Handling | `code` | conductor |
| 11 | Cleanup  | `executeCommand` | tool |
| 12 | Webhook | `webhook` | tool |
| 13 | Respond to Webhook | `respondToWebhook` | report |
| 14 | If1 | `if` | conductor |
| 15 | Respond to Webhook1 | `respondToWebhook` | report |
| 16 | Read/Write Files from Disk | `readWriteFile` | tool |
| 17 | Read/Write Files from Disk1 | `readWriteFile` | tool |
| 18 | Parse Results | `code` | gigo |
| 19 | Parse Both Results | `code` | gigo |

## Script Index

- `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-results.py`
- `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-both-results.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__setup-github-repo.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__setup-python-enviornment-and-output-directories.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__edgar-fetcher.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__financial-analyzer.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__narrative-parser.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__cleanup.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__webhook.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk.py`
- `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk1.py`

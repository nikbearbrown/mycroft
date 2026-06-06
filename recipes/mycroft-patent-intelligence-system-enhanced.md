# Mycroft - Patent Intelligence System Enhanced

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (17 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (3 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (3 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroft-patent-intelligence-system-enhanced.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroft-patent-intelligence-system-enhanced__initialize-logging`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__initialize-logging.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroft-patent-intelligence-system-enhanced__setup-github-repo`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-github-repo.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroft-patent-intelligence-system-enhanced__log-repo-cloned`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-repo-cloned.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroft-patent-intelligence-system-enhanced__setup-environment-and-output-directories`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-environment-and-output-directories.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroft-patent-intelligence-system-enhanced__log-environment-setup`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-environment-setup.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroft-patent-intelligence-system-enhanced__extract-patents`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__extract-patents.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroft-patent-intelligence-system-enhanced__log-patents-extracted`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-patents-extracted.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroft-patent-intelligence-system-enhanced__process-patents`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__process-patents.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `mycroft-patent-intelligence-system-enhanced__log-processing-complete`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-processing-complete.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `mycroft-patent-intelligence-system-enhanced__read-processed-data`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-processed-data.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `mycroft-patent-intelligence-system-enhanced__read-metrics`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-metrics.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: `mycroft-patent-intelligence-system-enhanced__log-results-loaded`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-results-loaded.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
13. Step name: `mycroft-patent-intelligence-system-enhanced__cleanup-and-save-data`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-and-save-data.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
14. Step name: `mycroft-patent-intelligence-system-enhanced__log-completion`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-completion.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
15. Step name: `mycroft-patent-intelligence-system-enhanced__log-error`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-error.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
16. Step name: `mycroft-patent-intelligence-system-enhanced__cleanup-repository-error`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-repository-error.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
17. Step name: `mycroft-patent-intelligence-system-enhanced__webhook`. Labor: AI. Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__webhook.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
18. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-patent-intelligence-system-enhanced/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroft-patent-intelligence-system-enhanced-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Set Variables | `set` | conductor |
| 2 | Initialize Logging | `executeCommand` | tool |
| 3 | Setup Github Repo | `executeCommand` | tool |
| 4 | Log: Repo Cloned | `executeCommand` | tool |
| 5 | Set Path Variables | `code` | conductor |
| 6 | Setup Environment and Output Directories | `executeCommand` | tool |
| 7 | Log: Environment Setup | `executeCommand` | tool |
| 8 | Extract Patents | `executeCommand` | tool |
| 9 | Log: Patents Extracted | `executeCommand` | tool |
| 10 | Check Extraction Success | `if` | conductor |
| 11 | Process Patents | `executeCommand` | tool |
| 12 | Log: Processing Complete | `executeCommand` | tool |
| 13 | Read Processed Data | `readBinaryFile` | tool |
| 14 | Read Metrics | `readBinaryFile` | tool |
| 15 | Log: Results Loaded | `executeCommand` | tool |
| 16 | Send Report Email | `emailSend` | report |
| 17 | Cleanup and Save Data | `executeCommand` | tool |
| 18 | Log Completion | `executeCommand` | tool |
| 19 | Error Notification | `emailSend` | report |
| 20 | Log Error | `executeCommand` | tool |
| 21 | Cleanup Repository Error | `executeCommand` | tool |
| 22 | Webhook | `webhook` | tool |
| 23 | Respond to Webhook | `respondToWebhook` | report |

## Script Index

- `scripts/tools/mycroft-patent-intelligence-system-enhanced__initialize-logging.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-github-repo.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-repo-cloned.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-environment-and-output-directories.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-environment-setup.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__extract-patents.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-patents-extracted.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__process-patents.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-processing-complete.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-processed-data.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-metrics.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-results-loaded.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-and-save-data.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-completion.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-error.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-repository-error.py`
- `scripts/tools/mycroft-patent-intelligence-system-enhanced__webhook.py`

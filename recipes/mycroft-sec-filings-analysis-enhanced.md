# Mycroft - SEC_Filings_Analysis_Enhanced

## Purpose

Mycroft - SEC_Filings_Analysis_Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - sec_filings_analysis_enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Set Variables | `set` | conductor |
| Initialize Logging | `executeCommand` | tool |
| Setup Github Repo | `executeCommand` | tool |
| Log: Repo Cloned | `executeCommand` | tool |
| Set Path Variables | `code` | conductor |
| Setup Python Enviornment and Output Directories | `executeCommand` | tool |
| Log: Python Setup | `executeCommand` | tool |
| Edgar_Fetcher | `executeCommand` | tool |
| Validate Fetcher | `code` | conductor |
| Log: Fetcher Complete | `executeCommand` | tool |
| If | `if` | conductor |
| Financial Analyzer | `executeCommand` | tool |
| Narrative Parser | `executeCommand` | tool |
| Validate Financial Metrics | `code` | tool |
| Validate Narrative Content | `code` | conductor |
| Log: Financial Complete | `executeCommand` | tool |
| Log: Narrative Complete | `executeCommand` | tool |
| Merge Results | `code` | conductor |
| Log: Merge Complete | `executeCommand` | tool |
| Save to Database | `executeCommand` | tool |
| Log: Saved | `executeCommand` | tool |
| Cleanup Temp Directories | `executeCommand` | tool |
| Log Completion | `executeCommand` | tool |
| Error Handling | `code` | conductor |
| Log Error | `executeCommand` | tool |
| Cleanup On Error | `executeCommand` | tool |
| Webhook | `webhook` | tool |
| Respond to Webhook | `respondToWebhook` | report |
| Code in JavaScript | `code` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (20 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-sec-filings-analysis-enhanced.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-sec-filings-analysis-enhanced --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-sec-filings-analysis-enhanced data/verified/mycroft-sec-filings-analysis-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-sec-filings-analysis-enhanced.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Initialize Logging. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__initialize-logging.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Log: Repo Cloned. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-repo-cloned.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Setup Python Enviornment and Output Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-python-enviornment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Log: Python Setup. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-python-setup.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Edgar_Fetcher. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__edgar-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Log: Fetcher Complete. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-fetcher-complete.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Financial Analyzer. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__financial-analyzer.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Narrative Parser. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__narrative-parser.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Validate Financial Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__validate-financial-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Log: Financial Complete. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-financial-complete.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Log: Narrative Complete. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-narrative-complete.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Log: Merge Complete. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-merge-complete.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Save to Database. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__save-to-database.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Log: Saved. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-saved.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Cleanup Temp Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-temp-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
18. Step name: Log Completion. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-completion.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Log Error. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-error.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
20. Step name: Cleanup On Error. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-on-error.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
21. Step name: Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-enhanced__webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
22. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-enhanced__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
23. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-enhanced__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-sec-filings-analysis-enhanced-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-sec-filings-analysis-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - SEC_Filings_Analysis_Enhanced` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run mycroft-sec-filings-analysis-enhanced --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-sec-filings-analysis-enhanced --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Initialize Logging | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step initialize-logging` | `--no-write` |
| Setup Github Repo | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step setup-github-repo` | `--no-write` |
| Log: Repo Cloned | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-repo-cloned` | `--no-write` |
| Setup Python Enviornment and Output Directories | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step setup-python-enviornment-and-output-directories` | `--no-write` |
| Log: Python Setup | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-python-setup` | `--no-write` |
| Edgar_Fetcher | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step edgar-fetcher` | `--no-write` |
| Log: Fetcher Complete | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-fetcher-complete` | `--no-write` |
| Financial Analyzer | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step financial-analyzer` | `--no-write` |
| Narrative Parser | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step narrative-parser` | `--no-write` |
| Validate Financial Metrics | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step validate-financial-metrics` | `--no-write` |
| Log: Financial Complete | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-financial-complete` | `--no-write` |
| Log: Narrative Complete | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-narrative-complete` | `--no-write` |
| Log: Merge Complete | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-merge-complete` | `--no-write` |
| Save to Database | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step save-to-database` | `--no-write` |
| Log: Saved | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-saved` | `--no-write` |
| Cleanup Temp Directories | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step cleanup-temp-directories` | `--no-write` |
| Log Completion | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-completion` | `--no-write` |
| Log Error | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step log-error` | `--no-write` |
| Cleanup On Error | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step cleanup-on-error` | `--no-write` |
| Webhook | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step webhook` | `--no-write` |
| Respond to Webhook | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step respond-to-webhook` | `--no-write` |
| Produce human report | `snickerdoodle run mycroft-sec-filings-analysis-enhanced --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-sec-filings-analysis-enhanced --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-sec-filings-analysis-enhanced --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-sec-filings-analysis-enhanced --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Initialize Logging | `scripts/tools/mycroft-sec-filings-analysis-enhanced__initialize-logging.py` | tool |
| Setup Github Repo | `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-github-repo.py` | tool |
| Log: Repo Cloned | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-repo-cloned.py` | tool |
| Setup Python Enviornment and Output Directories | `scripts/tools/mycroft-sec-filings-analysis-enhanced__setup-python-enviornment-and-output-directories.py` | tool |
| Log: Python Setup | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-python-setup.py` | tool |
| Edgar_Fetcher | `scripts/tools/mycroft-sec-filings-analysis-enhanced__edgar-fetcher.py` | tool |
| Log: Fetcher Complete | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-fetcher-complete.py` | tool |
| Financial Analyzer | `scripts/tools/mycroft-sec-filings-analysis-enhanced__financial-analyzer.py` | tool |
| Narrative Parser | `scripts/tools/mycroft-sec-filings-analysis-enhanced__narrative-parser.py` | tool |
| Validate Financial Metrics | `scripts/tools/mycroft-sec-filings-analysis-enhanced__validate-financial-metrics.py` | tool |
| Log: Financial Complete | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-financial-complete.py` | tool |
| Log: Narrative Complete | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-narrative-complete.py` | tool |
| Log: Merge Complete | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-merge-complete.py` | tool |
| Save to Database | `scripts/tools/mycroft-sec-filings-analysis-enhanced__save-to-database.py` | tool |
| Log: Saved | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-saved.py` | tool |
| Cleanup Temp Directories | `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-temp-directories.py` | tool |
| Log Completion | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-completion.py` | tool |
| Log Error | `scripts/tools/mycroft-sec-filings-analysis-enhanced__log-error.py` | tool |
| Cleanup On Error | `scripts/tools/mycroft-sec-filings-analysis-enhanced__cleanup-on-error.py` | tool |
| Webhook | `scripts/tools/mycroft-sec-filings-analysis-enhanced__webhook.py` | tool |
| Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-enhanced__respond-to-webhook.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-enhanced__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-sec-filings-analysis-enhanced/` | JSON |
| Verified data | `data/verified/mycroft-sec-filings-analysis-enhanced/` | JSON |
| Agent log | `logs/mycroft-sec-filings-analysis-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-sec-filings-analysis-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json`

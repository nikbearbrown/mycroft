# Mycroft - SEC_Filings_Analysis_Enhanced

## Purpose

Mycroft - SEC_Filings_Analysis_Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - sec_filings_analysis_enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Edgar_Fetcher | executeCommand | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Validate Fetcher | code | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Log: Fetcher Complete | executeCommand | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Set Variables | set | gigo |
| Initialize Logging | executeCommand | gigo |
| Setup Github Repo | executeCommand | gigo |
| Log: Repo Cloned | executeCommand | gigo |
| Set Path Variables | code | gigo |
| Setup Python Enviornment and Output Directories | executeCommand | gigo |
| Log: Python Setup | executeCommand | gigo |
| Edgar_Fetcher | executeCommand | ingest |
| Validate Fetcher | code | ingest |
| Log: Fetcher Complete | executeCommand | ingest |
| If | if | conductor |
| Financial Analyzer | executeCommand | gigo |
| Narrative Parser | executeCommand | gigo |
| Validate Financial Metrics | code | gigo |
| Validate Narrative Content | code | gigo |
| Log: Financial Complete | executeCommand | gigo |
| Log: Narrative Complete | executeCommand | gigo |
| Merge Results | code | conductor |
| Log: Merge Complete | executeCommand | conductor |
| Save to Database | executeCommand | tool |
| Log: Saved | executeCommand | gigo |
| Cleanup Temp Directories | executeCommand | gigo |
| Log Completion | executeCommand | gigo |
| Error Handling | code | gigo |
| Log Error | executeCommand | gigo |
| Cleanup On Error | executeCommand | gigo |
| Webhook | webhook | conductor |
| Respond to Webhook | respondToWebhook | conductor |
| Code in JavaScript | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-sec-filings-analysis-enhanced.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-sec-filings-analysis-enhanced data/verified/n8n-mycroft-sec-filings-analysis-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-sec-filings-analysis-enhanced.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Set Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__set-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
3. Step name: Initialize Logging. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__initialize-logging.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
4. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
5. Step name: Log: Repo Cloned. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-repo-cloned.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
6. Step name: Set Path Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__set-path-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
7. Step name: Setup Python Enviornment and Output Directories. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__setup-python-enviornment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
8. Step name: Log: Python Setup. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-python-setup.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
9. Step name: Edgar_Fetcher. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-enhanced__edgar-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-sec-filings-analysis-enhanced/.
10. Step name: Validate Fetcher. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-enhanced__validate-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-sec-filings-analysis-enhanced/.
11. Step name: Log: Fetcher Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-enhanced__log-fetcher-complete.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-sec-filings-analysis-enhanced/.
12. Step name: Financial Analyzer. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__financial-analyzer.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
13. Step name: Narrative Parser. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__narrative-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
14. Step name: Validate Financial Metrics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__validate-financial-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
15. Step name: Validate Narrative Content. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__validate-narrative-content.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
16. Step name: Log: Financial Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-financial-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
17. Step name: Log: Narrative Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-narrative-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
18. Step name: Save to Database. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-enhanced__save-to-database.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Log: Saved. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-saved.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
20. Step name: Cleanup Temp Directories. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__cleanup-temp-directories.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
21. Step name: Log Completion. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-completion.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
22. Step name: Error Handling. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__error-handling.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
23. Step name: Log Error. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-error.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
24. Step name: Cleanup On Error. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__cleanup-on-error.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
25. Step name: Code in JavaScript. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__code-in-javascript.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-enhanced/.
26. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-enhanced__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroft-sec-filings-analysis-enhanced-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroft-sec-filings-analysis-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - SEC_Filings_Analysis_Enhanced` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Set Variables | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step set-variables` |  |
| Initialize Logging | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step initialize-logging` |  |
| Setup Github Repo | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step setup-github-repo` |  |
| Log: Repo Cloned | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-repo-cloned` |  |
| Set Path Variables | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step set-path-variables` |  |
| Setup Python Enviornment and Output Directories | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step setup-python-enviornment-and-output-directories` |  |
| Log: Python Setup | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-python-setup` |  |
| Edgar_Fetcher | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step edgar-fetcher` | `--sample` |
| Validate Fetcher | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step validate-fetcher` | `--sample` |
| Log: Fetcher Complete | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-fetcher-complete` | `--sample` |
| Financial Analyzer | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step financial-analyzer` |  |
| Narrative Parser | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step narrative-parser` |  |
| Validate Financial Metrics | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step validate-financial-metrics` |  |
| Validate Narrative Content | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step validate-narrative-content` |  |
| Log: Financial Complete | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-financial-complete` |  |
| Log: Narrative Complete | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-narrative-complete` |  |
| Save to Database | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step save-to-database` | `--no-write` |
| Log: Saved | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-saved` |  |
| Cleanup Temp Directories | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step cleanup-temp-directories` |  |
| Log Completion | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-completion` |  |
| Error Handling | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step error-handling` |  |
| Log Error | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step log-error` |  |
| Cleanup On Error | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step cleanup-on-error` |  |
| Code in JavaScript | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step code-in-javascript` |  |
| Produce human report | `snickerdoodle run n8n-mycroft-sec-filings-analysis-enhanced --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroft-sec-filings-analysis-enhanced --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroft-sec-filings-analysis-enhanced --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroft-sec-filings-analysis-enhanced --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Set Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__set-variables.py` | gigo |
| Initialize Logging | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__initialize-logging.py` | gigo |
| Setup Github Repo | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__setup-github-repo.py` | gigo |
| Log: Repo Cloned | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-repo-cloned.py` | gigo |
| Set Path Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__set-path-variables.py` | gigo |
| Setup Python Enviornment and Output Directories | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__setup-python-enviornment-and-output-directories.py` | gigo |
| Log: Python Setup | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-python-setup.py` | gigo |
| Edgar_Fetcher | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-enhanced__edgar-fetcher.py` | ingest |
| Validate Fetcher | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-enhanced__validate-fetcher.py` | ingest |
| Log: Fetcher Complete | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-enhanced__log-fetcher-complete.py` | ingest |
| Financial Analyzer | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__financial-analyzer.py` | gigo |
| Narrative Parser | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__narrative-parser.py` | gigo |
| Validate Financial Metrics | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__validate-financial-metrics.py` | gigo |
| Validate Narrative Content | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__validate-narrative-content.py` | gigo |
| Log: Financial Complete | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-financial-complete.py` | gigo |
| Log: Narrative Complete | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-narrative-complete.py` | gigo |
| Save to Database | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-enhanced__save-to-database.py` | tool |
| Log: Saved | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-saved.py` | gigo |
| Cleanup Temp Directories | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__cleanup-temp-directories.py` | gigo |
| Log Completion | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-completion.py` | gigo |
| Error Handling | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__error-handling.py` | gigo |
| Log Error | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__log-error.py` | gigo |
| Cleanup On Error | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__cleanup-on-error.py` | gigo |
| Code in JavaScript | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-enhanced__code-in-javascript.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-enhanced__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-sec-filings-analysis-enhanced/` | JSON |
| Verified data | `data/verified/n8n-mycroft-sec-filings-analysis-enhanced/` | JSON |
| Agent log | `logs/n8n-mycroft-sec-filings-analysis-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-sec-filings-analysis-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - SEC_Filings_Analysis_Enhanced.json`

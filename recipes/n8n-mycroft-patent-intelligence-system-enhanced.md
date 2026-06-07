# Mycroft - Patent Intelligence System Enhanced

## Purpose

Mycroft - Patent Intelligence System Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - patent intelligence system enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Read Processed Data | readBinaryFile | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Read Metrics | readBinaryFile | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Set Variables | set | gigo |
| Initialize Logging | executeCommand | gigo |
| Setup Github Repo | executeCommand | gigo |
| Log: Repo Cloned | executeCommand | gigo |
| Set Path Variables | code | gigo |
| Setup Environment and Output Directories | executeCommand | gigo |
| Log: Environment Setup | executeCommand | gigo |
| Extract Patents | executeCommand | gigo |
| Log: Patents Extracted | executeCommand | gigo |
| Check Extraction Success | if | conductor |
| Process Patents | executeCommand | gigo |
| Log: Processing Complete | executeCommand | gigo |
| Read Processed Data | readBinaryFile | ingest |
| Read Metrics | readBinaryFile | ingest |
| Log: Results Loaded | executeCommand | gigo |
| Send Report Email | emailSend | tool |
| Cleanup and Save Data | executeCommand | gigo |
| Log Completion | executeCommand | gigo |
| Error Notification | emailSend | conductor |
| Log Error | executeCommand | gigo |
| Cleanup Repository Error | executeCommand | gigo |
| Webhook | webhook | conductor |
| Respond to Webhook | respondToWebhook | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-patent-intelligence-system-enhanced.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-patent-intelligence-system-enhanced data/verified/n8n-mycroft-patent-intelligence-system-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-patent-intelligence-system-enhanced.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Set Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__set-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
3. Step name: Initialize Logging. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__initialize-logging.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
4. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
5. Step name: Log: Repo Cloned. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-repo-cloned.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
6. Step name: Set Path Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__set-path-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
7. Step name: Setup Environment and Output Directories. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__setup-environment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
8. Step name: Log: Environment Setup. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-environment-setup.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
9. Step name: Extract Patents. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__extract-patents.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
10. Step name: Log: Patents Extracted. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-patents-extracted.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
11. Step name: Process Patents. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__process-patents.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
12. Step name: Log: Processing Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-processing-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
13. Step name: Read Processed Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-system-enhanced__read-processed-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-patent-intelligence-system-enhanced/.
14. Step name: Read Metrics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-system-enhanced__read-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-patent-intelligence-system-enhanced/.
15. Step name: Log: Results Loaded. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-results-loaded.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
16. Step name: Send Report Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-system-enhanced__send-report-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Cleanup and Save Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__cleanup-and-save-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
18. Step name: Log Completion. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-completion.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
19. Step name: Log Error. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-error.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
20. Step name: Cleanup Repository Error. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__cleanup-repository-error.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-system-enhanced/.
21. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-system-enhanced__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroft-patent-intelligence-system-enhanced-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroft-patent-intelligence-system-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Patent Intelligence System Enhanced` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Set Variables | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step set-variables` |  |
| Initialize Logging | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step initialize-logging` |  |
| Setup Github Repo | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step setup-github-repo` |  |
| Log: Repo Cloned | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step log-repo-cloned` |  |
| Set Path Variables | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step set-path-variables` |  |
| Setup Environment and Output Directories | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step setup-environment-and-output-directories` |  |
| Log: Environment Setup | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step log-environment-setup` |  |
| Extract Patents | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step extract-patents` |  |
| Log: Patents Extracted | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step log-patents-extracted` |  |
| Process Patents | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step process-patents` |  |
| Log: Processing Complete | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step log-processing-complete` |  |
| Read Processed Data | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step read-processed-data` | `--sample` |
| Read Metrics | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step read-metrics` | `--sample` |
| Log: Results Loaded | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step log-results-loaded` |  |
| Send Report Email | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step send-report-email` | `--no-write` |
| Cleanup and Save Data | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step cleanup-and-save-data` |  |
| Log Completion | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step log-completion` |  |
| Log Error | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step log-error` |  |
| Cleanup Repository Error | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step cleanup-repository-error` |  |
| Produce human report | `snickerdoodle run n8n-mycroft-patent-intelligence-system-enhanced --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroft-patent-intelligence-system-enhanced --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroft-patent-intelligence-system-enhanced --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroft-patent-intelligence-system-enhanced --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Set Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__set-variables.py` | gigo |
| Initialize Logging | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__initialize-logging.py` | gigo |
| Setup Github Repo | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__setup-github-repo.py` | gigo |
| Log: Repo Cloned | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-repo-cloned.py` | gigo |
| Set Path Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__set-path-variables.py` | gigo |
| Setup Environment and Output Directories | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__setup-environment-and-output-directories.py` | gigo |
| Log: Environment Setup | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-environment-setup.py` | gigo |
| Extract Patents | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__extract-patents.py` | gigo |
| Log: Patents Extracted | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-patents-extracted.py` | gigo |
| Process Patents | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__process-patents.py` | gigo |
| Log: Processing Complete | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-processing-complete.py` | gigo |
| Read Processed Data | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-system-enhanced__read-processed-data.py` | ingest |
| Read Metrics | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-system-enhanced__read-metrics.py` | ingest |
| Log: Results Loaded | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-results-loaded.py` | gigo |
| Send Report Email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-system-enhanced__send-report-email.py` | tool |
| Cleanup and Save Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__cleanup-and-save-data.py` | gigo |
| Log Completion | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-completion.py` | gigo |
| Log Error | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__log-error.py` | gigo |
| Cleanup Repository Error | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-system-enhanced__cleanup-repository-error.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-system-enhanced__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-patent-intelligence-system-enhanced/` | JSON |
| Verified data | `data/verified/n8n-mycroft-patent-intelligence-system-enhanced/` | JSON |
| Agent log | `logs/n8n-mycroft-patent-intelligence-system-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-patent-intelligence-system-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json`

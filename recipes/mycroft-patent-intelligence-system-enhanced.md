# Mycroft - Patent Intelligence System Enhanced

## Purpose

Mycroft - Patent Intelligence System Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - patent intelligence system enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Set Variables | `set` | conductor |
| Initialize Logging | `executeCommand` | tool |
| Setup Github Repo | `executeCommand` | tool |
| Log: Repo Cloned | `executeCommand` | tool |
| Set Path Variables | `code` | conductor |
| Setup Environment and Output Directories | `executeCommand` | tool |
| Log: Environment Setup | `executeCommand` | tool |
| Extract Patents | `executeCommand` | tool |
| Log: Patents Extracted | `executeCommand` | tool |
| Check Extraction Success | `if` | conductor |
| Process Patents | `executeCommand` | tool |
| Log: Processing Complete | `executeCommand` | tool |
| Read Processed Data | `readBinaryFile` | tool |
| Read Metrics | `readBinaryFile` | tool |
| Log: Results Loaded | `executeCommand` | tool |
| Send Report Email | `emailSend` | report |
| Cleanup and Save Data | `executeCommand` | tool |
| Log Completion | `executeCommand` | tool |
| Error Notification | `emailSend` | report |
| Log Error | `executeCommand` | tool |
| Cleanup Repository Error | `executeCommand` | tool |
| Webhook | `webhook` | tool |
| Respond to Webhook | `respondToWebhook` | report |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (17 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (3 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (3 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-patent-intelligence-system-enhanced.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-patent-intelligence-system-enhanced --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-patent-intelligence-system-enhanced data/verified/mycroft-patent-intelligence-system-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-patent-intelligence-system-enhanced.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Initialize Logging. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__initialize-logging.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Log: Repo Cloned. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-repo-cloned.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Setup Environment and Output Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-environment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Log: Environment Setup. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-environment-setup.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Extract Patents. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__extract-patents.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Log: Patents Extracted. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-patents-extracted.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Process Patents. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__process-patents.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Log: Processing Complete. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-processing-complete.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Read Processed Data. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-processed-data.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Read Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Log: Results Loaded. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-results-loaded.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Send Report Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__send-report-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
15. Step name: Cleanup and Save Data. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-and-save-data.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Log Completion. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-completion.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Error Notification. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__error-notification.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
18. Step name: Log Error. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-error.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Cleanup Repository Error. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-repository-error.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
20. Step name: Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-enhanced__webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
21. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
22. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-patent-intelligence-system-enhanced-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-patent-intelligence-system-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Patent Intelligence System Enhanced` run.
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
`snickerdoodle run mycroft-patent-intelligence-system-enhanced --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-patent-intelligence-system-enhanced --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Initialize Logging | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step initialize-logging` | `--no-write` |
| Setup Github Repo | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step setup-github-repo` | `--no-write` |
| Log: Repo Cloned | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step log-repo-cloned` | `--no-write` |
| Setup Environment and Output Directories | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step setup-environment-and-output-directories` | `--no-write` |
| Log: Environment Setup | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step log-environment-setup` | `--no-write` |
| Extract Patents | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step extract-patents` | `--no-write` |
| Log: Patents Extracted | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step log-patents-extracted` | `--no-write` |
| Process Patents | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step process-patents` | `--no-write` |
| Log: Processing Complete | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step log-processing-complete` | `--no-write` |
| Read Processed Data | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step read-processed-data` | `--no-write` |
| Read Metrics | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step read-metrics` | `--no-write` |
| Log: Results Loaded | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step log-results-loaded` | `--no-write` |
| Send Report Email | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step send-report-email` | `--no-write` |
| Cleanup and Save Data | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step cleanup-and-save-data` | `--no-write` |
| Log Completion | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step log-completion` | `--no-write` |
| Error Notification | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step error-notification` | `--no-write` |
| Log Error | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step log-error` | `--no-write` |
| Cleanup Repository Error | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step cleanup-repository-error` | `--no-write` |
| Webhook | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step webhook` | `--no-write` |
| Respond to Webhook | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step respond-to-webhook` | `--no-write` |
| Produce human report | `snickerdoodle run mycroft-patent-intelligence-system-enhanced --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-patent-intelligence-system-enhanced --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-patent-intelligence-system-enhanced --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-patent-intelligence-system-enhanced --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Initialize Logging | `scripts/tools/mycroft-patent-intelligence-system-enhanced__initialize-logging.py` | tool |
| Setup Github Repo | `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-github-repo.py` | tool |
| Log: Repo Cloned | `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-repo-cloned.py` | tool |
| Setup Environment and Output Directories | `scripts/tools/mycroft-patent-intelligence-system-enhanced__setup-environment-and-output-directories.py` | tool |
| Log: Environment Setup | `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-environment-setup.py` | tool |
| Extract Patents | `scripts/tools/mycroft-patent-intelligence-system-enhanced__extract-patents.py` | tool |
| Log: Patents Extracted | `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-patents-extracted.py` | tool |
| Process Patents | `scripts/tools/mycroft-patent-intelligence-system-enhanced__process-patents.py` | tool |
| Log: Processing Complete | `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-processing-complete.py` | tool |
| Read Processed Data | `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-processed-data.py` | tool |
| Read Metrics | `scripts/tools/mycroft-patent-intelligence-system-enhanced__read-metrics.py` | tool |
| Log: Results Loaded | `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-results-loaded.py` | tool |
| Send Report Email | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__send-report-email.py` | tool |
| Cleanup and Save Data | `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-and-save-data.py` | tool |
| Log Completion | `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-completion.py` | tool |
| Error Notification | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__error-notification.py` | tool |
| Log Error | `scripts/tools/mycroft-patent-intelligence-system-enhanced__log-error.py` | tool |
| Cleanup Repository Error | `scripts/tools/mycroft-patent-intelligence-system-enhanced__cleanup-repository-error.py` | tool |
| Webhook | `scripts/tools/mycroft-patent-intelligence-system-enhanced__webhook.py` | tool |
| Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__respond-to-webhook.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-enhanced__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-patent-intelligence-system-enhanced/` | JSON |
| Verified data | `data/verified/mycroft-patent-intelligence-system-enhanced/` | JSON |
| Agent log | `logs/mycroft-patent-intelligence-system-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-patent-intelligence-system-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Patent Intelligence System Enhanced.json`

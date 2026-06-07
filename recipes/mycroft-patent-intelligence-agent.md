# Mycroft - Patent Intelligence Agent

## Purpose

Mycroft - Patent Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - patent intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Set Variables | `set` | conductor |
| Setup Github Repo | `executeCommand` | tool |
| Set Path Variables | `code` | conductor |
| Setup Environment and Output Directories | `executeCommand` | tool |
| Extract Patents | `executeCommand` | tool |
| Check Extraction Success | `if` | conductor |
| Process Patents | `executeCommand` | tool |
| Read Processed Data | `readBinaryFile` | tool |
| Read Metrics | `readBinaryFile` | tool |
| Send Report Email | `emailSend` | report |
| Error Notification | `emailSend` | report |
| Cleanup Repository | `executeCommand` | tool |
| Cleanup Repository Error | `executeCommand` | tool |
| Webhook | `webhook` | tool |
| Respond to Webhook | `respondToWebhook` | report |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (9 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (3 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (3 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-patent-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-patent-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-patent-intelligence-agent data/verified/mycroft-patent-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-patent-intelligence-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Setup Environment and Output Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__setup-environment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Extract Patents. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__extract-patents.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Process Patents. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__process-patents.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Read Processed Data. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__read-processed-data.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Read Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__read-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Send Report Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__send-report-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
9. Step name: Error Notification. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__error-notification.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
10. Step name: Cleanup Repository. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__cleanup-repository.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Cleanup Repository Error. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__cleanup-repository-error.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-agent__webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
14. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-patent-intelligence-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-patent-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Patent Intelligence Agent` run.
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
`snickerdoodle run mycroft-patent-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-patent-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Setup Github Repo | `snickerdoodle run mycroft-patent-intelligence-agent --step setup-github-repo` | `--no-write` |
| Setup Environment and Output Directories | `snickerdoodle run mycroft-patent-intelligence-agent --step setup-environment-and-output-directories` | `--no-write` |
| Extract Patents | `snickerdoodle run mycroft-patent-intelligence-agent --step extract-patents` | `--no-write` |
| Process Patents | `snickerdoodle run mycroft-patent-intelligence-agent --step process-patents` | `--no-write` |
| Read Processed Data | `snickerdoodle run mycroft-patent-intelligence-agent --step read-processed-data` | `--no-write` |
| Read Metrics | `snickerdoodle run mycroft-patent-intelligence-agent --step read-metrics` | `--no-write` |
| Send Report Email | `snickerdoodle run mycroft-patent-intelligence-agent --step send-report-email` | `--no-write` |
| Error Notification | `snickerdoodle run mycroft-patent-intelligence-agent --step error-notification` | `--no-write` |
| Cleanup Repository | `snickerdoodle run mycroft-patent-intelligence-agent --step cleanup-repository` | `--no-write` |
| Cleanup Repository Error | `snickerdoodle run mycroft-patent-intelligence-agent --step cleanup-repository-error` | `--no-write` |
| Webhook | `snickerdoodle run mycroft-patent-intelligence-agent --step webhook` | `--no-write` |
| Respond to Webhook | `snickerdoodle run mycroft-patent-intelligence-agent --step respond-to-webhook` | `--no-write` |
| Produce human report | `snickerdoodle run mycroft-patent-intelligence-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-patent-intelligence-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-patent-intelligence-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-patent-intelligence-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Setup Github Repo | `scripts/tools/mycroft-patent-intelligence-agent__setup-github-repo.py` | tool |
| Setup Environment and Output Directories | `scripts/tools/mycroft-patent-intelligence-agent__setup-environment-and-output-directories.py` | tool |
| Extract Patents | `scripts/tools/mycroft-patent-intelligence-agent__extract-patents.py` | tool |
| Process Patents | `scripts/tools/mycroft-patent-intelligence-agent__process-patents.py` | tool |
| Read Processed Data | `scripts/tools/mycroft-patent-intelligence-agent__read-processed-data.py` | tool |
| Read Metrics | `scripts/tools/mycroft-patent-intelligence-agent__read-metrics.py` | tool |
| Send Report Email | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__send-report-email.py` | tool |
| Error Notification | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__error-notification.py` | tool |
| Cleanup Repository | `scripts/tools/mycroft-patent-intelligence-agent__cleanup-repository.py` | tool |
| Cleanup Repository Error | `scripts/tools/mycroft-patent-intelligence-agent__cleanup-repository-error.py` | tool |
| Webhook | `scripts/tools/mycroft-patent-intelligence-agent__webhook.py` | tool |
| Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__respond-to-webhook.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-patent-intelligence-agent/` | JSON |
| Verified data | `data/verified/mycroft-patent-intelligence-agent/` | JSON |
| Agent log | `logs/mycroft-patent-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-patent-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json`

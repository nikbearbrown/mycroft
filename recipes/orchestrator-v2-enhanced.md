# Orchestrator v2 - Enhanced

## Purpose

Orchestrator v2 - Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to orchestrator v2 - enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When chat message received | `chatTrigger` | conductor |
| Ollama Chat Model | `lmChatOllama` | tool |
| The Brain | `chainLlm` | tool |
| The Processor | `code` | gigo |
| The Router | `httpRequest` | ingest |
| Response Processor | `code` | gigo |
| Store Request Log | `n8nDataStore` | tool |
| Store Analytics | `n8nDataStore` | tool |
| Check for Email | `if` | conductor |
| Send Notification | `emailSend` | report |
| Generate Summary | `code` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (4 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (3 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/orchestrator-v2-dev.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/orchestrator-v2-dev.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/orchestrator-v2-enhanced.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run orchestrator-v2-enhanced --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/orchestrator-v2-enhanced data/verified/orchestrator-v2-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/orchestrator-v2-enhanced.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/orchestrator-v2-dev.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Ollama Chat Model. Labor: AI with Human gate.
   Script called: `scripts/tools/orchestrator-v2-enhanced__ollama-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: The Brain. Labor: AI with Human gate.
   Script called: `scripts/tools/orchestrator-v2-enhanced__the-brain.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: The Processor. Labor: AI with Human gate.
   Script called: `scripts/gigo/orchestrator-v2-enhanced__the-processor.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/orchestrator-v2-enhanced/.
5. Step name: The Router. Labor: AI with Human gate.
   Script called: `scripts/ingest/orchestrator-v2-enhanced__the-router.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/orchestrator-v2-enhanced/.
6. Step name: Response Processor. Labor: AI with Human gate.
   Script called: `scripts/gigo/orchestrator-v2-enhanced__response-processor.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/orchestrator-v2-enhanced/.
7. Step name: Store Request Log. Labor: AI with Human gate.
   Script called: `scripts/tools/orchestrator-v2-enhanced__store-request-log.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Store Analytics. Labor: AI with Human gate.
   Script called: `scripts/tools/orchestrator-v2-enhanced__store-analytics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Send Notification. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/orchestrator-v2-enhanced__send-notification.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/orchestrator-v2-enhanced__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/orchestrator-v2-enhanced-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/orchestrator-v2-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Orchestrator v2 - Enhanced` run.
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
`snickerdoodle run orchestrator-v2-enhanced --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run orchestrator-v2-enhanced --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Ollama Chat Model | `snickerdoodle run orchestrator-v2-enhanced --step ollama-chat-model` | `--no-write` |
| The Brain | `snickerdoodle run orchestrator-v2-enhanced --step the-brain` | `--no-write` |
| The Processor | `snickerdoodle run orchestrator-v2-enhanced --step the-processor` |  |
| The Router | `snickerdoodle run orchestrator-v2-enhanced --step the-router` | `--sample` |
| Response Processor | `snickerdoodle run orchestrator-v2-enhanced --step response-processor` |  |
| Store Request Log | `snickerdoodle run orchestrator-v2-enhanced --step store-request-log` | `--no-write` |
| Store Analytics | `snickerdoodle run orchestrator-v2-enhanced --step store-analytics` | `--no-write` |
| Send Notification | `snickerdoodle run orchestrator-v2-enhanced --step send-notification` | `--no-write` |
| Produce human report | `snickerdoodle run orchestrator-v2-enhanced --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate orchestrator-v2-enhanced --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate orchestrator-v2-enhanced --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate orchestrator-v2-enhanced --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Ollama Chat Model | `scripts/tools/orchestrator-v2-enhanced__ollama-chat-model.py` | tool |
| The Brain | `scripts/tools/orchestrator-v2-enhanced__the-brain.py` | tool |
| The Processor | `scripts/gigo/orchestrator-v2-enhanced__the-processor.py` | gigo |
| The Router | `scripts/ingest/orchestrator-v2-enhanced__the-router.py` | ingest |
| Response Processor | `scripts/gigo/orchestrator-v2-enhanced__response-processor.py` | gigo |
| Store Request Log | `scripts/tools/orchestrator-v2-enhanced__store-request-log.py` | tool |
| Store Analytics | `scripts/tools/orchestrator-v2-enhanced__store-analytics.py` | tool |
| Send Notification | `[TODO: DEV] Create or map script path: scripts/tools/orchestrator-v2-enhanced__send-notification.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/orchestrator-v2-enhanced__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/orchestrator-v2-enhanced/` | JSON |
| Verified data | `data/verified/orchestrator-v2-enhanced/` | JSON |
| Agent log | `logs/orchestrator-v2-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/orchestrator-v2-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/orchestrator-v2-dev.json`

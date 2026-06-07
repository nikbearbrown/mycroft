# Mycroft - Patent Intelligence System

## Purpose

Mycroft - Patent Intelligence System defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - patent intelligence system. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
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
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (8 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Intelligence_Agent/Mycroft - Patent Intelligence System.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/mycroft-patent-intelligence-system.md" && rg -n "\[TODO: DEFINE]" "recipes/mycroft-patent-intelligence-system.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/mycroft-patent-intelligence-system/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/mycroft-patent-intelligence-system data/verified/mycroft-patent-intelligence-system -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/mycroft-patent-intelligence-system-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/mycroft-patent-intelligence-system.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/mycroft-patent-intelligence-system-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/mycroft-patent-intelligence-system.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/mycroft-patent-intelligence-system-[DATE].json && test -f reports/generated/mycroft-patent-intelligence-system-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-patent-intelligence-system`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroft-patent-intelligence-system-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-patent-intelligence-system`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/mycroft-patent-intelligence-system/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-patent-intelligence-system-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-patent-intelligence-system`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/mycroft-patent-intelligence-system/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-patent-intelligence-system-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-patent-intelligence-system`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/mycroft-patent-intelligence-system/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-patent-intelligence-system`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-patent-intelligence-system`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/mycroft-patent-intelligence-system-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/mycroft-patent-intelligence-system-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Patent Intelligence System` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run mycroft-patent-intelligence-system --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-patent-intelligence-system --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run mycroft-patent-intelligence-system --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run mycroft-patent-intelligence-system --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run mycroft-patent-intelligence-system --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run mycroft-patent-intelligence-system --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run mycroft-patent-intelligence-system --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run mycroft-patent-intelligence-system --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate mycroft-patent-intelligence-system --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate mycroft-patent-intelligence-system --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate mycroft-patent-intelligence-system --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate mycroft-patent-intelligence-system --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate mycroft-patent-intelligence-system --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate mycroft-patent-intelligence-system --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/mycroft-patent-intelligence-system-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/mycroft-patent-intelligence-system-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/mycroft-patent-intelligence-system-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/mycroft-patent-intelligence-system-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/mycroft-patent-intelligence-system-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/mycroft-patent-intelligence-system-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-patent-intelligence-system/` | JSON |
| Verified data | `data/verified/mycroft-patent-intelligence-system/` | JSON |
| Agent log | `logs/mycroft-patent-intelligence-system-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-patent-intelligence-system-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Intelligence_Agent/Mycroft - Patent Intelligence System.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Intelligence_Agent/Mycroft - Patent Intelligence System.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Mycroft - Patent Intelligence System defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - patent intelligence system. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Intelligence_Agent/Mycroft - Patent Intelligence System.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-patent-intelligence-system.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-patent-intelligence-system --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-patent-intelligence-system data/verified/mycroft-patent-intelligence-system -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-patent-intelligence-system.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Intelligence_Agent/Mycroft - Patent Intelligence System.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Setup Environment and Output Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-setup-environment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Extract Patents. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-extract-patents.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Process Patents. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-process-patents.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Read Processed Data. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-read-processed-data.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Read Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-read-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Send Report Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-send-report-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
9. Step name: Error Notification. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-error-notification.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
10. Step name: Cleanup Repository. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-cleanup-repository.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Cleanup Repository Error. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-patent-intelligence-system-cleanup-repository-error.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-patent-intelligence-system-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

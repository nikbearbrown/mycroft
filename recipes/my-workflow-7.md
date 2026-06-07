# My workflow 7

## Purpose

My workflow 7 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to my workflow 7. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook: Receive Transcript | `webhook` | tool |
| Validate Input | `code` | conductor |
| DB: Insert earnings_call | `postgres` | gigo |
| Set Call Context | `set` | conductor |
| Process Section Response | `code` | gigo |
| DB: Insert transcript_section | `postgres` | gigo |
| Route by Section Type | `switch` | conductor |
| Process Guidance Response | `code` | gigo |
| Process Risk Response | `code` | tool |
| Process QA Response | `code` | gigo |
| DB: Insert guidance_signal | `postgres` | gigo |
| DB: Insert risk_admission | `postgres` | gigo |
| DB: Insert qa_pressure | `postgres` | gigo |
| DB: Log Agent Run | `postgres` | gigo |
| Fetch All Signals for Summary | `postgres` | ingest |
| Process Summary Response | `code` | gigo |
| DB: Insert call_summary | `postgres` | gigo |
| DB: Mark Call Complete | `postgres` | gigo |
| Final Response | `code` | conductor |
| Webhook Response | `respondToWebhook` | report |
| Groq: Generate Call Summary | `httpRequest` | tool |
| Groq: Parse Transcript Sections | `httpRequest` | tool |
| Groq: Extract Guidance Signals | `httpRequest` | tool |
| Groq: Extract Risk Admissions | `httpRequest` | tool |
| Groq: Map QA Pressure | `httpRequest` | tool |
| Execute a SQL query | `postgres` | gigo |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (13 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (7 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/my-workflow-7.md" && rg -n "\[TODO: DEFINE]" "recipes/my-workflow-7.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/my-workflow-7/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/my-workflow-7 data/verified/my-workflow-7 -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/my-workflow-7-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/my-workflow-7.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/my-workflow-7-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/my-workflow-7.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/my-workflow-7-[DATE].json && test -f reports/generated/my-workflow-7-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `my-workflow-7`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/my-workflow-7-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `my-workflow-7`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/my-workflow-7/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `my-workflow-7`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/my-workflow-7/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `my-workflow-7`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/my-workflow-7/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `my-workflow-7`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `my-workflow-7`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/my-workflow-7-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/my-workflow-7-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `My workflow 7` run.
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
`snickerdoodle run my-workflow-7 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run my-workflow-7 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run my-workflow-7 --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run my-workflow-7 --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run my-workflow-7 --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run my-workflow-7 --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run my-workflow-7 --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run my-workflow-7 --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate my-workflow-7 --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate my-workflow-7 --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate my-workflow-7 --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate my-workflow-7 --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate my-workflow-7 --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate my-workflow-7 --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/my-workflow-7-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/my-workflow-7-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/my-workflow-7-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/my-workflow-7-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/my-workflow-7-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/my-workflow-7-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/my-workflow-7/` | JSON |
| Verified data | `data/verified/my-workflow-7/` | JSON |
| Agent log | `logs/my-workflow-7-[DATE].json` | JSON |
| Human report | `reports/generated/my-workflow-7-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

My workflow 7 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to my workflow 7. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow-7.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run my-workflow-7 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/my-workflow-7 data/verified/my-workflow-7 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow-7.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Webhook: Receive Transcript. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-webhook-receive-transcript.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: DB: Insert earnings_call. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-insert-earnings-call.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
4. Step name: Process Section Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-process-section-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
5. Step name: DB: Insert transcript_section. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-insert-transcript-section.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
6. Step name: Process Guidance Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-process-guidance-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
7. Step name: Process Risk Response. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-process-risk-response.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Process QA Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-process-qa-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
9. Step name: DB: Insert guidance_signal. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-insert-guidance-signal.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
10. Step name: DB: Insert risk_admission. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-insert-risk-admission.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
11. Step name: DB: Insert qa_pressure. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-insert-qa-pressure.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
12. Step name: DB: Log Agent Run. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-log-agent-run.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
13. Step name: Fetch All Signals for Summary. Labor: AI with Human gate.
   Script called: `scripts/ingest/my-workflow-7-fetch-all-signals-for-summary.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/my-workflow-7/.
14. Step name: Process Summary Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-process-summary-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
15. Step name: DB: Insert call_summary. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-insert-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
16. Step name: DB: Mark Call Complete. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-db-mark-call-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
17. Step name: Webhook Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-7-webhook-response.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
18. Step name: Groq: Generate Call Summary. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-groq-generate-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Groq: Parse Transcript Sections. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-groq-parse-transcript-sections.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
20. Step name: Groq: Extract Guidance Signals. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-groq-extract-guidance-signals.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
21. Step name: Groq: Extract Risk Admissions. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-groq-extract-risk-admissions.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
22. Step name: Groq: Map QA Pressure. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7-groq-map-qa-pressure.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
23. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7-execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
24. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-7-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

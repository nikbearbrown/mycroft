# Contradiction_detection_agent

## Purpose

Contradiction_detection_agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to contradiction_detection_agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (7 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Set Company Input | `set` | conductor |
| DB: Fetch Earnings Guidance Signals | `postgres` | ingest |
| DB: Fetch Risk Admissions | `postgres` | ingest |
| DB: Fetch QA Pressure Map | `postgres` | ingest |
| DB: Fetch News Signals | `postgres` | ingest |
| DB: Fetch Tech Stack Signals | `postgres` | ingest |
| Aggregate All Signals | `code` | conductor |
| Run Pattern Detection Engine | `code` | conductor |
| Build Groq Prompt | `code` | tool |
| LLM Needed? | `if` | conductor |
| Groq: Analyse Contradictions | `httpRequest` | tool |
| Process Groq Response | `code` | gigo |
| No-Flag Passthrough | `code` | conductor |
| DB: Insert Contradiction Report | `postgres` | report |
| Fan Out Flags | `code` | conductor |
| DB: Insert Contradiction Flag | `postgres` | gigo |
| Build Final Report | `code` | report |
| Execute a SQL query | `postgres` | gigo |
| Execute a SQL query1 | `postgres` | gigo |
| Execute a SQL query2 | `postgres` | ingest |
| Execute a SQL query3 | `postgres` | gigo |
| HTTP Request | `httpRequest` | ingest |
| Process News Response | `code` | gigo |
| DB: Save News Signals | `postgres` | gigo |
| Merge | `merge` | conductor |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (7 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (7 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (2 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/contradiction-detection-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/contradiction-detection-agent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/contradiction-detection-agent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/contradiction-detection-agent data/verified/contradiction-detection-agent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/contradiction-detection-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/contradiction-detection-agent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/contradiction-detection-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/contradiction-detection-agent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/contradiction-detection-agent-[DATE].json && test -f reports/generated/contradiction-detection-agent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/contradiction-detection-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/contradiction-detection-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/contradiction-detection-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/contradiction-detection-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/contradiction-detection-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Contradiction_detection_agent` run.
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
`snickerdoodle run contradiction-detection-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run contradiction-detection-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run contradiction-detection-agent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run contradiction-detection-agent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run contradiction-detection-agent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run contradiction-detection-agent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run contradiction-detection-agent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run contradiction-detection-agent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate contradiction-detection-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate contradiction-detection-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate contradiction-detection-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate contradiction-detection-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate contradiction-detection-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate contradiction-detection-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/contradiction-detection-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/contradiction-detection-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/contradiction-detection-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/contradiction-detection-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/contradiction-detection-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/contradiction-detection-agent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/contradiction-detection-agent/` | JSON |
| Verified data | `data/verified/contradiction-detection-agent/` | JSON |
| Agent log | `logs/contradiction-detection-agent-[DATE].json` | JSON |
| Human report | `reports/generated/contradiction-detection-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Contradiction_detection_agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to contradiction_detection_agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/contradiction-detection-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run contradiction-detection-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/contradiction-detection-agent data/verified/contradiction-detection-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/contradiction-detection-agent.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: DB: Fetch Earnings Guidance Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-earnings-guidance-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
3. Step name: DB: Fetch Risk Admissions. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-risk-admissions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
4. Step name: DB: Fetch QA Pressure Map. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-qa-pressure-map.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
5. Step name: DB: Fetch News Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-news-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
6. Step name: DB: Fetch Tech Stack Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-tech-stack-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
7. Step name: Build Groq Prompt. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-build-groq-prompt.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Groq: Analyse Contradictions. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-groq-analyse-contradictions.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Process Groq Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-process-groq-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
10. Step name: DB: Insert Contradiction Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent-db-insert-contradiction-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
11. Step name: DB: Insert Contradiction Flag. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-db-insert-contradiction-flag.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
12. Step name: Build Final Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent-build-final-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
13. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-execute-a-sql-query2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
14. Step name: Execute a SQL query1. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-execute-a-sql-query1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
15. Step name: Execute a SQL query2. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-execute-a-sql-query2.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
16. Step name: Execute a SQL query3. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-execute-a-sql-query3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
17. Step name: HTTP Request. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-http-request.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
18. Step name: Process News Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-process-news-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
19. Step name: DB: Save News Signals. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-db-save-news-signals.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
20. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

# TechStackComparativeAgentWorkflow

## Purpose

TechStackComparativeAgentWorkflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to techstackcomparativeagentworkflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Validate Input | `if` | conductor |
| Prepare Variables | `set` | conductor |
| GitHub: Get Repos | `httpRequest` | ingest |
| Batch Repos (Top 5) | `splitInBatches` | conductor |
| GitHub: Get Languages | `httpRequest` | ingest |
| Aggregate Repo Data | `set` | conductor |
| arXiv: Search Papers | `httpRequest` | ingest |
| Error: Invalid Input | `set` | conductor |
| Parse arXiv XML | `code` | gigo |
| When clicking ‘Execute workflow’ | `manualTrigger` | conductor |
| Split Out | `splitOut` | gigo |
| set | `set` | conductor |
| set1 | `set` | conductor |
| Convert to File | `convertToFile` | gigo |
| Edit Fields | `set` | conductor |
| Edit Fields1 | `set` | conductor |
| Code | `code` | conductor |
| Edit Fields2 | `set` | conductor |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (3 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (12 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/techstackcomparativeagentworkflow.md" && rg -n "\[TODO: DEFINE]" "recipes/techstackcomparativeagentworkflow.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/techstackcomparativeagentworkflow/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/techstackcomparativeagentworkflow data/verified/techstackcomparativeagentworkflow -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/techstackcomparativeagentworkflow-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/techstackcomparativeagentworkflow.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/techstackcomparativeagentworkflow-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/techstackcomparativeagentworkflow.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/techstackcomparativeagentworkflow-[DATE].json && test -f reports/generated/techstackcomparativeagentworkflow-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/techstackcomparativeagentworkflow-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `techstackcomparativeagentworkflow`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/techstackcomparativeagentworkflow-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `techstackcomparativeagentworkflow`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/techstackcomparativeagentworkflow/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `techstackcomparativeagentworkflow`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/techstackcomparativeagentworkflow/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `techstackcomparativeagentworkflow`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/techstackcomparativeagentworkflow/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/techstackcomparativeagentworkflow-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `techstackcomparativeagentworkflow`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/techstackcomparativeagentworkflow-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `techstackcomparativeagentworkflow`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/techstackcomparativeagentworkflow-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/techstackcomparativeagentworkflow-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `TechStackComparativeAgentWorkflow` run.
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
`snickerdoodle run techstackcomparativeagentworkflow --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run techstackcomparativeagentworkflow --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run techstackcomparativeagentworkflow --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run techstackcomparativeagentworkflow --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run techstackcomparativeagentworkflow --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run techstackcomparativeagentworkflow --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run techstackcomparativeagentworkflow --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run techstackcomparativeagentworkflow --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate techstackcomparativeagentworkflow --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate techstackcomparativeagentworkflow --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate techstackcomparativeagentworkflow --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate techstackcomparativeagentworkflow --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate techstackcomparativeagentworkflow --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate techstackcomparativeagentworkflow --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/techstackcomparativeagentworkflow-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/techstackcomparativeagentworkflow-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/techstackcomparativeagentworkflow-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/techstackcomparativeagentworkflow-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/techstackcomparativeagentworkflow-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/techstackcomparativeagentworkflow-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/techstackcomparativeagentworkflow/` | JSON |
| Verified data | `data/verified/techstackcomparativeagentworkflow/` | JSON |
| Agent log | `logs/techstackcomparativeagentworkflow-[DATE].json` | JSON |
| Human report | `reports/generated/techstackcomparativeagentworkflow-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

TechStackComparativeAgentWorkflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to techstackcomparativeagentworkflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/techstackcomparativeagentworkflow.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run techstackcomparativeagentworkflow --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/techstackcomparativeagentworkflow data/verified/techstackcomparativeagentworkflow -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/techstackcomparativeagentworkflow.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: GitHub: Get Repos. Labor: AI with Human gate.
   Script called: `scripts/ingest/techstackcomparativeagentworkflow-github-get-repos.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/techstackcomparativeagentworkflow/.
3. Step name: GitHub: Get Languages. Labor: AI with Human gate.
   Script called: `scripts/ingest/techstackcomparativeagentworkflow-github-get-languages.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/techstackcomparativeagentworkflow/.
4. Step name: arXiv: Search Papers. Labor: AI with Human gate.
   Script called: `scripts/ingest/techstackcomparativeagentworkflow-arxiv-search-papers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/techstackcomparativeagentworkflow/.
5. Step name: Parse arXiv XML. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow-parse-arxiv-xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/techstackcomparativeagentworkflow/.
6. Step name: Split Out. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow-split-out.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/techstackcomparativeagentworkflow/.
7. Step name: Convert to File. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow-convert-to-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/techstackcomparativeagentworkflow/.
8. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/techstackcomparativeagentworkflow-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

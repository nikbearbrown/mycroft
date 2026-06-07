# TechStackComparativeAgentWorkflow

## Purpose

TechStackComparativeAgentWorkflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to techstackcomparativeagentworkflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| GitHub: Get Repos | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| GitHub: Get Languages | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| arXiv: Search Papers | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Validate Input | if | conductor |
| Prepare Variables | set | gigo |
| GitHub: Get Repos | httpRequest | ingest |
| Batch Repos (Top 5) | splitInBatches | conductor |
| GitHub: Get Languages | httpRequest | ingest |
| Aggregate Repo Data | set | gigo |
| arXiv: Search Papers | httpRequest | ingest |
| Error: Invalid Input | set | gigo |
| Parse arXiv XML | code | gigo |
| When clicking ‘Execute workflow’ | manualTrigger | conductor |
| Split Out | splitOut | conductor |
| set | set | gigo |
| set1 | set | gigo |
| Convert to File | convertToFile | gigo |
| Edit Fields | set | gigo |
| Edit Fields1 | set | gigo |
| Code | code | gigo |
| Edit Fields2 | set | gigo |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json` | Yes |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/n8n-techstackcomparativeagentworkflow.md" && rg -n "\[TODO: DEFINE]" "recipes/n8n-techstackcomparativeagentworkflow.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/n8n-techstackcomparativeagentworkflow/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/n8n-techstackcomparativeagentworkflow data/verified/n8n-techstackcomparativeagentworkflow -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/n8n-techstackcomparativeagentworkflow-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/n8n-techstackcomparativeagentworkflow.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/n8n-techstackcomparativeagentworkflow-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/n8n-techstackcomparativeagentworkflow.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/n8n-techstackcomparativeagentworkflow-[DATE].json && test -f reports/generated/n8n-techstackcomparativeagentworkflow-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-techstackcomparativeagentworkflow-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-techstackcomparativeagentworkflow`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/n8n-techstackcomparativeagentworkflow-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-techstackcomparativeagentworkflow`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/n8n-techstackcomparativeagentworkflow/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-techstackcomparativeagentworkflow-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-techstackcomparativeagentworkflow`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/n8n-techstackcomparativeagentworkflow/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-techstackcomparativeagentworkflow-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-techstackcomparativeagentworkflow`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/n8n-techstackcomparativeagentworkflow/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-techstackcomparativeagentworkflow-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-techstackcomparativeagentworkflow`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-techstackcomparativeagentworkflow-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-techstackcomparativeagentworkflow`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/n8n-techstackcomparativeagentworkflow-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/n8n-techstackcomparativeagentworkflow-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `TechStackComparativeAgentWorkflow` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-techstackcomparativeagentworkflow --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-techstackcomparativeagentworkflow --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/n8n-techstackcomparativeagentworkflow-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/n8n-techstackcomparativeagentworkflow-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/n8n-techstackcomparativeagentworkflow-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/n8n-techstackcomparativeagentworkflow-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/n8n-techstackcomparativeagentworkflow-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/n8n-techstackcomparativeagentworkflow-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-techstackcomparativeagentworkflow/` | JSON |
| Verified data | `data/verified/n8n-techstackcomparativeagentworkflow/` | JSON |
| Agent log | `logs/n8n-techstackcomparativeagentworkflow-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-techstackcomparativeagentworkflow-[DATE].md` | Markdown |
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
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-techstackcomparativeagentworkflow.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-techstackcomparativeagentworkflow --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-techstackcomparativeagentworkflow data/verified/n8n-techstackcomparativeagentworkflow -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-techstackcomparativeagentworkflow.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Prepare Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-prepare-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
3. Step name: GitHub: Get Repos. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow-github-get-repos.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-techstackcomparativeagentworkflow/.
4. Step name: GitHub: Get Languages. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow-github-get-languages.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-techstackcomparativeagentworkflow/.
5. Step name: Aggregate Repo Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-aggregate-repo-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
6. Step name: arXiv: Search Papers. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow-arxiv-search-papers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-techstackcomparativeagentworkflow/.
7. Step name: Error: Invalid Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-error-invalid-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
8. Step name: Parse arXiv XML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-parse-arxiv-xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
9. Step name: set. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-set.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
10. Step name: set1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-set1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
11. Step name: Convert to File. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-convert-to-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
12. Step name: Edit Fields. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-edit-fields.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
13. Step name: Edit Fields1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-edit-fields1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
14. Step name: Code. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-code.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
15. Step name: Edit Fields2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow-edit-fields2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
16. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-techstackcomparativeagentworkflow-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

# Mycroft - SEC_Filings_Analysis

## Purpose

Mycroft - SEC_Filings_Analysis defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - sec_filings_analysis. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Edgar_Fetcher | executeCommand | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Validate Fetcher | code | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| When clicking 'Execute workflow' | manualTrigger | conductor |
| If | if | conductor |
| Set Variables | set | gigo |
| Setup Github Repo | executeCommand | gigo |
| Set Path Variables | code | gigo |
| Setup Python Enviornment and Output Directories | executeCommand | gigo |
| Edgar_Fetcher | executeCommand | ingest |
| Validate Fetcher | code | ingest |
| Financial Analyzer | executeCommand | gigo |
| Narrative Parser | executeCommand | gigo |
| Validate Financial Metrics | code | gigo |
| Validate Narrative Content | code | gigo |
| Cleanup Temp Directories | executeCommand | gigo |
| Error Handling | code | gigo |
| Cleanup | executeCommand | gigo |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json` | Yes |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/n8n-mycroft-sec-filings-analysis.md" && rg -n "\[TODO: DEFINE]" "recipes/n8n-mycroft-sec-filings-analysis.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/n8n-mycroft-sec-filings-analysis/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/n8n-mycroft-sec-filings-analysis data/verified/n8n-mycroft-sec-filings-analysis -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/n8n-mycroft-sec-filings-analysis-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/n8n-mycroft-sec-filings-analysis.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/n8n-mycroft-sec-filings-analysis-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/n8n-mycroft-sec-filings-analysis.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/n8n-mycroft-sec-filings-analysis-[DATE].json && test -f reports/generated/n8n-mycroft-sec-filings-analysis-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-mycroft-sec-filings-analysis-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-sec-filings-analysis`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/n8n-mycroft-sec-filings-analysis-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-sec-filings-analysis`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/n8n-mycroft-sec-filings-analysis/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-mycroft-sec-filings-analysis-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-sec-filings-analysis`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/n8n-mycroft-sec-filings-analysis/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-mycroft-sec-filings-analysis-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-sec-filings-analysis`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/n8n-mycroft-sec-filings-analysis/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-mycroft-sec-filings-analysis-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-sec-filings-analysis`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-mycroft-sec-filings-analysis-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-sec-filings-analysis`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/n8n-mycroft-sec-filings-analysis-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/n8n-mycroft-sec-filings-analysis-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - SEC_Filings_Analysis` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-sec-filings-analysis --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-sec-filings-analysis --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run n8n-mycroft-sec-filings-analysis --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run n8n-mycroft-sec-filings-analysis --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run n8n-mycroft-sec-filings-analysis --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run n8n-mycroft-sec-filings-analysis --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run n8n-mycroft-sec-filings-analysis --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run n8n-mycroft-sec-filings-analysis --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate n8n-mycroft-sec-filings-analysis --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate n8n-mycroft-sec-filings-analysis --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate n8n-mycroft-sec-filings-analysis --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate n8n-mycroft-sec-filings-analysis --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate n8n-mycroft-sec-filings-analysis --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate n8n-mycroft-sec-filings-analysis --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/n8n-mycroft-sec-filings-analysis-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/n8n-mycroft-sec-filings-analysis-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/n8n-mycroft-sec-filings-analysis-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/n8n-mycroft-sec-filings-analysis-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/n8n-mycroft-sec-filings-analysis-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/n8n-mycroft-sec-filings-analysis-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-sec-filings-analysis/` | JSON |
| Verified data | `data/verified/n8n-mycroft-sec-filings-analysis/` | JSON |
| Agent log | `logs/n8n-mycroft-sec-filings-analysis-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-sec-filings-analysis-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Mycroft - SEC_Filings_Analysis defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - sec_filings_analysis. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-sec-filings-analysis.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-sec-filings-analysis --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-sec-filings-analysis data/verified/n8n-mycroft-sec-filings-analysis -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-sec-filings-analysis.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Set Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-set-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
3. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
4. Step name: Set Path Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-set-path-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
5. Step name: Setup Python Enviornment and Output Directories. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-setup-python-enviornment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
6. Step name: Edgar_Fetcher. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-edgar-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-sec-filings-analysis/.
7. Step name: Validate Fetcher. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-validate-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-sec-filings-analysis/.
8. Step name: Financial Analyzer. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-financial-analyzer.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
9. Step name: Narrative Parser. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-narrative-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
10. Step name: Validate Financial Metrics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-validate-financial-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
11. Step name: Validate Narrative Content. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-validate-narrative-content.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
12. Step name: Cleanup Temp Directories. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-cleanup-temp-directories.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
13. Step name: Error Handling. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-error-handling.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
14. Step name: Cleanup. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-cleanup.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis/.
15. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

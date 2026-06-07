# MycroftResearchAgent_2.0

## Purpose

MycroftResearchAgent_2.0 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroftresearchagent_2.0. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (4 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| When clicking ‘Execute workflow’ | `manualTrigger` | conductor |
| Company Input | `set` | conductor |
| Get Financial Overview1 | `httpRequest` | ingest |
| Get Income Statement1 | `httpRequest` | ingest |
| Process Company Data1 | `code` | gigo |
| Google Search Patent | `httpRequest` | ingest |
| Process Patent Data1 | `code` | gigo |
| Process Financial Data1 | `code` | gigo |
| Generate Analysis1 | `code` | tool |
| Generate Final Report1 | `code` | report |
| Merge | `merge` | conductor |
| Get Earnings Data | `httpRequest` | ingest |
| Process Earnings Data | `code` | gigo |
| Get Competitive Analysis | `code` | tool |
| Merge Competitive Analysis | `code` | tool |
| Investment Report | `code` | report |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (4 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (4 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (3 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (3 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/mycroftresearchagent-2-0.md" && rg -n "\[TODO: DEFINE]" "recipes/mycroftresearchagent-2-0.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/mycroftresearchagent-2-0/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/mycroftresearchagent-2-0 data/verified/mycroftresearchagent-2-0 -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/mycroftresearchagent-2-0-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/mycroftresearchagent-2-0.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/mycroftresearchagent-2-0-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/mycroftresearchagent-2-0.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/mycroftresearchagent-2-0-[DATE].json && test -f reports/generated/mycroftresearchagent-2-0-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroftresearchagent-2-0-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroftresearchagent-2-0`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroftresearchagent-2-0-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroftresearchagent-2-0`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/mycroftresearchagent-2-0/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroftresearchagent-2-0-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroftresearchagent-2-0`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/mycroftresearchagent-2-0/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroftresearchagent-2-0-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroftresearchagent-2-0`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/mycroftresearchagent-2-0/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroftresearchagent-2-0-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroftresearchagent-2-0`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroftresearchagent-2-0-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroftresearchagent-2-0`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/mycroftresearchagent-2-0-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/mycroftresearchagent-2-0-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `MycroftResearchAgent_2.0` run.
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
`snickerdoodle run mycroftresearchagent-2-0 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroftresearchagent-2-0 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run mycroftresearchagent-2-0 --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run mycroftresearchagent-2-0 --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run mycroftresearchagent-2-0 --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run mycroftresearchagent-2-0 --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run mycroftresearchagent-2-0 --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run mycroftresearchagent-2-0 --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate mycroftresearchagent-2-0 --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate mycroftresearchagent-2-0 --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate mycroftresearchagent-2-0 --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate mycroftresearchagent-2-0 --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate mycroftresearchagent-2-0 --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate mycroftresearchagent-2-0 --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/mycroftresearchagent-2-0-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/mycroftresearchagent-2-0-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/mycroftresearchagent-2-0-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/mycroftresearchagent-2-0-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/mycroftresearchagent-2-0-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/mycroftresearchagent-2-0-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroftresearchagent-2-0/` | JSON |
| Verified data | `data/verified/mycroftresearchagent-2-0/` | JSON |
| Agent log | `logs/mycroftresearchagent-2-0-[DATE].json` | JSON |
| Human report | `reports/generated/mycroftresearchagent-2-0-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

MycroftResearchAgent_2.0 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroftresearchagent_2.0. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroftresearchagent-2-0.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroftresearchagent-2-0 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroftresearchagent-2-0 data/verified/mycroftresearchagent-2-0 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroftresearchagent-2-0.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Get Financial Overview1. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroftresearchagent-2-0-get-financial-overview1.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroftresearchagent-2-0/.
3. Step name: Get Income Statement1. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroftresearchagent-2-0-get-income-statement1.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroftresearchagent-2-0/.
4. Step name: Process Company Data1. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroftresearchagent-2-0-process-company-data1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroftresearchagent-2-0/.
5. Step name: Google Search Patent. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroftresearchagent-2-0-google-search-patent.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroftresearchagent-2-0/.
6. Step name: Process Patent Data1. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroftresearchagent-2-0-process-patent-data1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroftresearchagent-2-0/.
7. Step name: Process Financial Data1. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroftresearchagent-2-0-process-financial-data1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroftresearchagent-2-0/.
8. Step name: Generate Analysis1. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroftresearchagent-2-0-generate-analysis1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Generate Final Report1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroftresearchagent-2-0-generate-final-report1.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
10. Step name: Get Earnings Data. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroftresearchagent-2-0-get-earnings-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroftresearchagent-2-0/.
11. Step name: Process Earnings Data. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroftresearchagent-2-0-process-earnings-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroftresearchagent-2-0/.
12. Step name: Get Competitive Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroftresearchagent-2-0-get-competitive-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Merge Competitive Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroftresearchagent-2-0-merge-competitive-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Investment Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroftresearchagent-2-0-investment-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
15. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroftresearchagent-2-0-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

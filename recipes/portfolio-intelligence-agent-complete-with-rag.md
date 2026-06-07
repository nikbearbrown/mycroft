# Portfolio Intelligence Agent - Complete with RAG

## Purpose

Portfolio Intelligence Agent - Complete with RAG defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to portfolio intelligence agent - complete with rag. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Schedule Trigger | `scheduleTrigger` | conductor |
| Read Holdings File | `readBinaryFile` | tool |
| Parse JSON Holdings | `code` | gigo |
| Calculate Portfolio Metrics | `code` | tool |
| Read Previous Summaries | `readBinaryFile` | tool |
| Fetch & Extract Stock Prices | `code` | conductor |
| Parse Summaries CSV | `code` | gigo |
| Calculate Daily Return | `code` | report |
| Read Knowledge Base1 | `readWriteFile` | tool |
| Parse Knowledge Base CSV | `code` | gigo |
| Read Portfolio History CSV | `readWriteFile` | tool |
| Parse Portfolio History Data | `code` | gigo |
| Build Portfolio Analysis | `code` | tool |
| RAG-Retrieve Context | `code` | conductor |
| Extract AI Summary | `code` | conductor |
| Split Out | `splitOut` | gigo |
| Generate AI Summary (Groq) | `httpRequest` | tool |
| Send a message | `gmail` | tool |
| Append Portfolio History1 | `readWriteFile` | tool |
| Convert Holdings to CSV | `convertToFile` | gigo |
| Convert Summary to CSV | `convertToFile` | gigo |
| Append Daily Summary | `readWriteFile` | tool |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (7 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (10 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (5 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/portfolio-intelligence-agent-complete-with-rag.md" && rg -n "\[TODO: DEFINE]" "recipes/portfolio-intelligence-agent-complete-with-rag.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/portfolio-intelligence-agent-complete-with-rag/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/portfolio-intelligence-agent-complete-with-rag data/verified/portfolio-intelligence-agent-complete-with-rag -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/portfolio-intelligence-agent-complete-with-rag-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/portfolio-intelligence-agent-complete-with-rag.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/portfolio-intelligence-agent-complete-with-rag-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/portfolio-intelligence-agent-complete-with-rag.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/portfolio-intelligence-agent-complete-with-rag-[DATE].json && test -f reports/generated/portfolio-intelligence-agent-complete-with-rag-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `portfolio-intelligence-agent-complete-with-rag`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/portfolio-intelligence-agent-complete-with-rag-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `portfolio-intelligence-agent-complete-with-rag`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/portfolio-intelligence-agent-complete-with-rag/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `portfolio-intelligence-agent-complete-with-rag`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/portfolio-intelligence-agent-complete-with-rag/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `portfolio-intelligence-agent-complete-with-rag`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/portfolio-intelligence-agent-complete-with-rag/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `portfolio-intelligence-agent-complete-with-rag`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `portfolio-intelligence-agent-complete-with-rag`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/portfolio-intelligence-agent-complete-with-rag-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/portfolio-intelligence-agent-complete-with-rag-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Portfolio Intelligence Agent - Complete with RAG` run.
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
`snickerdoodle run portfolio-intelligence-agent-complete-with-rag --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run portfolio-intelligence-agent-complete-with-rag --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/portfolio-intelligence-agent-complete-with-rag-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/portfolio-intelligence-agent-complete-with-rag-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/portfolio-intelligence-agent-complete-with-rag-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/portfolio-intelligence-agent-complete-with-rag-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/portfolio-intelligence-agent-complete-with-rag/` | JSON |
| Verified data | `data/verified/portfolio-intelligence-agent-complete-with-rag/` | JSON |
| Agent log | `logs/portfolio-intelligence-agent-complete-with-rag-[DATE].json` | JSON |
| Human report | `reports/generated/portfolio-intelligence-agent-complete-with-rag-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Portfolio Intelligence Agent - Complete with RAG defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to portfolio intelligence agent - complete with rag. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/portfolio-intelligence-agent-complete-with-rag.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/portfolio-intelligence-agent-complete-with-rag data/verified/portfolio-intelligence-agent-complete-with-rag -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/portfolio-intelligence-agent-complete-with-rag.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Read Holdings File. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-read-holdings-file.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Parse JSON Holdings. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-parse-json-holdings.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
4. Step name: Calculate Portfolio Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-calculate-portfolio-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Read Previous Summaries. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-read-previous-summaries.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Parse Summaries CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-parse-summaries-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
7. Step name: Calculate Daily Return. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/portfolio-intelligence-agent-complete-with-rag-calculate-daily-return.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
8. Step name: Read Knowledge Base1. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-read-knowledge-base1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Parse Knowledge Base CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-parse-knowledge-base-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
10. Step name: Read Portfolio History CSV. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-read-portfolio-history-csv.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Parse Portfolio History Data. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-parse-portfolio-history-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
12. Step name: Build Portfolio Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-build-portfolio-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Split Out. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-split-out.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
14. Step name: Generate AI Summary (Groq). Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-generate-ai-summary-groq.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Send a message. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-send-a-message.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Append Portfolio History1. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-append-portfolio-history1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Convert Holdings to CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-convert-holdings-to-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
18. Step name: Convert Summary to CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag-convert-summary-to-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
19. Step name: Append Daily Summary. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag-append-daily-summary.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
20. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/portfolio-intelligence-agent-complete-with-rag-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

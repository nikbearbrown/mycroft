# rag grader

## Purpose

The rag grader evaluates whether a RAG answer is relevant to the question, grounded in retrieved facts, and free of obvious factual or internal conflicts before the answer is trusted in a Mycroft report.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Question | String | Calling workflow log or chat run | Confirm source is allowed, current, and rate-safe before live fetch. |
| Student answer / RAG output | String | Calling workflow log | Confirm source is allowed, current, and rate-safe before live fetch. |
| Retrieved facts | Array/string | `intermediateSteps`, sources, or observations from calling workflow | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json` | Yes |
| Question | String | Calling workflow log or chat run | Yes |
| Student answer / RAG output | String | Calling workflow log | Yes |
| Retrieved facts | Array/string | `intermediateSteps`, sources, or observations from calling workflow | Yes |
| Model credential | Environment variable | `OPENROUTER_API_KEY` for future live grading adapter | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/rag-grader.md" && rg -n "\[TODO: DEFINE]" "recipes/rag-grader.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/rag-grader/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/rag-grader data/verified/rag-grader -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/rag-grader-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/rag-grader.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/rag-grader-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/rag-grader.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/rag-grader-[DATE].json && test -f reports/generated/rag-grader-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/rag-grader-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `rag-grader`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/rag-grader-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `rag-grader`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/rag-grader/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/rag-grader-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `rag-grader`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/rag-grader/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/rag-grader-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `rag-grader`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/rag-grader/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/rag-grader-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `rag-grader`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/rag-grader-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `rag-grader`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/rag-grader-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/rag-grader-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `rag grader` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if the question or answer is missing.
- Stop if groundedness is requested but no facts, sources, or intermediate observations are present.
- Stop if any parser output lacks the required boolean field.
- Stop if the merged grade omits correctness, relevance, or groundedness.
- Stop before treating a local lexical grade as a definitive semantic evaluation without human review.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run rag-grader --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run rag-grader --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run rag-grader --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run rag-grader --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run rag-grader --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run rag-grader --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run rag-grader --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run rag-grader --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate rag-grader --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate rag-grader --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate rag-grader --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate rag-grader --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate rag-grader --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate rag-grader --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/rag-grader-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/rag-grader-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/rag-grader-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/rag-grader-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/rag-grader-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/rag-grader-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/rag-grader/` | JSON |
| Verified data | `data/verified/rag-grader/` | JSON |
| Agent log | `logs/rag-grader-[DATE].json` | JSON |
| Human report | `reports/generated/rag-grader-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json` | `test -f "data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

The rag grader evaluates whether a RAG answer is relevant to the question, grounded in retrieved facts, and free of obvious factual or internal conflicts before the answer is trusted in a Mycroft report.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/rag-grader.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run rag-grader --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/rag-grader data/verified/rag-grader -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/rag-grader.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: rag_relevance_grader. Labor: AI with Human gate.
   Script called: `scripts/tools/rag-relevance-grader.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: rag_groundedness_grader. Labor: AI with Human gate.
   Script called: `scripts/tools/rag-groundedness-grader.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: rag_correctness_grader. Labor: AI with Human gate.
   Script called: `scripts/tools/rag-correctness-grader.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: parse_relevance_grade. Labor: AI with Human gate.
   Script called: `scripts/gigo/parse-relevance-grade.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/rag-grader/.
6. Step name: merge_rag_grades. Labor: AI with Human gate.
   Script called: `scripts/tools/merge-rag-grades.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/rag-grader-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

# rag grader

## Purpose

The rag grader evaluates whether a RAG answer is relevant to the question, grounded in retrieved facts, and free of obvious factual or internal conflicts before the answer is trusted in a Mycroft report.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Question | String | Calling workflow log or chat run | Confirm source is allowed, current, and rate-safe before live fetch. |
| Student answer / RAG output | String | Calling workflow log | Confirm source is allowed, current, and rate-safe before live fetch. |
| Retrieved facts | Array/string | `intermediateSteps`, sources, or observations from calling workflow | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: rag_relevance_grader. Labor: AI with Human gate.
   Script called: `scripts/tools/rag_relevance_grader.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: rag_groundedness_grader. Labor: AI with Human gate.
   Script called: `scripts/tools/rag_groundedness_grader.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: rag_correctness_grader. Labor: AI with Human gate.
   Script called: `scripts/tools/rag_correctness_grader.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: parse_relevance_grade. Labor: AI with Human gate.
   Script called: `scripts/gigo/parse_relevance_grade.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/rag-grader/.
6. Step name: merge_rag_grades. Labor: AI with Human gate.
   Script called: `scripts/tools/merge_rag_grades.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/rag-grader__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/rag-grader-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/rag-grader-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `rag grader` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| rag_relevance_grader | `snickerdoodle run rag-grader --step rag-relevance-grader` | `--no-write` |
| rag_groundedness_grader | `snickerdoodle run rag-grader --step rag-groundedness-grader` | `--no-write` |
| rag_correctness_grader | `snickerdoodle run rag-grader --step rag-correctness-grader` | `--no-write` |
| parse_relevance_grade | `snickerdoodle run rag-grader --step parse-relevance-grade` |  |
| merge_rag_grades | `snickerdoodle run rag-grader --step merge-rag-grades` | `--no-write` |
| Produce human report | `snickerdoodle run rag-grader --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate rag-grader --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate rag-grader --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate rag-grader --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| rag_relevance_grader | `scripts/tools/rag_relevance_grader.py` | tool |
| rag_groundedness_grader | `scripts/tools/rag_groundedness_grader.py` | tool |
| rag_correctness_grader | `scripts/tools/rag_correctness_grader.py` | tool |
| parse_relevance_grade | `scripts/gigo/parse_relevance_grade.py` | gigo |
| merge_rag_grades | `scripts/tools/merge_rag_grades.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/rag-grader__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/rag-grader/` | JSON |
| Verified data | `data/verified/rag-grader/` | JSON |
| Agent log | `logs/rag-grader-[DATE].json` | JSON |
| Human report | `reports/generated/rag-grader-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json`

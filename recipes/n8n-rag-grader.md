# rag grader

## Purpose

rag grader defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to rag grader. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Original workflow sources | [TODO: DEV] Parse original workflow node types. | [TODO: DATA SOURCE] Extract source URLs or paths from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| OpenRouter Chat Model2 | lmChatOpenRouter | gigo |
| Merge7 | merge | conductor |
| Correctness grader | agent | gigo |
| Relevance grader | agent | gigo |
| Groundedness grader | agent | gigo |
| Groundedness output parser | outputParserStructured | gigo |
| Relevance output parser | outputParserStructured | gigo |
| Correctness output parser | outputParserStructured | gigo |
| Dummy node | code | gigo |
| OpenRouter Chat Model | lmChatOpenRouter | gigo |
| OpenRouter Chat Model1 | lmChatOpenRouter | gigo |
| Start | executeWorkflowTrigger | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-rag-grader.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-rag-grader --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-rag-grader data/verified/n8n-rag-grader -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-rag-grader.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: OpenRouter Chat Model2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__openrouter-chat-model2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
3. Step name: Correctness grader. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__correctness-grader.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
4. Step name: Relevance grader. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__relevance-grader.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
5. Step name: Groundedness grader. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__groundedness-grader.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
6. Step name: Groundedness output parser. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__groundedness-output-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
7. Step name: Relevance output parser. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__relevance-output-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
8. Step name: Correctness output parser. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__correctness-output-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
9. Step name: Dummy node. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__dummy-node.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
10. Step name: OpenRouter Chat Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__openrouter-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
11. Step name: OpenRouter Chat Model1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__openrouter-chat-model1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-rag-grader/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-rag-grader__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-rag-grader-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-rag-grader-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `rag grader` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-rag-grader --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-rag-grader --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| OpenRouter Chat Model2 | `snickerdoodle run n8n-rag-grader --step openrouter-chat-model2` |  |
| Correctness grader | `snickerdoodle run n8n-rag-grader --step correctness-grader` |  |
| Relevance grader | `snickerdoodle run n8n-rag-grader --step relevance-grader` |  |
| Groundedness grader | `snickerdoodle run n8n-rag-grader --step groundedness-grader` |  |
| Groundedness output parser | `snickerdoodle run n8n-rag-grader --step groundedness-output-parser` |  |
| Relevance output parser | `snickerdoodle run n8n-rag-grader --step relevance-output-parser` |  |
| Correctness output parser | `snickerdoodle run n8n-rag-grader --step correctness-output-parser` |  |
| Dummy node | `snickerdoodle run n8n-rag-grader --step dummy-node` |  |
| OpenRouter Chat Model | `snickerdoodle run n8n-rag-grader --step openrouter-chat-model` |  |
| OpenRouter Chat Model1 | `snickerdoodle run n8n-rag-grader --step openrouter-chat-model1` |  |
| Produce human report | `snickerdoodle run n8n-rag-grader --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-rag-grader --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-rag-grader --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-rag-grader --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| OpenRouter Chat Model2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__openrouter-chat-model2.py` | gigo |
| Correctness grader | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__correctness-grader.py` | gigo |
| Relevance grader | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__relevance-grader.py` | gigo |
| Groundedness grader | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__groundedness-grader.py` | gigo |
| Groundedness output parser | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__groundedness-output-parser.py` | gigo |
| Relevance output parser | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__relevance-output-parser.py` | gigo |
| Correctness output parser | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__correctness-output-parser.py` | gigo |
| Dummy node | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__dummy-node.py` | gigo |
| OpenRouter Chat Model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__openrouter-chat-model.py` | gigo |
| OpenRouter Chat Model1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-rag-grader__openrouter-chat-model1.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-rag-grader__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-rag-grader/` | JSON |
| Verified data | `data/verified/n8n-rag-grader/` | JSON |
| Agent log | `logs/n8n-rag-grader-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-rag-grader-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/rag grader.json`

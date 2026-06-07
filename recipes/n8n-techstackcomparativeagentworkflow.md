# TechStackComparativeAgentWorkflow

## Purpose

TechStackComparativeAgentWorkflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to techstackcomparativeagentworkflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| GitHub: Get Repos | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| GitHub: Get Languages | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| arXiv: Search Papers | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Prepare Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__prepare-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
3. Step name: GitHub: Get Repos. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow__github-get-repos.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-techstackcomparativeagentworkflow/.
4. Step name: GitHub: Get Languages. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow__github-get-languages.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-techstackcomparativeagentworkflow/.
5. Step name: Aggregate Repo Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__aggregate-repo-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
6. Step name: arXiv: Search Papers. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow__arxiv-search-papers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-techstackcomparativeagentworkflow/.
7. Step name: Error: Invalid Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__error-invalid-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
8. Step name: Parse arXiv XML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__parse-arxiv-xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
9. Step name: set. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__set.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
10. Step name: set1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__set1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
11. Step name: Convert to File. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__convert-to-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
12. Step name: Edit Fields. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__edit-fields.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
13. Step name: Edit Fields1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__edit-fields1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
14. Step name: Code. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__code.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
15. Step name: Edit Fields2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__edit-fields2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-techstackcomparativeagentworkflow/.
16. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-techstackcomparativeagentworkflow__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-techstackcomparativeagentworkflow-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-techstackcomparativeagentworkflow-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `TechStackComparativeAgentWorkflow` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| Prepare Variables | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step prepare-variables` |  |
| GitHub: Get Repos | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step github-get-repos` | `--sample` |
| GitHub: Get Languages | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step github-get-languages` | `--sample` |
| Aggregate Repo Data | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step aggregate-repo-data` |  |
| arXiv: Search Papers | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step arxiv-search-papers` | `--sample` |
| Error: Invalid Input | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step error-invalid-input` |  |
| Parse arXiv XML | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step parse-arxiv-xml` |  |
| set | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step set` |  |
| set1 | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step set1` |  |
| Convert to File | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step convert-to-file` |  |
| Edit Fields | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step edit-fields` |  |
| Edit Fields1 | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step edit-fields1` |  |
| Code | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step code` |  |
| Edit Fields2 | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step edit-fields2` |  |
| Produce human report | `snickerdoodle run n8n-techstackcomparativeagentworkflow --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-techstackcomparativeagentworkflow --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Prepare Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__prepare-variables.py` | gigo |
| GitHub: Get Repos | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow__github-get-repos.py` | ingest |
| GitHub: Get Languages | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow__github-get-languages.py` | ingest |
| Aggregate Repo Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__aggregate-repo-data.py` | gigo |
| arXiv: Search Papers | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-techstackcomparativeagentworkflow__arxiv-search-papers.py` | ingest |
| Error: Invalid Input | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__error-invalid-input.py` | gigo |
| Parse arXiv XML | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__parse-arxiv-xml.py` | gigo |
| set | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__set.py` | gigo |
| set1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__set1.py` | gigo |
| Convert to File | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__convert-to-file.py` | gigo |
| Edit Fields | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__edit-fields.py` | gigo |
| Edit Fields1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__edit-fields1.py` | gigo |
| Code | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__code.py` | gigo |
| Edit Fields2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-techstackcomparativeagentworkflow__edit-fields2.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-techstackcomparativeagentworkflow__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-techstackcomparativeagentworkflow/` | JSON |
| Verified data | `data/verified/n8n-techstackcomparativeagentworkflow/` | JSON |
| Agent log | `logs/n8n-techstackcomparativeagentworkflow-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-techstackcomparativeagentworkflow-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json`

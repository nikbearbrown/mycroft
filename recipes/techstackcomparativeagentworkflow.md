# TechStackComparativeAgentWorkflow

## Purpose

TechStackComparativeAgentWorkflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to techstackcomparativeagentworkflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: GitHub: Get Repos. Labor: AI with Human gate.
   Script called: `scripts/ingest/techstackcomparativeagentworkflow__github-get-repos.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/techstackcomparativeagentworkflow/.
3. Step name: GitHub: Get Languages. Labor: AI with Human gate.
   Script called: `scripts/ingest/techstackcomparativeagentworkflow__github-get-languages.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/techstackcomparativeagentworkflow/.
4. Step name: arXiv: Search Papers. Labor: AI with Human gate.
   Script called: `scripts/ingest/techstackcomparativeagentworkflow__arxiv-search-papers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/techstackcomparativeagentworkflow/.
5. Step name: Parse arXiv XML. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow__parse-arxiv-xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/techstackcomparativeagentworkflow/.
6. Step name: Split Out. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow__split-out.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/techstackcomparativeagentworkflow/.
7. Step name: Convert to File. Labor: AI with Human gate.
   Script called: `scripts/gigo/techstackcomparativeagentworkflow__convert-to-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/techstackcomparativeagentworkflow/.
8. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/techstackcomparativeagentworkflow__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/techstackcomparativeagentworkflow-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/techstackcomparativeagentworkflow-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `TechStackComparativeAgentWorkflow` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| GitHub: Get Repos | `snickerdoodle run techstackcomparativeagentworkflow --step github-get-repos` | `--sample` |
| GitHub: Get Languages | `snickerdoodle run techstackcomparativeagentworkflow --step github-get-languages` | `--sample` |
| arXiv: Search Papers | `snickerdoodle run techstackcomparativeagentworkflow --step arxiv-search-papers` | `--sample` |
| Parse arXiv XML | `snickerdoodle run techstackcomparativeagentworkflow --step parse-arxiv-xml` |  |
| Split Out | `snickerdoodle run techstackcomparativeagentworkflow --step split-out` |  |
| Convert to File | `snickerdoodle run techstackcomparativeagentworkflow --step convert-to-file` |  |
| Produce human report | `snickerdoodle run techstackcomparativeagentworkflow --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate techstackcomparativeagentworkflow --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate techstackcomparativeagentworkflow --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate techstackcomparativeagentworkflow --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| GitHub: Get Repos | `scripts/ingest/techstackcomparativeagentworkflow__github-get-repos.py` | ingest |
| GitHub: Get Languages | `scripts/ingest/techstackcomparativeagentworkflow__github-get-languages.py` | ingest |
| arXiv: Search Papers | `scripts/ingest/techstackcomparativeagentworkflow__arxiv-search-papers.py` | ingest |
| Parse arXiv XML | `scripts/gigo/techstackcomparativeagentworkflow__parse-arxiv-xml.py` | gigo |
| Split Out | `scripts/gigo/techstackcomparativeagentworkflow__split-out.py` | gigo |
| Convert to File | `scripts/gigo/techstackcomparativeagentworkflow__convert-to-file.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/techstackcomparativeagentworkflow__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/techstackcomparativeagentworkflow/` | JSON |
| Verified data | `data/verified/techstackcomparativeagentworkflow/` | JSON |
| Agent log | `logs/techstackcomparativeagentworkflow-[DATE].json` | JSON |
| Human report | `reports/generated/techstackcomparativeagentworkflow-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json`

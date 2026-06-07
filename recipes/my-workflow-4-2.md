# My workflow 4

## Purpose

My workflow 4 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to my workflow 4. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Prepare Variables | `set` | conductor |
| GitHub: Get Repos | `httpRequest` | ingest |
| Batch Repos | `splitInBatches` | conductor |
| GitHub: Get Languages | `httpRequest` | ingest |
| Aggregate Repo Data | `set` | conductor |
| arXiv: Search Papers | `httpRequest` | ingest |
| Parse arXiv XML | `code` | gigo |
| Manual Trigger | `manualTrigger` | conductor |
| Input: Companies | `set` | conductor |
| Format Language Data | `set` | conductor |
| Format Research Data | `set` | conductor |
| Code | `code` | conductor |
| Code1 | `code` | conductor |
| Code2 | `code` | conductor |
| Code3 | `code` | conductor |
| Code4 | `code` | conductor |
| Code5 | `code` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (13 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow-4-2.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run my-workflow-4-2 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/my-workflow-4-2 data/verified/my-workflow-4-2 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow-4-2.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: GitHub: Get Repos. Labor: AI with Human gate.
   Script called: `scripts/ingest/my-workflow-4-2__github-get-repos.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/my-workflow-4-2/.
3. Step name: GitHub: Get Languages. Labor: AI with Human gate.
   Script called: `scripts/ingest/my-workflow-4-2__github-get-languages.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/my-workflow-4-2/.
4. Step name: arXiv: Search Papers. Labor: AI with Human gate.
   Script called: `scripts/ingest/my-workflow-4-2__arxiv-search-papers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/my-workflow-4-2/.
5. Step name: Parse arXiv XML. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-4-2__parse-arxiv-xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-4-2/.
6. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-4-2__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/my-workflow-4-2-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/my-workflow-4-2-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `My workflow 4` run.
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
`snickerdoodle run my-workflow-4-2 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run my-workflow-4-2 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| GitHub: Get Repos | `snickerdoodle run my-workflow-4-2 --step github-get-repos` | `--sample` |
| GitHub: Get Languages | `snickerdoodle run my-workflow-4-2 --step github-get-languages` | `--sample` |
| arXiv: Search Papers | `snickerdoodle run my-workflow-4-2 --step arxiv-search-papers` | `--sample` |
| Parse arXiv XML | `snickerdoodle run my-workflow-4-2 --step parse-arxiv-xml` |  |
| Produce human report | `snickerdoodle run my-workflow-4-2 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate my-workflow-4-2 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate my-workflow-4-2 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate my-workflow-4-2 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| GitHub: Get Repos | `scripts/ingest/my-workflow-4-2__github-get-repos.py` | ingest |
| GitHub: Get Languages | `scripts/ingest/my-workflow-4-2__github-get-languages.py` | ingest |
| arXiv: Search Papers | `scripts/ingest/my-workflow-4-2__arxiv-search-papers.py` | ingest |
| Parse arXiv XML | `scripts/gigo/my-workflow-4-2__parse-arxiv-xml.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-4-2__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/my-workflow-4-2/` | JSON |
| Verified data | `data/verified/my-workflow-4-2/` | JSON |
| Agent log | `logs/my-workflow-4-2-[DATE].json` | JSON |
| Human report | `reports/generated/my-workflow-4-2-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json`

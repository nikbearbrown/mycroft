# Workflow A — Extract & Store Raw Data

## Purpose

Workflow A — Extract & Store Raw Data defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to workflow a — extract & store raw data. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch TechCrunch | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch VentureBeat | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch HackerNews | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch ArXiv | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch Reddit | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Schedule Trigger | scheduleTrigger | conductor |
| Fetch TechCrunch | httpRequest | ingest |
| Fetch VentureBeat | httpRequest | ingest |
| Fetch HackerNews | httpRequest | ingest |
| Fetch ArXiv | httpRequest | ingest |
| Fetch Reddit | httpRequest | ingest |
| Parse TechCrunch | code | gigo |
| Parse VentureBeat | code | gigo |
| Parse HackerNews | code | gigo |
| Parse ArXiv | code | gigo |
| Parse Reddit | code | gigo |
| Store TechCrunch | postgres | gigo |
| Store VentureBeat | postgres | gigo |
| Store HackerNews | postgres | gigo |
| Store ArXiv | postgres | gigo |
| Store Reddit | postgres | gigo |
| Verify — Count Stored Items | postgres | conductor |
| Check — New Items Exist? | if | conductor |
| Trigger — Start Workflow B | executeWorkflow | conductor |
| Log — Skip | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-workflow-a-extract-store-raw-data.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-workflow-a-extract-store-raw-data --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-workflow-a-extract-store-raw-data data/verified/n8n-workflow-a-extract-store-raw-data -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-workflow-a-extract-store-raw-data.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Fetch TechCrunch. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-workflow-a-extract-store-raw-data/.
3. Step name: Fetch VentureBeat. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-venturebeat.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-workflow-a-extract-store-raw-data/.
4. Step name: Fetch HackerNews. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-hackernews.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-workflow-a-extract-store-raw-data/.
5. Step name: Fetch ArXiv. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-workflow-a-extract-store-raw-data/.
6. Step name: Fetch Reddit. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-reddit.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-workflow-a-extract-store-raw-data/.
7. Step name: Parse TechCrunch. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
8. Step name: Parse VentureBeat. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-venturebeat.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
9. Step name: Parse HackerNews. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-hackernews.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
10. Step name: Parse ArXiv. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
11. Step name: Parse Reddit. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-reddit.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
12. Step name: Store TechCrunch. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
13. Step name: Store VentureBeat. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-venturebeat.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
14. Step name: Store HackerNews. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-hackernews.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
15. Step name: Store ArXiv. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
16. Step name: Store Reddit. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-reddit.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
17. Step name: Log — Skip. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__log-skip.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-a-extract-store-raw-data/.
18. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-workflow-a-extract-store-raw-data__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-workflow-a-extract-store-raw-data-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-workflow-a-extract-store-raw-data-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Workflow A — Extract & Store Raw Data` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-workflow-a-extract-store-raw-data --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-workflow-a-extract-store-raw-data --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Fetch TechCrunch | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step fetch-techcrunch` | `--sample` |
| Fetch VentureBeat | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step fetch-venturebeat` | `--sample` |
| Fetch HackerNews | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step fetch-hackernews` | `--sample` |
| Fetch ArXiv | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step fetch-arxiv` | `--sample` |
| Fetch Reddit | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step fetch-reddit` | `--sample` |
| Parse TechCrunch | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step parse-techcrunch` |  |
| Parse VentureBeat | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step parse-venturebeat` |  |
| Parse HackerNews | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step parse-hackernews` |  |
| Parse ArXiv | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step parse-arxiv` |  |
| Parse Reddit | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step parse-reddit` |  |
| Store TechCrunch | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step store-techcrunch` |  |
| Store VentureBeat | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step store-venturebeat` |  |
| Store HackerNews | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step store-hackernews` |  |
| Store ArXiv | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step store-arxiv` |  |
| Store Reddit | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step store-reddit` |  |
| Log — Skip | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step log-skip` |  |
| Produce human report | `snickerdoodle run n8n-workflow-a-extract-store-raw-data --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-workflow-a-extract-store-raw-data --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-workflow-a-extract-store-raw-data --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-workflow-a-extract-store-raw-data --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Fetch TechCrunch | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-techcrunch.py` | ingest |
| Fetch VentureBeat | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-venturebeat.py` | ingest |
| Fetch HackerNews | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-hackernews.py` | ingest |
| Fetch ArXiv | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-arxiv.py` | ingest |
| Fetch Reddit | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-a-extract-store-raw-data__fetch-reddit.py` | ingest |
| Parse TechCrunch | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-techcrunch.py` | gigo |
| Parse VentureBeat | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-venturebeat.py` | gigo |
| Parse HackerNews | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-hackernews.py` | gigo |
| Parse ArXiv | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-arxiv.py` | gigo |
| Parse Reddit | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__parse-reddit.py` | gigo |
| Store TechCrunch | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-techcrunch.py` | gigo |
| Store VentureBeat | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-venturebeat.py` | gigo |
| Store HackerNews | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-hackernews.py` | gigo |
| Store ArXiv | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-arxiv.py` | gigo |
| Store Reddit | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__store-reddit.py` | gigo |
| Log — Skip | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-a-extract-store-raw-data__log-skip.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-workflow-a-extract-store-raw-data__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-workflow-a-extract-store-raw-data/` | JSON |
| Verified data | `data/verified/n8n-workflow-a-extract-store-raw-data/` | JSON |
| Agent log | `logs/n8n-workflow-a-extract-store-raw-data-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-workflow-a-extract-store-raw-data-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json`

# Investor agent - part 2

## Purpose

Investor agent - part 2 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to investor agent - part 2. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| RSS Read | rssFeedRead | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When clicking ‘Execute workflow’ | manualTrigger | conductor |
| RSS Read | rssFeedRead | ingest |
| Extract Funding Deals | code | gigo |
| Insert or update rows in a table | postgres | gigo |
| extract investor | code | gigo |
| Execute a SQL query | postgres | gigo |
| Build Investor Links | code | gigo |
| Insert or update rows in a table1 | postgres | gigo |
| Execute a SQL query1 | postgres | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-investor-agent-part-2.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-investor-agent-part-2 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-investor-agent-part-2 data/verified/n8n-investor-agent-part-2 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-investor-agent-part-2.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: RSS Read. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-investor-agent-part-2__rss-read.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-investor-agent-part-2/.
3. Step name: Extract Funding Deals. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__extract-funding-deals.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-investor-agent-part-2/.
4. Step name: Insert or update rows in a table. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__insert-or-update-rows-in-a-table.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-investor-agent-part-2/.
5. Step name: extract investor. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__extract-investor.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-investor-agent-part-2/.
6. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-investor-agent-part-2/.
7. Step name: Build Investor Links. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__build-investor-links.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-investor-agent-part-2/.
8. Step name: Insert or update rows in a table1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__insert-or-update-rows-in-a-table1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-investor-agent-part-2/.
9. Step name: Execute a SQL query1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__execute-a-sql-query1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-investor-agent-part-2/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-investor-agent-part-2__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-investor-agent-part-2-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-investor-agent-part-2-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Investor agent - part 2` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-investor-agent-part-2 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-investor-agent-part-2 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| RSS Read | `snickerdoodle run n8n-investor-agent-part-2 --step rss-read` | `--sample` |
| Extract Funding Deals | `snickerdoodle run n8n-investor-agent-part-2 --step extract-funding-deals` |  |
| Insert or update rows in a table | `snickerdoodle run n8n-investor-agent-part-2 --step insert-or-update-rows-in-a-table` |  |
| extract investor | `snickerdoodle run n8n-investor-agent-part-2 --step extract-investor` |  |
| Execute a SQL query | `snickerdoodle run n8n-investor-agent-part-2 --step execute-a-sql-query` |  |
| Build Investor Links | `snickerdoodle run n8n-investor-agent-part-2 --step build-investor-links` |  |
| Insert or update rows in a table1 | `snickerdoodle run n8n-investor-agent-part-2 --step insert-or-update-rows-in-a-table1` |  |
| Execute a SQL query1 | `snickerdoodle run n8n-investor-agent-part-2 --step execute-a-sql-query1` |  |
| Produce human report | `snickerdoodle run n8n-investor-agent-part-2 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-investor-agent-part-2 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-investor-agent-part-2 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-investor-agent-part-2 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| RSS Read | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-investor-agent-part-2__rss-read.py` | ingest |
| Extract Funding Deals | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__extract-funding-deals.py` | gigo |
| Insert or update rows in a table | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__insert-or-update-rows-in-a-table.py` | gigo |
| extract investor | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__extract-investor.py` | gigo |
| Execute a SQL query | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__execute-a-sql-query.py` | gigo |
| Build Investor Links | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__build-investor-links.py` | gigo |
| Insert or update rows in a table1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__insert-or-update-rows-in-a-table1.py` | gigo |
| Execute a SQL query1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-investor-agent-part-2__execute-a-sql-query1.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-investor-agent-part-2__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-investor-agent-part-2/` | JSON |
| Verified data | `data/verified/n8n-investor-agent-part-2/` | JSON |
| Agent log | `logs/n8n-investor-agent-part-2-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-investor-agent-part-2-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json`

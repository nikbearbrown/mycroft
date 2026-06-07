# Investor agent - part 2

## Purpose

Investor agent - part 2 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to investor agent - part 2. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Original workflow sources | [TODO: DEV] Parse original workflow node types. | [TODO: DATA SOURCE] Extract source URLs or paths from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When clicking ‘Execute workflow’ | `manualTrigger` | conductor |
| RSS Read | `rssFeedRead` | tool |
| Extract Funding Deals | `code` | conductor |
| Insert or update rows in a table | `postgres` | gigo |
| extract investor | `code` | conductor |
| Execute a SQL query | `postgres` | gigo |
| Build Investor Links | `code` | conductor |
| Insert or update rows in a table1 | `postgres` | gigo |
| Execute a SQL query1 | `postgres` | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (4 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/investor-agent-part-2.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run investor-agent-part-2 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/investor-agent-part-2 data/verified/investor-agent-part-2 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/investor-agent-part-2.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: RSS Read. Labor: AI with Human gate.
   Script called: `scripts/tools/investor-agent-part-2__rss-read.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Insert or update rows in a table. Labor: AI with Human gate.
   Script called: `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/investor-agent-part-2/.
4. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/gigo/investor-agent-part-2__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/investor-agent-part-2/.
5. Step name: Insert or update rows in a table1. Labor: AI with Human gate.
   Script called: `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/investor-agent-part-2/.
6. Step name: Execute a SQL query1. Labor: AI with Human gate.
   Script called: `scripts/gigo/investor-agent-part-2__execute-a-sql-query1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/investor-agent-part-2/.
7. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/investor-agent-part-2__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/investor-agent-part-2-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/investor-agent-part-2-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Investor agent - part 2` run.
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
`snickerdoodle run investor-agent-part-2 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run investor-agent-part-2 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| RSS Read | `snickerdoodle run investor-agent-part-2 --step rss-read` | `--no-write` |
| Insert or update rows in a table | `snickerdoodle run investor-agent-part-2 --step insert-or-update-rows-in-a-table` |  |
| Execute a SQL query | `snickerdoodle run investor-agent-part-2 --step execute-a-sql-query` |  |
| Insert or update rows in a table1 | `snickerdoodle run investor-agent-part-2 --step insert-or-update-rows-in-a-table1` |  |
| Execute a SQL query1 | `snickerdoodle run investor-agent-part-2 --step execute-a-sql-query1` |  |
| Produce human report | `snickerdoodle run investor-agent-part-2 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate investor-agent-part-2 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate investor-agent-part-2 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate investor-agent-part-2 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| RSS Read | `scripts/tools/investor-agent-part-2__rss-read.py` | tool |
| Insert or update rows in a table | `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table.py` | gigo |
| Execute a SQL query | `scripts/gigo/investor-agent-part-2__execute-a-sql-query.py` | gigo |
| Insert or update rows in a table1 | `scripts/gigo/investor-agent-part-2__insert-or-update-rows-in-a-table1.py` | gigo |
| Execute a SQL query1 | `scripts/gigo/investor-agent-part-2__execute-a-sql-query1.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/investor-agent-part-2__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/investor-agent-part-2/` | JSON |
| Verified data | `data/verified/investor-agent-part-2/` | JSON |
| Agent log | `logs/investor-agent-part-2-[DATE].json` | JSON |
| Human report | `reports/generated/investor-agent-part-2-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Investor agent - part 2.json`

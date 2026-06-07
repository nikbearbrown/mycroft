# FORECASTING

## Purpose

FORECASTING defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to forecasting. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Alpha Vantage Market Data | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| FinBert | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Alpha Vantage Market Data | httpRequest | ingest |
| Configuration | set | gigo |
| FinBert | httpRequest | ingest |
| Merge | merge | conductor |
| Code1 | code | gigo |
| If | if | conductor |
| Code2 | code | gigo |
| Execute a SQL query | postgres | gigo |
| Edit Fields | set | gigo |
| When clicking ‘Execute workflow’ | manualTrigger | conductor |
| Insert rows in a table | postgres | gigo |
| Send email | emailSend | tool |
| Historical data | code | gigo |
| Code | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Forecasting_Agent/Forecasting_Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Forecasting_Agent/Forecasting_Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-forecasting.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-forecasting --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-forecasting data/verified/n8n-forecasting -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-forecasting.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Forecasting_Agent/Forecasting_Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Alpha Vantage Market Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-forecasting__alpha-vantage-market-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-forecasting/.
3. Step name: Configuration. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__configuration.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
4. Step name: FinBert. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-forecasting__finbert.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-forecasting/.
5. Step name: Code1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__code1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
6. Step name: Code2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__code2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
7. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
8. Step name: Edit Fields. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__edit-fields.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
9. Step name: Insert rows in a table. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__insert-rows-in-a-table.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
10. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-forecasting__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Historical data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__historical-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
12. Step name: Code. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__code.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-forecasting/.
13. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-forecasting__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-forecasting-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-forecasting-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `FORECASTING` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-forecasting --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-forecasting --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Alpha Vantage Market Data | `snickerdoodle run n8n-forecasting --step alpha-vantage-market-data` | `--sample` |
| Configuration | `snickerdoodle run n8n-forecasting --step configuration` |  |
| FinBert | `snickerdoodle run n8n-forecasting --step finbert` | `--sample` |
| Code1 | `snickerdoodle run n8n-forecasting --step code1` |  |
| Code2 | `snickerdoodle run n8n-forecasting --step code2` |  |
| Execute a SQL query | `snickerdoodle run n8n-forecasting --step execute-a-sql-query` |  |
| Edit Fields | `snickerdoodle run n8n-forecasting --step edit-fields` |  |
| Insert rows in a table | `snickerdoodle run n8n-forecasting --step insert-rows-in-a-table` |  |
| Send email | `snickerdoodle run n8n-forecasting --step send-email` | `--no-write` |
| Historical data | `snickerdoodle run n8n-forecasting --step historical-data` |  |
| Code | `snickerdoodle run n8n-forecasting --step code` |  |
| Produce human report | `snickerdoodle run n8n-forecasting --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-forecasting --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-forecasting --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-forecasting --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Alpha Vantage Market Data | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-forecasting__alpha-vantage-market-data.py` | ingest |
| Configuration | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__configuration.py` | gigo |
| FinBert | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-forecasting__finbert.py` | ingest |
| Code1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__code1.py` | gigo |
| Code2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__code2.py` | gigo |
| Execute a SQL query | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__execute-a-sql-query.py` | gigo |
| Edit Fields | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__edit-fields.py` | gigo |
| Insert rows in a table | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__insert-rows-in-a-table.py` | gigo |
| Send email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-forecasting__send-email.py` | tool |
| Historical data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__historical-data.py` | gigo |
| Code | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-forecasting__code.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-forecasting__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-forecasting/` | JSON |
| Verified data | `data/verified/n8n-forecasting/` | JSON |
| Agent log | `logs/n8n-forecasting-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-forecasting-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Forecasting_Agent/Forecasting_Agent.json`

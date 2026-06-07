# Funding Intelligence Agent

## Purpose

Funding Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to funding intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Schedule Trigger | `scheduleTrigger` | conductor |
| Zyte_TechCrunch_Scraper | `httpRequest` | ingest |
| HTML | `html` | tool |
| Zyte_VentureBeat | `httpRequest` | ingest |
| Decode_VB | `code` | conductor |
| Decode_TC | `code` | conductor |
| HTML1 | `html` | tool |
| Merge | `merge` | conductor |
| Filter and split VB | `code` | gigo |
| Filter and split tech_crunch | `code` | gigo |
| Filter_Funding_Keywords | `code` | gigo |
| Classify_Industry | `code` | conductor |
| Execute a SQL query | `postgres` | gigo |
| Insert rows in a table | `postgres` | gigo |
| Send email | `emailSend` | report |
| Append row in sheet | `googleSheets` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (5 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (3 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (5 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/funding-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run funding-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/funding-intelligence-agent data/verified/funding-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/funding-intelligence-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Zyte_TechCrunch_Scraper. Labor: AI with Human gate.
   Script called: `scripts/ingest/funding-intelligence-agent__zyte-techcrunch-scraper.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/funding-intelligence-agent/.
3. Step name: HTML. Labor: AI with Human gate.
   Script called: `scripts/tools/funding-intelligence-agent__html.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Zyte_VentureBeat. Labor: AI with Human gate.
   Script called: `scripts/ingest/funding-intelligence-agent__zyte-venturebeat.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/funding-intelligence-agent/.
5. Step name: HTML1. Labor: AI with Human gate.
   Script called: `scripts/tools/funding-intelligence-agent__html1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Filter and split VB. Labor: AI with Human gate.
   Script called: `scripts/gigo/funding-intelligence-agent__filter-and-split-vb.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/funding-intelligence-agent/.
7. Step name: Filter and split tech_crunch. Labor: AI with Human gate.
   Script called: `scripts/gigo/funding-intelligence-agent__filter-and-split-tech-crunch.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/funding-intelligence-agent/.
8. Step name: Filter_Funding_Keywords. Labor: AI with Human gate.
   Script called: `scripts/gigo/funding-intelligence-agent__filter-funding-keywords.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/funding-intelligence-agent/.
9. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/gigo/funding-intelligence-agent__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/funding-intelligence-agent/.
10. Step name: Insert rows in a table. Labor: AI with Human gate.
   Script called: `scripts/gigo/funding-intelligence-agent__insert-rows-in-a-table.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/funding-intelligence-agent/.
11. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/funding-intelligence-agent__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
12. Step name: Append row in sheet. Labor: AI with Human gate.
   Script called: `scripts/tools/funding-intelligence-agent__append-row-in-sheet.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/funding-intelligence-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/funding-intelligence-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/funding-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Funding Intelligence Agent` run.
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
`snickerdoodle run funding-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run funding-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Zyte_TechCrunch_Scraper | `snickerdoodle run funding-intelligence-agent --step zyte-techcrunch-scraper` | `--sample` |
| HTML | `snickerdoodle run funding-intelligence-agent --step html` | `--no-write` |
| Zyte_VentureBeat | `snickerdoodle run funding-intelligence-agent --step zyte-venturebeat` | `--sample` |
| HTML1 | `snickerdoodle run funding-intelligence-agent --step html1` | `--no-write` |
| Filter and split VB | `snickerdoodle run funding-intelligence-agent --step filter-and-split-vb` |  |
| Filter and split tech_crunch | `snickerdoodle run funding-intelligence-agent --step filter-and-split-tech-crunch` |  |
| Filter_Funding_Keywords | `snickerdoodle run funding-intelligence-agent --step filter-funding-keywords` |  |
| Execute a SQL query | `snickerdoodle run funding-intelligence-agent --step execute-a-sql-query` |  |
| Insert rows in a table | `snickerdoodle run funding-intelligence-agent --step insert-rows-in-a-table` |  |
| Send email | `snickerdoodle run funding-intelligence-agent --step send-email` | `--no-write` |
| Append row in sheet | `snickerdoodle run funding-intelligence-agent --step append-row-in-sheet` | `--no-write` |
| Produce human report | `snickerdoodle run funding-intelligence-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate funding-intelligence-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate funding-intelligence-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate funding-intelligence-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Zyte_TechCrunch_Scraper | `scripts/ingest/funding-intelligence-agent__zyte-techcrunch-scraper.py` | ingest |
| HTML | `scripts/tools/funding-intelligence-agent__html.py` | tool |
| Zyte_VentureBeat | `scripts/ingest/funding-intelligence-agent__zyte-venturebeat.py` | ingest |
| HTML1 | `scripts/tools/funding-intelligence-agent__html1.py` | tool |
| Filter and split VB | `scripts/gigo/funding-intelligence-agent__filter-and-split-vb.py` | gigo |
| Filter and split tech_crunch | `scripts/gigo/funding-intelligence-agent__filter-and-split-tech-crunch.py` | gigo |
| Filter_Funding_Keywords | `scripts/gigo/funding-intelligence-agent__filter-funding-keywords.py` | gigo |
| Execute a SQL query | `scripts/gigo/funding-intelligence-agent__execute-a-sql-query.py` | gigo |
| Insert rows in a table | `scripts/gigo/funding-intelligence-agent__insert-rows-in-a-table.py` | gigo |
| Send email | `[TODO: DEV] Create or map script path: scripts/tools/funding-intelligence-agent__send-email.py` | tool |
| Append row in sheet | `scripts/tools/funding-intelligence-agent__append-row-in-sheet.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/funding-intelligence-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/funding-intelligence-agent/` | JSON |
| Verified data | `data/verified/funding-intelligence-agent/` | JSON |
| Agent log | `logs/funding-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/funding-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json`

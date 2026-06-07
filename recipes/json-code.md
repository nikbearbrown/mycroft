# Json_code

## Purpose

Json_code defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to json_code. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Get Portfolio from Sheets | `googleSheets` | tool |
| Fetch Live Prices | `httpRequest` | ingest |
| Calculate Advanced Risk | `code` | tool |
| Prepare for LLM | `code` | tool |
| Call Groq API | `httpRequest` | tool |
| Format Report | `code` | report |
| Log to Sheets | `googleSheets` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (5 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (1 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Risk_Management_Agent/Json_code.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Risk_Management_Agent/Json_code.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/json-code.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run json-code --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/json-code data/verified/json-code -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/json-code.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Risk_Management_Agent/Json_code.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Get Portfolio from Sheets. Labor: AI with Human gate.
   Script called: `scripts/tools/json-code__get-portfolio-from-sheets.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Fetch Live Prices. Labor: AI with Human gate.
   Script called: `scripts/ingest/json-code__fetch-live-prices.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/json-code/.
4. Step name: Calculate Advanced Risk. Labor: AI with Human gate.
   Script called: `scripts/tools/json-code__calculate-advanced-risk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Prepare for LLM. Labor: AI with Human gate.
   Script called: `scripts/tools/json-code__prepare-for-llm.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Call Groq API. Labor: AI with Human gate.
   Script called: `scripts/tools/json-code__call-groq-api.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Format Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/json-code__format-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
8. Step name: Log to Sheets. Labor: AI with Human gate.
   Script called: `scripts/tools/json-code__log-to-sheets.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/json-code__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/json-code-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/json-code-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Json_code` run.
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
`snickerdoodle run json-code --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run json-code --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Get Portfolio from Sheets | `snickerdoodle run json-code --step get-portfolio-from-sheets` | `--no-write` |
| Fetch Live Prices | `snickerdoodle run json-code --step fetch-live-prices` | `--sample` |
| Calculate Advanced Risk | `snickerdoodle run json-code --step calculate-advanced-risk` | `--no-write` |
| Prepare for LLM | `snickerdoodle run json-code --step prepare-for-llm` | `--no-write` |
| Call Groq API | `snickerdoodle run json-code --step call-groq-api` | `--no-write` |
| Format Report | `snickerdoodle run json-code --step format-report` | `--no-write` |
| Log to Sheets | `snickerdoodle run json-code --step log-to-sheets` | `--no-write` |
| Produce human report | `snickerdoodle run json-code --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate json-code --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate json-code --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate json-code --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Get Portfolio from Sheets | `scripts/tools/json-code__get-portfolio-from-sheets.py` | tool |
| Fetch Live Prices | `scripts/ingest/json-code__fetch-live-prices.py` | ingest |
| Calculate Advanced Risk | `scripts/tools/json-code__calculate-advanced-risk.py` | tool |
| Prepare for LLM | `scripts/tools/json-code__prepare-for-llm.py` | tool |
| Call Groq API | `scripts/tools/json-code__call-groq-api.py` | tool |
| Format Report | `[TODO: DEV] Create or map script path: scripts/tools/json-code__format-report.py` | tool |
| Log to Sheets | `scripts/tools/json-code__log-to-sheets.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/json-code__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/json-code/` | JSON |
| Verified data | `data/verified/json-code/` | JSON |
| Agent log | `logs/json-code-[DATE].json` | JSON |
| Human report | `reports/generated/json-code-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Risk_Management_Agent/Json_code.json`

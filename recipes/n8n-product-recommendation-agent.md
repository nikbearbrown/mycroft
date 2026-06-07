# Product Recommendation Agent

## Purpose

Product Recommendation Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to product recommendation agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Original workflow sources | [TODO: DEV] Parse original workflow node types. | [TODO: DATA SOURCE] Extract source URLs or paths from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Execute a SQL query | postgres | gigo |
| When clicking ‘Execute workflow’ | manualTrigger | conductor |
| Execute a SQL query1 | postgres | gigo |
| Execute a SQL query2 | postgres | gigo |
| Collect User Requirements | set | gigo |
| Code | code | gigo |
| Message a model | googleGemini | gigo |
| Code1 | code | gigo |
| Send email | emailSend | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Product_Recommendation_Agent/Product_Recommendation_Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Product_Recommendation_Agent/Product_Recommendation_Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-product-recommendation-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-product-recommendation-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-product-recommendation-agent data/verified/n8n-product-recommendation-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-product-recommendation-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Product_Recommendation_Agent/Product_Recommendation_Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-product-recommendation-agent/.
3. Step name: Execute a SQL query1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__execute-a-sql-query1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-product-recommendation-agent/.
4. Step name: Execute a SQL query2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__execute-a-sql-query2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-product-recommendation-agent/.
5. Step name: Collect User Requirements. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__collect-user-requirements.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-product-recommendation-agent/.
6. Step name: Code. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__code.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-product-recommendation-agent/.
7. Step name: Message a model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__message-a-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-product-recommendation-agent/.
8. Step name: Code1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__code1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-product-recommendation-agent/.
9. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-product-recommendation-agent__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-product-recommendation-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-product-recommendation-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-product-recommendation-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Product Recommendation Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-product-recommendation-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-product-recommendation-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Execute a SQL query | `snickerdoodle run n8n-product-recommendation-agent --step execute-a-sql-query` |  |
| Execute a SQL query1 | `snickerdoodle run n8n-product-recommendation-agent --step execute-a-sql-query1` |  |
| Execute a SQL query2 | `snickerdoodle run n8n-product-recommendation-agent --step execute-a-sql-query2` |  |
| Collect User Requirements | `snickerdoodle run n8n-product-recommendation-agent --step collect-user-requirements` |  |
| Code | `snickerdoodle run n8n-product-recommendation-agent --step code` |  |
| Message a model | `snickerdoodle run n8n-product-recommendation-agent --step message-a-model` |  |
| Code1 | `snickerdoodle run n8n-product-recommendation-agent --step code1` |  |
| Send email | `snickerdoodle run n8n-product-recommendation-agent --step send-email` | `--no-write` |
| Produce human report | `snickerdoodle run n8n-product-recommendation-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-product-recommendation-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-product-recommendation-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-product-recommendation-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Execute a SQL query | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__execute-a-sql-query.py` | gigo |
| Execute a SQL query1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__execute-a-sql-query1.py` | gigo |
| Execute a SQL query2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__execute-a-sql-query2.py` | gigo |
| Collect User Requirements | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__collect-user-requirements.py` | gigo |
| Code | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__code.py` | gigo |
| Message a model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__message-a-model.py` | gigo |
| Code1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-product-recommendation-agent__code1.py` | gigo |
| Send email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-product-recommendation-agent__send-email.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-product-recommendation-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-product-recommendation-agent/` | JSON |
| Verified data | `data/verified/n8n-product-recommendation-agent/` | JSON |
| Agent log | `logs/n8n-product-recommendation-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-product-recommendation-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Product_Recommendation_Agent/Product_Recommendation_Agent.json`

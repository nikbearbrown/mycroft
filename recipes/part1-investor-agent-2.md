# Part1 -Investor_ Agent

## Purpose

Part1 -Investor_ Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to part1 -investor_ agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Parse User Question | `code` | gigo |
| DB - Get Recent Deals | `postgres` | ingest |
| Format Chatbot Response | `code` | conductor |
| Send Response | `respondToWebhook` | report |
| Get top investor | `postgres` | ingest |
| Route by Query Type | `switch` | conductor |
| Investor Profile SQL node | `postgres` | gigo |
| Startup Investors SQL node | `postgres` | gigo |
| Execute a SQL query | `postgres` | gigo |
| Webhook | `webhook` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (4 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (2 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Sprint2_Part1 -Investor_ Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Sprint2_Part1 -Investor_ Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/part1-investor-agent-2.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run part1-investor-agent-2 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/part1-investor-agent-2 data/verified/part1-investor-agent-2 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/part1-investor-agent-2.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Sprint2_Part1 -Investor_ Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Parse User Question. Labor: AI with Human gate.
   Script called: `scripts/gigo/part1-investor-agent-2__parse-user-question.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/part1-investor-agent-2/.
3. Step name: DB - Get Recent Deals. Labor: AI with Human gate.
   Script called: `scripts/ingest/part1-investor-agent-2__db-get-recent-deals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/part1-investor-agent-2/.
4. Step name: Send Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/part1-investor-agent-2__send-response.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
5. Step name: Get top investor. Labor: AI with Human gate.
   Script called: `scripts/ingest/part1-investor-agent-2__get-top-investor.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/part1-investor-agent-2/.
6. Step name: Investor Profile SQL node. Labor: AI with Human gate.
   Script called: `scripts/gigo/part1-investor-agent-2__investor-profile-sql-node.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/part1-investor-agent-2/.
7. Step name: Startup Investors SQL node. Labor: AI with Human gate.
   Script called: `scripts/gigo/part1-investor-agent-2__startup-investors-sql-node.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/part1-investor-agent-2/.
8. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/gigo/part1-investor-agent-2__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/part1-investor-agent-2/.
9. Step name: Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/part1-investor-agent-2__webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/part1-investor-agent-2__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/part1-investor-agent-2-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/part1-investor-agent-2-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Part1 -Investor_ Agent` run.
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
`snickerdoodle run part1-investor-agent-2 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run part1-investor-agent-2 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Parse User Question | `snickerdoodle run part1-investor-agent-2 --step parse-user-question` |  |
| DB - Get Recent Deals | `snickerdoodle run part1-investor-agent-2 --step db-get-recent-deals` | `--sample` |
| Send Response | `snickerdoodle run part1-investor-agent-2 --step send-response` | `--no-write` |
| Get top investor | `snickerdoodle run part1-investor-agent-2 --step get-top-investor` | `--sample` |
| Investor Profile SQL node | `snickerdoodle run part1-investor-agent-2 --step investor-profile-sql-node` |  |
| Startup Investors SQL node | `snickerdoodle run part1-investor-agent-2 --step startup-investors-sql-node` |  |
| Execute a SQL query | `snickerdoodle run part1-investor-agent-2 --step execute-a-sql-query` |  |
| Webhook | `snickerdoodle run part1-investor-agent-2 --step webhook` | `--no-write` |
| Produce human report | `snickerdoodle run part1-investor-agent-2 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate part1-investor-agent-2 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate part1-investor-agent-2 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate part1-investor-agent-2 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Parse User Question | `scripts/gigo/part1-investor-agent-2__parse-user-question.py` | gigo |
| DB - Get Recent Deals | `scripts/ingest/part1-investor-agent-2__db-get-recent-deals.py` | ingest |
| Send Response | `[TODO: DEV] Create or map script path: scripts/tools/part1-investor-agent-2__send-response.py` | tool |
| Get top investor | `scripts/ingest/part1-investor-agent-2__get-top-investor.py` | ingest |
| Investor Profile SQL node | `scripts/gigo/part1-investor-agent-2__investor-profile-sql-node.py` | gigo |
| Startup Investors SQL node | `scripts/gigo/part1-investor-agent-2__startup-investors-sql-node.py` | gigo |
| Execute a SQL query | `scripts/gigo/part1-investor-agent-2__execute-a-sql-query.py` | gigo |
| Webhook | `scripts/tools/part1-investor-agent-2__webhook.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/part1-investor-agent-2__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/part1-investor-agent-2/` | JSON |
| Verified data | `data/verified/part1-investor-agent-2/` | JSON |
| Agent log | `logs/part1-investor-agent-2-[DATE].json` | JSON |
| Human report | `reports/generated/part1-investor-agent-2-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Sprint2_Part1 -Investor_ Agent.json`

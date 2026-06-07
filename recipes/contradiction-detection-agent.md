# Contradiction_detection_agent

## Purpose

Contradiction_detection_agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to contradiction_detection_agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (7 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Set Company Input | `set` | conductor |
| DB: Fetch Earnings Guidance Signals | `postgres` | ingest |
| DB: Fetch Risk Admissions | `postgres` | ingest |
| DB: Fetch QA Pressure Map | `postgres` | ingest |
| DB: Fetch News Signals | `postgres` | ingest |
| DB: Fetch Tech Stack Signals | `postgres` | ingest |
| Aggregate All Signals | `code` | conductor |
| Run Pattern Detection Engine | `code` | conductor |
| Build Groq Prompt | `code` | tool |
| LLM Needed? | `if` | conductor |
| Groq: Analyse Contradictions | `httpRequest` | tool |
| Process Groq Response | `code` | gigo |
| No-Flag Passthrough | `code` | conductor |
| DB: Insert Contradiction Report | `postgres` | report |
| Fan Out Flags | `code` | conductor |
| DB: Insert Contradiction Flag | `postgres` | gigo |
| Build Final Report | `code` | report |
| Execute a SQL query | `postgres` | gigo |
| Execute a SQL query1 | `postgres` | gigo |
| Execute a SQL query2 | `postgres` | ingest |
| Execute a SQL query3 | `postgres` | gigo |
| HTTP Request | `httpRequest` | ingest |
| Process News Response | `code` | gigo |
| DB: Save News Signals | `postgres` | gigo |
| Merge | `merge` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (7 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (7 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (2 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/contradiction-detection-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run contradiction-detection-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/contradiction-detection-agent data/verified/contradiction-detection-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/contradiction-detection-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: DB: Fetch Earnings Guidance Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-earnings-guidance-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
3. Step name: DB: Fetch Risk Admissions. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-risk-admissions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
4. Step name: DB: Fetch QA Pressure Map. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-qa-pressure-map.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
5. Step name: DB: Fetch News Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-news-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
6. Step name: DB: Fetch Tech Stack Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__db-fetch-tech-stack-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
7. Step name: Build Groq Prompt. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent__build-groq-prompt.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Groq: Analyse Contradictions. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent__groq-analyse-contradictions.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Process Groq Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent__process-groq-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
10. Step name: DB: Insert Contradiction Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent__db-insert-contradiction-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
11. Step name: DB: Insert Contradiction Flag. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent__db-insert-contradiction-flag.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
12. Step name: Build Final Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent__build-final-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
13. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__execute-a-sql-query2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
14. Step name: Execute a SQL query1. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent__execute-a-sql-query1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
15. Step name: Execute a SQL query2. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__execute-a-sql-query2.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
16. Step name: Execute a SQL query3. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent__execute-a-sql-query3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
17. Step name: HTTP Request. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent__http-request.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
18. Step name: Process News Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent__process-news-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
19. Step name: DB: Save News Signals. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent__db-save-news-signals.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
20. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/contradiction-detection-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/contradiction-detection-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Contradiction_detection_agent` run.
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
`snickerdoodle run contradiction-detection-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run contradiction-detection-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| DB: Fetch Earnings Guidance Signals | `snickerdoodle run contradiction-detection-agent --step db-fetch-earnings-guidance-signals` | `--sample` |
| DB: Fetch Risk Admissions | `snickerdoodle run contradiction-detection-agent --step db-fetch-risk-admissions` | `--sample` |
| DB: Fetch QA Pressure Map | `snickerdoodle run contradiction-detection-agent --step db-fetch-qa-pressure-map` | `--sample` |
| DB: Fetch News Signals | `snickerdoodle run contradiction-detection-agent --step db-fetch-news-signals` | `--sample` |
| DB: Fetch Tech Stack Signals | `snickerdoodle run contradiction-detection-agent --step db-fetch-tech-stack-signals` | `--sample` |
| Build Groq Prompt | `snickerdoodle run contradiction-detection-agent --step build-groq-prompt` | `--no-write` |
| Groq: Analyse Contradictions | `snickerdoodle run contradiction-detection-agent --step groq-analyse-contradictions` | `--no-write` |
| Process Groq Response | `snickerdoodle run contradiction-detection-agent --step process-groq-response` |  |
| DB: Insert Contradiction Report | `snickerdoodle run contradiction-detection-agent --step db-insert-contradiction-report` | `--no-write` |
| DB: Insert Contradiction Flag | `snickerdoodle run contradiction-detection-agent --step db-insert-contradiction-flag` |  |
| Build Final Report | `snickerdoodle run contradiction-detection-agent --step build-final-report` | `--no-write` |
| Execute a SQL query | `snickerdoodle run contradiction-detection-agent --step execute-a-sql-query` |  |
| Execute a SQL query1 | `snickerdoodle run contradiction-detection-agent --step execute-a-sql-query1` |  |
| Execute a SQL query2 | `snickerdoodle run contradiction-detection-agent --step execute-a-sql-query2` | `--sample` |
| Execute a SQL query3 | `snickerdoodle run contradiction-detection-agent --step execute-a-sql-query3` |  |
| HTTP Request | `snickerdoodle run contradiction-detection-agent --step http-request` | `--sample` |
| Process News Response | `snickerdoodle run contradiction-detection-agent --step process-news-response` |  |
| DB: Save News Signals | `snickerdoodle run contradiction-detection-agent --step db-save-news-signals` |  |
| Produce human report | `snickerdoodle run contradiction-detection-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate contradiction-detection-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate contradiction-detection-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate contradiction-detection-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| DB: Fetch Earnings Guidance Signals | `scripts/ingest/contradiction-detection-agent__db-fetch-earnings-guidance-signals.py` | ingest |
| DB: Fetch Risk Admissions | `scripts/ingest/contradiction-detection-agent__db-fetch-risk-admissions.py` | ingest |
| DB: Fetch QA Pressure Map | `scripts/ingest/contradiction-detection-agent__db-fetch-qa-pressure-map.py` | ingest |
| DB: Fetch News Signals | `scripts/ingest/contradiction-detection-agent__db-fetch-news-signals.py` | ingest |
| DB: Fetch Tech Stack Signals | `scripts/ingest/contradiction-detection-agent__db-fetch-tech-stack-signals.py` | ingest |
| Build Groq Prompt | `scripts/tools/contradiction-detection-agent__build-groq-prompt.py` | tool |
| Groq: Analyse Contradictions | `scripts/tools/contradiction-detection-agent__groq-analyse-contradictions.py` | tool |
| Process Groq Response | `scripts/gigo/contradiction-detection-agent__process-groq-response.py` | gigo |
| DB: Insert Contradiction Report | `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent__db-insert-contradiction-report.py` | tool |
| DB: Insert Contradiction Flag | `scripts/gigo/contradiction-detection-agent__db-insert-contradiction-flag.py` | gigo |
| Build Final Report | `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent__build-final-report.py` | tool |
| Execute a SQL query | `scripts/ingest/contradiction-detection-agent__execute-a-sql-query2.py` | gigo |
| Execute a SQL query1 | `scripts/gigo/contradiction-detection-agent__execute-a-sql-query1.py` | gigo |
| Execute a SQL query2 | `scripts/ingest/contradiction-detection-agent__execute-a-sql-query2.py` | ingest |
| Execute a SQL query3 | `scripts/gigo/contradiction-detection-agent__execute-a-sql-query3.py` | gigo |
| HTTP Request | `scripts/ingest/contradiction-detection-agent__http-request.py` | ingest |
| Process News Response | `scripts/gigo/contradiction-detection-agent__process-news-response.py` | gigo |
| DB: Save News Signals | `scripts/gigo/contradiction-detection-agent__db-save-news-signals.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/contradiction-detection-agent/` | JSON |
| Verified data | `data/verified/contradiction-detection-agent/` | JSON |
| Agent log | `logs/contradiction-detection-agent-[DATE].json` | JSON |
| Human report | `reports/generated/contradiction-detection-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json`

# My workflow 7

## Purpose

My workflow 7 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to my workflow 7. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook: Receive Transcript | `webhook` | tool |
| Validate Input | `code` | conductor |
| DB: Insert earnings_call | `postgres` | gigo |
| Set Call Context | `set` | conductor |
| Process Section Response | `code` | gigo |
| DB: Insert transcript_section | `postgres` | gigo |
| Route by Section Type | `switch` | conductor |
| Process Guidance Response | `code` | gigo |
| Process Risk Response | `code` | tool |
| Process QA Response | `code` | gigo |
| DB: Insert guidance_signal | `postgres` | gigo |
| DB: Insert risk_admission | `postgres` | gigo |
| DB: Insert qa_pressure | `postgres` | gigo |
| DB: Log Agent Run | `postgres` | gigo |
| Fetch All Signals for Summary | `postgres` | ingest |
| Process Summary Response | `code` | gigo |
| DB: Insert call_summary | `postgres` | gigo |
| DB: Mark Call Complete | `postgres` | gigo |
| Final Response | `code` | conductor |
| Webhook Response | `respondToWebhook` | report |
| Groq: Generate Call Summary | `httpRequest` | tool |
| Groq: Parse Transcript Sections | `httpRequest` | tool |
| Groq: Extract Guidance Signals | `httpRequest` | tool |
| Groq: Extract Risk Admissions | `httpRequest` | tool |
| Groq: Map QA Pressure | `httpRequest` | tool |
| Execute a SQL query | `postgres` | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (13 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (7 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow-7.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run my-workflow-7 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/my-workflow-7 data/verified/my-workflow-7 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow-7.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Webhook: Receive Transcript. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7__webhook-receive-transcript.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: DB: Insert earnings_call. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-insert-earnings-call.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
4. Step name: Process Section Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__process-section-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
5. Step name: DB: Insert transcript_section. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-insert-transcript-section.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
6. Step name: Process Guidance Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__process-guidance-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
7. Step name: Process Risk Response. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7__process-risk-response.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Process QA Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__process-qa-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
9. Step name: DB: Insert guidance_signal. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-insert-guidance-signal.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
10. Step name: DB: Insert risk_admission. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-insert-risk-admission.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
11. Step name: DB: Insert qa_pressure. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-insert-qa-pressure.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
12. Step name: DB: Log Agent Run. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-log-agent-run.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
13. Step name: Fetch All Signals for Summary. Labor: AI with Human gate.
   Script called: `scripts/ingest/my-workflow-7__fetch-all-signals-for-summary.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/my-workflow-7/.
14. Step name: Process Summary Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__process-summary-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
15. Step name: DB: Insert call_summary. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-insert-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
16. Step name: DB: Mark Call Complete. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__db-mark-call-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
17. Step name: Webhook Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-7__webhook-response.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
18. Step name: Groq: Generate Call Summary. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7__groq-generate-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Groq: Parse Transcript Sections. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7__groq-parse-transcript-sections.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
20. Step name: Groq: Extract Guidance Signals. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7__groq-extract-guidance-signals.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
21. Step name: Groq: Extract Risk Admissions. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7__groq-extract-risk-admissions.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
22. Step name: Groq: Map QA Pressure. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow-7__groq-map-qa-pressure.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
23. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow-7__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow-7/.
24. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-7__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/my-workflow-7-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/my-workflow-7-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `My workflow 7` run.
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
`snickerdoodle run my-workflow-7 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run my-workflow-7 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Webhook: Receive Transcript | `snickerdoodle run my-workflow-7 --step webhook-receive-transcript` | `--no-write` |
| DB: Insert earnings_call | `snickerdoodle run my-workflow-7 --step db-insert-earnings-call` |  |
| Process Section Response | `snickerdoodle run my-workflow-7 --step process-section-response` |  |
| DB: Insert transcript_section | `snickerdoodle run my-workflow-7 --step db-insert-transcript-section` |  |
| Process Guidance Response | `snickerdoodle run my-workflow-7 --step process-guidance-response` |  |
| Process Risk Response | `snickerdoodle run my-workflow-7 --step process-risk-response` | `--no-write` |
| Process QA Response | `snickerdoodle run my-workflow-7 --step process-qa-response` |  |
| DB: Insert guidance_signal | `snickerdoodle run my-workflow-7 --step db-insert-guidance-signal` |  |
| DB: Insert risk_admission | `snickerdoodle run my-workflow-7 --step db-insert-risk-admission` |  |
| DB: Insert qa_pressure | `snickerdoodle run my-workflow-7 --step db-insert-qa-pressure` |  |
| DB: Log Agent Run | `snickerdoodle run my-workflow-7 --step db-log-agent-run` |  |
| Fetch All Signals for Summary | `snickerdoodle run my-workflow-7 --step fetch-all-signals-for-summary` | `--sample` |
| Process Summary Response | `snickerdoodle run my-workflow-7 --step process-summary-response` |  |
| DB: Insert call_summary | `snickerdoodle run my-workflow-7 --step db-insert-call-summary` |  |
| DB: Mark Call Complete | `snickerdoodle run my-workflow-7 --step db-mark-call-complete` |  |
| Webhook Response | `snickerdoodle run my-workflow-7 --step webhook-response` | `--no-write` |
| Groq: Generate Call Summary | `snickerdoodle run my-workflow-7 --step groq-generate-call-summary` | `--no-write` |
| Groq: Parse Transcript Sections | `snickerdoodle run my-workflow-7 --step groq-parse-transcript-sections` | `--no-write` |
| Groq: Extract Guidance Signals | `snickerdoodle run my-workflow-7 --step groq-extract-guidance-signals` | `--no-write` |
| Groq: Extract Risk Admissions | `snickerdoodle run my-workflow-7 --step groq-extract-risk-admissions` | `--no-write` |
| Groq: Map QA Pressure | `snickerdoodle run my-workflow-7 --step groq-map-qa-pressure` | `--no-write` |
| Execute a SQL query | `snickerdoodle run my-workflow-7 --step execute-a-sql-query` |  |
| Produce human report | `snickerdoodle run my-workflow-7 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate my-workflow-7 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate my-workflow-7 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate my-workflow-7 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Webhook: Receive Transcript | `scripts/tools/my-workflow-7__webhook-receive-transcript.py` | tool |
| DB: Insert earnings_call | `scripts/gigo/my-workflow-7__db-insert-earnings-call.py` | gigo |
| Process Section Response | `scripts/gigo/my-workflow-7__process-section-response.py` | gigo |
| DB: Insert transcript_section | `scripts/gigo/my-workflow-7__db-insert-transcript-section.py` | gigo |
| Process Guidance Response | `scripts/gigo/my-workflow-7__process-guidance-response.py` | gigo |
| Process Risk Response | `scripts/tools/my-workflow-7__process-risk-response.py` | tool |
| Process QA Response | `scripts/gigo/my-workflow-7__process-qa-response.py` | gigo |
| DB: Insert guidance_signal | `scripts/gigo/my-workflow-7__db-insert-guidance-signal.py` | gigo |
| DB: Insert risk_admission | `scripts/gigo/my-workflow-7__db-insert-risk-admission.py` | gigo |
| DB: Insert qa_pressure | `scripts/gigo/my-workflow-7__db-insert-qa-pressure.py` | gigo |
| DB: Log Agent Run | `scripts/gigo/my-workflow-7__db-log-agent-run.py` | gigo |
| Fetch All Signals for Summary | `scripts/ingest/my-workflow-7__fetch-all-signals-for-summary.py` | ingest |
| Process Summary Response | `scripts/gigo/my-workflow-7__process-summary-response.py` | gigo |
| DB: Insert call_summary | `scripts/gigo/my-workflow-7__db-insert-call-summary.py` | gigo |
| DB: Mark Call Complete | `scripts/gigo/my-workflow-7__db-mark-call-complete.py` | gigo |
| Webhook Response | `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-7__webhook-response.py` | tool |
| Groq: Generate Call Summary | `scripts/tools/my-workflow-7__groq-generate-call-summary.py` | tool |
| Groq: Parse Transcript Sections | `scripts/tools/my-workflow-7__groq-parse-transcript-sections.py` | tool |
| Groq: Extract Guidance Signals | `scripts/tools/my-workflow-7__groq-extract-guidance-signals.py` | tool |
| Groq: Extract Risk Admissions | `scripts/tools/my-workflow-7__groq-extract-risk-admissions.py` | tool |
| Groq: Map QA Pressure | `scripts/tools/my-workflow-7__groq-map-qa-pressure.py` | tool |
| Execute a SQL query | `scripts/gigo/my-workflow-7__execute-a-sql-query.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/my-workflow-7__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/my-workflow-7/` | JSON |
| Verified data | `data/verified/my-workflow-7/` | JSON |
| Agent log | `logs/my-workflow-7-[DATE].json` | JSON |
| Human report | `reports/generated/my-workflow-7-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json`

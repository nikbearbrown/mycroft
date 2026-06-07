# Earnings Call Intelligence Agent

## Purpose

Earnings Call Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to earnings call intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch All Signals for Summary | postgres | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Groq: Generate Call Summary | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Groq: Parse Transcript Sections | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Groq: Extract Guidance Signals | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Groq: Extract Risk Admissions | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Groq: Map QA Pressure | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook: Receive Transcript | webhook | conductor |
| Validate Input | code | gigo |
| DB: Insert earnings_call | postgres | gigo |
| Set Call Context | set | gigo |
| Process Section Response | code | gigo |
| DB: Insert transcript_section | postgres | gigo |
| Route by Section Type | switch | gigo |
| Process Guidance Response | code | gigo |
| Process Risk Response | code | gigo |
| Process QA Response | code | gigo |
| DB: Insert guidance_signal | postgres | gigo |
| DB: Insert risk_admission | postgres | gigo |
| DB: Insert qa_pressure | postgres | gigo |
| DB: Log Agent Run | postgres | gigo |
| Fetch All Signals for Summary | postgres | ingest |
| Process Summary Response | code | gigo |
| DB: Insert call_summary | postgres | gigo |
| DB: Mark Call Complete | postgres | gigo |
| Final Response | code | gigo |
| Webhook Response | respondToWebhook | conductor |
| Groq: Generate Call Summary | httpRequest | ingest |
| Groq: Parse Transcript Sections | httpRequest | ingest |
| Groq: Extract Guidance Signals | httpRequest | ingest |
| Groq: Extract Risk Admissions | httpRequest | ingest |
| Groq: Map QA Pressure | httpRequest | ingest |
| Execute a SQL query | postgres | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-earnings-call-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-earnings-call-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-earnings-call-intelligence-agent data/verified/n8n-earnings-call-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-earnings-call-intelligence-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Validate Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__validate-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
3. Step name: DB: Insert earnings_call. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-earnings-call.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
4. Step name: Set Call Context. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__set-call-context.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
5. Step name: Process Section Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-section-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
6. Step name: DB: Insert transcript_section. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-transcript-section.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
7. Step name: Route by Section Type. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__route-by-section-type.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
8. Step name: Process Guidance Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-guidance-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
9. Step name: Process Risk Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-risk-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
10. Step name: Process QA Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-qa-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
11. Step name: DB: Insert guidance_signal. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-guidance-signal.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
12. Step name: DB: Insert risk_admission. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-risk-admission.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
13. Step name: DB: Insert qa_pressure. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-qa-pressure.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
14. Step name: DB: Log Agent Run. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-log-agent-run.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
15. Step name: Fetch All Signals for Summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__fetch-all-signals-for-summary.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
16. Step name: Process Summary Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-summary-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
17. Step name: DB: Insert call_summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
18. Step name: DB: Mark Call Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-mark-call-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
19. Step name: Final Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__final-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
20. Step name: Groq: Generate Call Summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-generate-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
21. Step name: Groq: Parse Transcript Sections. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-parse-transcript-sections.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
22. Step name: Groq: Extract Guidance Signals. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-extract-guidance-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
23. Step name: Groq: Extract Risk Admissions. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-extract-risk-admissions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
24. Step name: Groq: Map QA Pressure. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-map-qa-pressure.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
25. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__execute-a-sql-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
26. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-earnings-call-intelligence-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-earnings-call-intelligence-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-earnings-call-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Earnings Call Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-earnings-call-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-earnings-call-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Validate Input | `snickerdoodle run n8n-earnings-call-intelligence-agent --step validate-input` |  |
| DB: Insert earnings_call | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-insert-earnings-call` |  |
| Set Call Context | `snickerdoodle run n8n-earnings-call-intelligence-agent --step set-call-context` |  |
| Process Section Response | `snickerdoodle run n8n-earnings-call-intelligence-agent --step process-section-response` |  |
| DB: Insert transcript_section | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-insert-transcript-section` |  |
| Route by Section Type | `snickerdoodle run n8n-earnings-call-intelligence-agent --step route-by-section-type` |  |
| Process Guidance Response | `snickerdoodle run n8n-earnings-call-intelligence-agent --step process-guidance-response` |  |
| Process Risk Response | `snickerdoodle run n8n-earnings-call-intelligence-agent --step process-risk-response` |  |
| Process QA Response | `snickerdoodle run n8n-earnings-call-intelligence-agent --step process-qa-response` |  |
| DB: Insert guidance_signal | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-insert-guidance-signal` |  |
| DB: Insert risk_admission | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-insert-risk-admission` |  |
| DB: Insert qa_pressure | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-insert-qa-pressure` |  |
| DB: Log Agent Run | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-log-agent-run` |  |
| Fetch All Signals for Summary | `snickerdoodle run n8n-earnings-call-intelligence-agent --step fetch-all-signals-for-summary` | `--sample` |
| Process Summary Response | `snickerdoodle run n8n-earnings-call-intelligence-agent --step process-summary-response` |  |
| DB: Insert call_summary | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-insert-call-summary` |  |
| DB: Mark Call Complete | `snickerdoodle run n8n-earnings-call-intelligence-agent --step db-mark-call-complete` |  |
| Final Response | `snickerdoodle run n8n-earnings-call-intelligence-agent --step final-response` |  |
| Groq: Generate Call Summary | `snickerdoodle run n8n-earnings-call-intelligence-agent --step groq-generate-call-summary` | `--sample` |
| Groq: Parse Transcript Sections | `snickerdoodle run n8n-earnings-call-intelligence-agent --step groq-parse-transcript-sections` | `--sample` |
| Groq: Extract Guidance Signals | `snickerdoodle run n8n-earnings-call-intelligence-agent --step groq-extract-guidance-signals` | `--sample` |
| Groq: Extract Risk Admissions | `snickerdoodle run n8n-earnings-call-intelligence-agent --step groq-extract-risk-admissions` | `--sample` |
| Groq: Map QA Pressure | `snickerdoodle run n8n-earnings-call-intelligence-agent --step groq-map-qa-pressure` | `--sample` |
| Execute a SQL query | `snickerdoodle run n8n-earnings-call-intelligence-agent --step execute-a-sql-query` |  |
| Produce human report | `snickerdoodle run n8n-earnings-call-intelligence-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Validate Input | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__validate-input.py` | gigo |
| DB: Insert earnings_call | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-earnings-call.py` | gigo |
| Set Call Context | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__set-call-context.py` | gigo |
| Process Section Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-section-response.py` | gigo |
| DB: Insert transcript_section | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-transcript-section.py` | gigo |
| Route by Section Type | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__route-by-section-type.py` | gigo |
| Process Guidance Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-guidance-response.py` | gigo |
| Process Risk Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-risk-response.py` | gigo |
| Process QA Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-qa-response.py` | gigo |
| DB: Insert guidance_signal | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-guidance-signal.py` | gigo |
| DB: Insert risk_admission | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-risk-admission.py` | gigo |
| DB: Insert qa_pressure | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-qa-pressure.py` | gigo |
| DB: Log Agent Run | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-log-agent-run.py` | gigo |
| Fetch All Signals for Summary | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__fetch-all-signals-for-summary.py` | ingest |
| Process Summary Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__process-summary-response.py` | gigo |
| DB: Insert call_summary | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-insert-call-summary.py` | gigo |
| DB: Mark Call Complete | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__db-mark-call-complete.py` | gigo |
| Final Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__final-response.py` | gigo |
| Groq: Generate Call Summary | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-generate-call-summary.py` | ingest |
| Groq: Parse Transcript Sections | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-parse-transcript-sections.py` | ingest |
| Groq: Extract Guidance Signals | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-extract-guidance-signals.py` | ingest |
| Groq: Extract Risk Admissions | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-extract-risk-admissions.py` | ingest |
| Groq: Map QA Pressure | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-map-qa-pressure.py` | ingest |
| Execute a SQL query | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent__execute-a-sql-query.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-earnings-call-intelligence-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-earnings-call-intelligence-agent/` | JSON |
| Verified data | `data/verified/n8n-earnings-call-intelligence-agent/` | JSON |
| Agent log | `logs/n8n-earnings-call-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-earnings-call-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json`

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

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/n8n-earnings-call-intelligence-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/n8n-earnings-call-intelligence-agent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/n8n-earnings-call-intelligence-agent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/n8n-earnings-call-intelligence-agent data/verified/n8n-earnings-call-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/n8n-earnings-call-intelligence-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/n8n-earnings-call-intelligence-agent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/n8n-earnings-call-intelligence-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/n8n-earnings-call-intelligence-agent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/n8n-earnings-call-intelligence-agent-[DATE].json && test -f reports/generated/n8n-earnings-call-intelligence-agent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-earnings-call-intelligence-agent-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-earnings-call-intelligence-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/n8n-earnings-call-intelligence-agent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-earnings-call-intelligence-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/n8n-earnings-call-intelligence-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-earnings-call-intelligence-agent-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-earnings-call-intelligence-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/n8n-earnings-call-intelligence-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-earnings-call-intelligence-agent-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-earnings-call-intelligence-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/n8n-earnings-call-intelligence-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-earnings-call-intelligence-agent-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-earnings-call-intelligence-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-earnings-call-intelligence-agent-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-earnings-call-intelligence-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/n8n-earnings-call-intelligence-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/n8n-earnings-call-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Earnings Call Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

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
| Verify provenance | `snickerdoodle run n8n-earnings-call-intelligence-agent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run n8n-earnings-call-intelligence-agent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run n8n-earnings-call-intelligence-agent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run n8n-earnings-call-intelligence-agent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run n8n-earnings-call-intelligence-agent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run n8n-earnings-call-intelligence-agent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate n8n-earnings-call-intelligence-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/n8n-earnings-call-intelligence-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/n8n-earnings-call-intelligence-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/n8n-earnings-call-intelligence-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/n8n-earnings-call-intelligence-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/n8n-earnings-call-intelligence-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/n8n-earnings-call-intelligence-agent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-earnings-call-intelligence-agent/` | JSON |
| Verified data | `data/verified/n8n-earnings-call-intelligence-agent/` | JSON |
| Agent log | `logs/n8n-earnings-call-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-earnings-call-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Earnings Call Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to earnings call intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

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

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Validate Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-validate-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
3. Step name: DB: Insert earnings_call. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-insert-earnings-call.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
4. Step name: Set Call Context. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-set-call-context.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
5. Step name: Process Section Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-process-section-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
6. Step name: DB: Insert transcript_section. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-insert-transcript-section.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
7. Step name: Route by Section Type. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-route-by-section-type.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
8. Step name: Process Guidance Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-process-guidance-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
9. Step name: Process Risk Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-process-risk-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
10. Step name: Process QA Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-process-qa-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
11. Step name: DB: Insert guidance_signal. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-insert-guidance-signal.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
12. Step name: DB: Insert risk_admission. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-insert-risk-admission.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
13. Step name: DB: Insert qa_pressure. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-insert-qa-pressure.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
14. Step name: DB: Log Agent Run. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-log-agent-run.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
15. Step name: Fetch All Signals for Summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent-fetch-all-signals-for-summary.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
16. Step name: Process Summary Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-process-summary-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
17. Step name: DB: Insert call_summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-insert-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
18. Step name: DB: Mark Call Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-db-mark-call-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
19. Step name: Final Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-earnings-call-intelligence-agent-final-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-earnings-call-intelligence-agent/.
20. Step name: Groq: Generate Call Summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent-groq-generate-call-summary.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
21. Step name: Groq: Parse Transcript Sections. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent-groq-parse-transcript-sections.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
22. Step name: Groq: Extract Guidance Signals. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent-groq-extract-guidance-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
23. Step name: Groq: Extract Risk Admissions. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent-groq-extract-risk-admissions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-earnings-call-intelligence-agent/.
24. Step name: Groq: Map QA Pressure. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-earnings-call-intelligence-agent__groq-

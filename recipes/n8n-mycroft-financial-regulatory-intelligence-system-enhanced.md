# Mycroft - Financial Regulatory Intelligence System - Enhanced

## Purpose

Mycroft - Financial Regulatory Intelligence System - Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - financial regulatory intelligence system - enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Federal Register - Securities | rssFeedRead | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| SEC Press Releases | rssFeedRead | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| FINRA Enforcement News | rssFeedRead | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| CFTC Regulations | rssFeedRead | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Investment Advisor Rules | rssFeedRead | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Federal Register - Securities | rssFeedRead | ingest |
| SEC Press Releases | rssFeedRead | ingest |
| FINRA Enforcement News | rssFeedRead | ingest |
| CFTC Regulations | rssFeedRead | ingest |
| Investment Advisor Rules | rssFeedRead | ingest |
| Merge All Sources | merge | conductor |
| Normalize Data | code | gigo |
| Filter Valid Content | if | conductor |
| Generate HTML Report | code | gigo |
| High Priority Filter | if | conductor |
| Send Email Alert | emailSend | tool |
| Read/Write Files from Disk | readWriteFile | tool |
| If | if | conductor |
| Send email | emailSend | tool |
| Schedule Every Day | scheduleTrigger | conductor |
| Generate Email | code | tool |
| Mark email sent | postgres | tool |
| Keyword Analysis & Urgency Scoring | code | gigo |
| Insert data into DB | postgres | gigo |
| Prepare Data | code | gigo |
| Code in JavaScript | code | gigo |
| If2 | if | conductor |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json` | Yes |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/n8n-mycroft-financial-regulatory-intelligence-system-enhanced.md" && rg -n "\[TODO: DEFINE]" "recipes/n8n-mycroft-financial-regulatory-intelligence-system-enhanced.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/n8n-mycroft-financial-regulatory-intelligence-system-enhanced.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/n8n-mycroft-financial-regulatory-intelligence-system-enhanced.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].json && test -f reports/generated/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-financial-regulatory-intelligence-system-enhanced`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-financial-regulatory-intelligence-system-enhanced`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-financial-regulatory-intelligence-system-enhanced`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-financial-regulatory-intelligence-system-enhanced`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-financial-regulatory-intelligence-system-enhanced`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-mycroft-financial-regulatory-intelligence-system-enhanced`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Financial Regulatory Intelligence System - Enhanced` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/` | JSON |
| Verified data | `data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/` | JSON |
| Agent log | `logs/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Mycroft - Financial Regulatory Intelligence System - Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - financial regulatory intelligence system - enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-financial-regulatory-intelligence-system-enhanced.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-financial-regulatory-intelligence-system-enhanced.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Federal Register - Securities. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-federal-register-securities.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
3. Step name: SEC Press Releases. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-sec-press-releases.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
4. Step name: FINRA Enforcement News. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-finra-enforcement-news.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
5. Step name: CFTC Regulations. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-cftc-regulations.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
6. Step name: Investment Advisor Rules. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-investment-advisor-rules.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
7. Step name: Normalize Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-normalize-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
8. Step name: Generate HTML Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-generate-html-report.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
9. Step name: Send Email Alert. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-send-email-alert.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-send-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Generate Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-generate-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Mark email sent. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-mark-email-sent.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Keyword Analysis & Urgency Scoring. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-keyword-analysis-and-urgency-scoring.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
15. Step name: Insert data into DB. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-insert-data-into-db.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
16. Step name: Prepare Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-prepare-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
17. Step name: Code in JavaScript. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-code-in-javascript.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
18. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

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

## Node Classification

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Federal Register - Securities. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__federal-register-securities.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
3. Step name: SEC Press Releases. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__sec-press-releases.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
4. Step name: FINRA Enforcement News. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__finra-enforcement-news.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
5. Step name: CFTC Regulations. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__cftc-regulations.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
6. Step name: Investment Advisor Rules. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__investment-advisor-rules.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
7. Step name: Normalize Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__normalize-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
8. Step name: Generate HTML Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__generate-html-report.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
9. Step name: Send Email Alert. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__send-email-alert.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Generate Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__generate-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Mark email sent. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__mark-email-sent.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Keyword Analysis & Urgency Scoring. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__keyword-analysis-and-urgency-scoring.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
15. Step name: Insert data into DB. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__insert-data-into-db.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
16. Step name: Prepare Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__prepare-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
17. Step name: Code in JavaScript. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__code-in-javascript.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/.
18. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Financial Regulatory Intelligence System - Enhanced` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| Federal Register - Securities | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step federal-register-securities` | `--sample` |
| SEC Press Releases | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step sec-press-releases` | `--sample` |
| FINRA Enforcement News | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step finra-enforcement-news` | `--sample` |
| CFTC Regulations | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step cftc-regulations` | `--sample` |
| Investment Advisor Rules | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step investment-advisor-rules` | `--sample` |
| Normalize Data | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step normalize-data` |  |
| Generate HTML Report | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step generate-html-report` |  |
| Send Email Alert | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step send-email-alert` | `--no-write` |
| Read/Write Files from Disk | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step read-write-files-from-disk` | `--no-write` |
| Send email | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step send-email` | `--no-write` |
| Generate Email | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step generate-email` | `--no-write` |
| Mark email sent | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step mark-email-sent` | `--no-write` |
| Keyword Analysis & Urgency Scoring | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step keyword-analysis-and-urgency-scoring` |  |
| Insert data into DB | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step insert-data-into-db` |  |
| Prepare Data | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step prepare-data` |  |
| Code in JavaScript | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step code-in-javascript` |  |
| Produce human report | `snickerdoodle run n8n-mycroft-financial-regulatory-intelligence-system-enhanced --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroft-financial-regulatory-intelligence-system-enhanced --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Federal Register - Securities | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__federal-register-securities.py` | ingest |
| SEC Press Releases | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__sec-press-releases.py` | ingest |
| FINRA Enforcement News | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__finra-enforcement-news.py` | ingest |
| CFTC Regulations | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__cftc-regulations.py` | ingest |
| Investment Advisor Rules | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__investment-advisor-rules.py` | ingest |
| Normalize Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__normalize-data.py` | gigo |
| Generate HTML Report | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__generate-html-report.py` | gigo |
| Send Email Alert | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__send-email-alert.py` | tool |
| Read/Write Files from Disk | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__read-write-files-from-disk.py` | tool |
| Send email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__send-email.py` | tool |
| Generate Email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__generate-email.py` | tool |
| Mark email sent | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__mark-email-sent.py` | tool |
| Keyword Analysis & Urgency Scoring | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__keyword-analysis-and-urgency-scoring.py` | gigo |
| Insert data into DB | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__insert-data-into-db.py` | gigo |
| Prepare Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__prepare-data.py` | gigo |
| Code in JavaScript | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__code-in-javascript.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-regulatory-intelligence-system-enhanced__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/` | JSON |
| Verified data | `data/verified/n8n-mycroft-financial-regulatory-intelligence-system-enhanced/` | JSON |
| Agent log | `logs/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json`

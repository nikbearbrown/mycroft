# Mycroft - Financial Regulatory Intelligence System - Enhanced

## Purpose

Mycroft - Financial Regulatory Intelligence System - Enhanced defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - financial regulatory intelligence system - enhanced. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (4 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Federal Register - Securities | `rssFeedRead` | tool |
| SEC Press Releases | `rssFeedRead` | tool |
| FINRA Enforcement News | `rssFeedRead` | tool |
| CFTC Regulations | `rssFeedRead` | tool |
| Investment Advisor Rules | `rssFeedRead` | tool |
| Merge All Sources | `merge` | conductor |
| Normalize Data | `code` | gigo |
| Filter Valid Content | `if` | conductor |
| Generate HTML Report | `code` | report |
| High Priority Filter | `if` | conductor |
| Send Email Alert | `emailSend` | report |
| Read/Write Files from Disk | `readWriteFile` | tool |
| If | `if` | conductor |
| Send email | `emailSend` | report |
| Schedule Every Day | `scheduleTrigger` | conductor |
| Generate Email | `code` | report |
| Mark email sent | `postgres` | gigo |
| Keyword Analysis & Urgency Scoring | `code` | tool |
| Insert data into DB | `postgres` | gigo |
| Prepare Data | `code` | conductor |
| Code in JavaScript | `code` | conductor |
| If2 | `if` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (3 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (7 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (4 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-financial-regulatory-intelligence-system-enhanced.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-financial-regulatory-intelligence-system-enhanced data/verified/mycroft-financial-regulatory-intelligence-system-enhanced -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-financial-regulatory-intelligence-system-enhanced.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Federal Register - Securities. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__federal-register-securities.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: SEC Press Releases. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__sec-press-releases.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: FINRA Enforcement News. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__finra-enforcement-news.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: CFTC Regulations. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__cftc-regulations.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Investment Advisor Rules. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__investment-advisor-rules.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Normalize Data. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__normalize-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-financial-regulatory-intelligence-system-enhanced/.
8. Step name: Generate HTML Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__generate-html-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
9. Step name: Send Email Alert. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__send-email-alert.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
10. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
12. Step name: Generate Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__generate-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
13. Step name: Mark email sent. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__mark-email-sent.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-financial-regulatory-intelligence-system-enhanced/.
14. Step name: Keyword Analysis & Urgency Scoring. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__keyword-analysis-and-urgency-scoring.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Insert data into DB. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__insert-data-into-db.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-financial-regulatory-intelligence-system-enhanced/.
16. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Financial Regulatory Intelligence System - Enhanced` run.
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
`snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Federal Register - Securities | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step federal-register-securities` | `--no-write` |
| SEC Press Releases | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step sec-press-releases` | `--no-write` |
| FINRA Enforcement News | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step finra-enforcement-news` | `--no-write` |
| CFTC Regulations | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step cftc-regulations` | `--no-write` |
| Investment Advisor Rules | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step investment-advisor-rules` | `--no-write` |
| Normalize Data | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step normalize-data` |  |
| Generate HTML Report | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step generate-html-report` | `--no-write` |
| Send Email Alert | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step send-email-alert` | `--no-write` |
| Read/Write Files from Disk | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step read-write-files-from-disk` | `--no-write` |
| Send email | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step send-email` | `--no-write` |
| Generate Email | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step generate-email` | `--no-write` |
| Mark email sent | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step mark-email-sent` |  |
| Keyword Analysis & Urgency Scoring | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step keyword-analysis-and-urgency-scoring` | `--no-write` |
| Insert data into DB | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step insert-data-into-db` |  |
| Produce human report | `snickerdoodle run mycroft-financial-regulatory-intelligence-system-enhanced --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-financial-regulatory-intelligence-system-enhanced --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-financial-regulatory-intelligence-system-enhanced --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-financial-regulatory-intelligence-system-enhanced --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Federal Register - Securities | `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__federal-register-securities.py` | tool |
| SEC Press Releases | `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__sec-press-releases.py` | tool |
| FINRA Enforcement News | `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__finra-enforcement-news.py` | tool |
| CFTC Regulations | `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__cftc-regulations.py` | tool |
| Investment Advisor Rules | `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__investment-advisor-rules.py` | tool |
| Normalize Data | `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__normalize-data.py` | gigo |
| Generate HTML Report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__generate-html-report.py` | tool |
| Send Email Alert | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__send-email-alert.py` | tool |
| Read/Write Files from Disk | `scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__read-write-files-from-disk.py` | tool |
| Send email | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__send-email.py` | tool |
| Generate Email | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__generate-email.py` | tool |
| Mark email sent | `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__mark-email-sent.py` | gigo |
| Keyword Analysis & Urgency Scoring | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__keyword-analysis-and-urgency-scoring.py` | tool |
| Insert data into DB | `scripts/gigo/mycroft-financial-regulatory-intelligence-system-enhanced__insert-data-into-db.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-regulatory-intelligence-system-enhanced__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-financial-regulatory-intelligence-system-enhanced/` | JSON |
| Verified data | `data/verified/mycroft-financial-regulatory-intelligence-system-enhanced/` | JSON |
| Agent log | `logs/mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-financial-regulatory-intelligence-system-enhanced-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json`

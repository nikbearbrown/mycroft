# Mycroft - News Intelligence Agent

## Purpose

Mycroft - News Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - news intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (4 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Company List | `code` | conductor |
| Build Query | `code` | conductor |
| Merge | `merge` | conductor |
| normalizenewsapi | `code` | gigo |
| NewsApiKey | `httpRequest` | ingest |
| HTTP Request | `httpRequest` | ingest |
| XML | `xml` | gigo |
| ProcessNewData | `code` | gigo |
| Edit Fields | `set` | conductor |
| HTTP Request1 | `httpRequest` | ingest |
| RiskCalculator | `code` | tool |
| Insert rows in a table | `postgres` | gigo |
| Alert Generator Code Node | `code` | report |
| Send email | `emailSend` | report |
| DailyGeneratorCode | `code` | report |
| Webhook | `webhook` | tool |
| Respond to Webhook | `respondToWebhook` | report |
| Set Variables | `set` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (4 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (2 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (4 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (5 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-news-intelligence-agent-2.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-news-intelligence-agent-2 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-news-intelligence-agent-2 data/verified/mycroft-news-intelligence-agent-2 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-news-intelligence-agent-2.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: normalizenewsapi. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__normalizenewsapi.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent-2/.
3. Step name: NewsApiKey. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroft-news-intelligence-agent-2__newsapikey.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroft-news-intelligence-agent-2/.
4. Step name: HTTP Request. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroft-news-intelligence-agent-2__http-request.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroft-news-intelligence-agent-2/.
5. Step name: XML. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent-2/.
6. Step name: ProcessNewData. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__processnewdata.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent-2/.
7. Step name: HTTP Request1. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroft-news-intelligence-agent-2__http-request1.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroft-news-intelligence-agent-2/.
8. Step name: RiskCalculator. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-news-intelligence-agent-2__riskcalculator.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Insert rows in a table. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-news-intelligence-agent-2__insert-rows-in-a-table.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent-2/.
10. Step name: Alert Generator Code Node. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__alert-generator-code-node.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
11. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
12. Step name: DailyGeneratorCode. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__dailygeneratorcode.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
13. Step name: Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-news-intelligence-agent-2__webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
15. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-news-intelligence-agent-2-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-news-intelligence-agent-2-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - News Intelligence Agent` run.
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
`snickerdoodle run mycroft-news-intelligence-agent-2 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-news-intelligence-agent-2 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| normalizenewsapi | `snickerdoodle run mycroft-news-intelligence-agent-2 --step normalizenewsapi` |  |
| NewsApiKey | `snickerdoodle run mycroft-news-intelligence-agent-2 --step newsapikey` | `--sample` |
| HTTP Request | `snickerdoodle run mycroft-news-intelligence-agent-2 --step http-request` | `--sample` |
| XML | `snickerdoodle run mycroft-news-intelligence-agent-2 --step xml` |  |
| ProcessNewData | `snickerdoodle run mycroft-news-intelligence-agent-2 --step processnewdata` |  |
| HTTP Request1 | `snickerdoodle run mycroft-news-intelligence-agent-2 --step http-request1` | `--sample` |
| RiskCalculator | `snickerdoodle run mycroft-news-intelligence-agent-2 --step riskcalculator` | `--no-write` |
| Insert rows in a table | `snickerdoodle run mycroft-news-intelligence-agent-2 --step insert-rows-in-a-table` |  |
| Alert Generator Code Node | `snickerdoodle run mycroft-news-intelligence-agent-2 --step alert-generator-code-node` | `--no-write` |
| Send email | `snickerdoodle run mycroft-news-intelligence-agent-2 --step send-email` | `--no-write` |
| DailyGeneratorCode | `snickerdoodle run mycroft-news-intelligence-agent-2 --step dailygeneratorcode` | `--no-write` |
| Webhook | `snickerdoodle run mycroft-news-intelligence-agent-2 --step webhook` | `--no-write` |
| Respond to Webhook | `snickerdoodle run mycroft-news-intelligence-agent-2 --step respond-to-webhook` | `--no-write` |
| Produce human report | `snickerdoodle run mycroft-news-intelligence-agent-2 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-news-intelligence-agent-2 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-news-intelligence-agent-2 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-news-intelligence-agent-2 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| normalizenewsapi | `scripts/gigo/mycroft-news-intelligence-agent-2__normalizenewsapi.py` | gigo |
| NewsApiKey | `scripts/ingest/mycroft-news-intelligence-agent-2__newsapikey.py` | ingest |
| HTTP Request | `scripts/ingest/mycroft-news-intelligence-agent-2__http-request.py` | ingest |
| XML | `scripts/gigo/mycroft-news-intelligence-agent-2__xml.py` | gigo |
| ProcessNewData | `scripts/gigo/mycroft-news-intelligence-agent-2__processnewdata.py` | gigo |
| HTTP Request1 | `scripts/ingest/mycroft-news-intelligence-agent-2__http-request1.py` | ingest |
| RiskCalculator | `scripts/tools/mycroft-news-intelligence-agent-2__riskcalculator.py` | tool |
| Insert rows in a table | `scripts/gigo/mycroft-news-intelligence-agent-2__insert-rows-in-a-table.py` | gigo |
| Alert Generator Code Node | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__alert-generator-code-node.py` | tool |
| Send email | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__send-email.py` | tool |
| DailyGeneratorCode | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__dailygeneratorcode.py` | tool |
| Webhook | `scripts/tools/mycroft-news-intelligence-agent-2__webhook.py` | tool |
| Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__respond-to-webhook.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-2__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-news-intelligence-agent-2/` | JSON |
| Verified data | `data/verified/mycroft-news-intelligence-agent-2/` | JSON |
| Agent log | `logs/mycroft-news-intelligence-agent-2-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-news-intelligence-agent-2-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json`

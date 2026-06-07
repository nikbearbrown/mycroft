# Mycroft - News Intelligence Agent

## Purpose

Mycroft - News Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - news intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| NewsApiKey | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| HTTP Request | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| HTTP Request1 | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Company List | code | gigo |
| Build Query | code | gigo |
| Merge | merge | conductor |
| normalizenewsapi | code | gigo |
| NewsApiKey | httpRequest | ingest |
| HTTP Request | httpRequest | ingest |
| XML | xml | gigo |
| ProcessNewData | code | gigo |
| Edit Fields | set | gigo |
| HTTP Request1 | httpRequest | ingest |
| RiskCalculator | code | gigo |
| Insert rows in a table | postgres | gigo |
| Alert Generator Code Node | code | gigo |
| Send email | emailSend | tool |
| DailyGeneratorCode | code | gigo |
| Webhook | webhook | conductor |
| Respond to Webhook | respondToWebhook | conductor |
| Set Variables | set | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-news-intelligence-agent-2.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-news-intelligence-agent-2 data/verified/n8n-mycroft-news-intelligence-agent-2 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-news-intelligence-agent-2.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Company List. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__company-list.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
3. Step name: Build Query. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__build-query.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
4. Step name: normalizenewsapi. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__normalizenewsapi.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
5. Step name: NewsApiKey. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-news-intelligence-agent-2__newsapikey.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-news-intelligence-agent-2/.
6. Step name: HTTP Request. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-news-intelligence-agent-2__http-request.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-news-intelligence-agent-2/.
7. Step name: XML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
8. Step name: ProcessNewData. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__processnewdata.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
9. Step name: Edit Fields. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__edit-fields.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
10. Step name: HTTP Request1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-news-intelligence-agent-2__http-request1.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-news-intelligence-agent-2/.
11. Step name: RiskCalculator. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__riskcalculator.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
12. Step name: Insert rows in a table. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__insert-rows-in-a-table.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
13. Step name: Alert Generator Code Node. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__alert-generator-code-node.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
14. Step name: Send email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-news-intelligence-agent-2__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: DailyGeneratorCode. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__dailygeneratorcode.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
16. Step name: Set Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__set-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-news-intelligence-agent-2/.
17. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-news-intelligence-agent-2__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroft-news-intelligence-agent-2-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroft-news-intelligence-agent-2-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - News Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Company List | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step company-list` |  |
| Build Query | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step build-query` |  |
| normalizenewsapi | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step normalizenewsapi` |  |
| NewsApiKey | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step newsapikey` | `--sample` |
| HTTP Request | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step http-request` | `--sample` |
| XML | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step xml` |  |
| ProcessNewData | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step processnewdata` |  |
| Edit Fields | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step edit-fields` |  |
| HTTP Request1 | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step http-request1` | `--sample` |
| RiskCalculator | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step riskcalculator` |  |
| Insert rows in a table | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step insert-rows-in-a-table` |  |
| Alert Generator Code Node | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step alert-generator-code-node` |  |
| Send email | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step send-email` | `--no-write` |
| DailyGeneratorCode | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step dailygeneratorcode` |  |
| Set Variables | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step set-variables` |  |
| Produce human report | `snickerdoodle run n8n-mycroft-news-intelligence-agent-2 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroft-news-intelligence-agent-2 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroft-news-intelligence-agent-2 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroft-news-intelligence-agent-2 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Company List | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__company-list.py` | gigo |
| Build Query | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__build-query.py` | gigo |
| normalizenewsapi | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__normalizenewsapi.py` | gigo |
| NewsApiKey | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-news-intelligence-agent-2__newsapikey.py` | ingest |
| HTTP Request | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-news-intelligence-agent-2__http-request.py` | ingest |
| XML | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__xml.py` | gigo |
| ProcessNewData | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__processnewdata.py` | gigo |
| Edit Fields | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__edit-fields.py` | gigo |
| HTTP Request1 | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-news-intelligence-agent-2__http-request1.py` | ingest |
| RiskCalculator | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__riskcalculator.py` | gigo |
| Insert rows in a table | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__insert-rows-in-a-table.py` | gigo |
| Alert Generator Code Node | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__alert-generator-code-node.py` | gigo |
| Send email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-news-intelligence-agent-2__send-email.py` | tool |
| DailyGeneratorCode | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__dailygeneratorcode.py` | gigo |
| Set Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-news-intelligence-agent-2__set-variables.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-news-intelligence-agent-2__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-news-intelligence-agent-2/` | JSON |
| Verified data | `data/verified/n8n-mycroft-news-intelligence-agent-2/` | JSON |
| Agent log | `logs/n8n-mycroft-news-intelligence-agent-2-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-news-intelligence-agent-2-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json`

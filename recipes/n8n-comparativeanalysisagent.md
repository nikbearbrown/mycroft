# ComparativeAnalysisAgent

## Purpose

ComparativeAnalysisAgent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to comparativeanalysisagent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch Financial Overview | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch Financial Time Series | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| HTTP Request | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| HTTP Request1 | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When clicking ‘Execute workflow’ | manualTrigger | conductor |
| Peer Company List | code | gigo |
| Subsector | set | gigo |
| Store Variables & Keys | code | gigo |
| Fetch Financial Overview | httpRequest | ingest |
| Fetch Financial Time Series | httpRequest | ingest |
| Merge | merge | conductor |
| Code in JavaScript | code | gigo |
| Loop - News | splitInBatches | conductor |
| HTTP Request | httpRequest | ingest |
| Code in Python (Beta)1 | code | gigo |
| Loop Over Items | splitInBatches | conductor |
| HTTP Request1 | httpRequest | ingest |
| Code in Python (Beta) | code | gigo |
| Aggregate | aggregate | gigo |
| Aggregate1 | aggregate | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-comparativeanalysisagent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-comparativeanalysisagent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-comparativeanalysisagent data/verified/n8n-comparativeanalysisagent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-comparativeanalysisagent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Peer Company List. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__peer-company-list.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
3. Step name: Subsector. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__subsector.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
4. Step name: Store Variables & Keys. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__store-variables-and-keys.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
5. Step name: Fetch Financial Overview. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__fetch-financial-overview.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-comparativeanalysisagent/.
6. Step name: Fetch Financial Time Series. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__fetch-financial-time-series.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-comparativeanalysisagent/.
7. Step name: Code in JavaScript. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__code-in-javascript.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
8. Step name: HTTP Request. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__http-request.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-comparativeanalysisagent/.
9. Step name: Code in Python (Beta)1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__code-in-python-beta-1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
10. Step name: HTTP Request1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__http-request1.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-comparativeanalysisagent/.
11. Step name: Code in Python (Beta). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__code-in-python-beta.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
12. Step name: Aggregate. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__aggregate.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
13. Step name: Aggregate1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__aggregate1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-comparativeanalysisagent/.
14. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-comparativeanalysisagent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-comparativeanalysisagent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-comparativeanalysisagent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `ComparativeAnalysisAgent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-comparativeanalysisagent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-comparativeanalysisagent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Peer Company List | `snickerdoodle run n8n-comparativeanalysisagent --step peer-company-list` |  |
| Subsector | `snickerdoodle run n8n-comparativeanalysisagent --step subsector` |  |
| Store Variables & Keys | `snickerdoodle run n8n-comparativeanalysisagent --step store-variables-and-keys` |  |
| Fetch Financial Overview | `snickerdoodle run n8n-comparativeanalysisagent --step fetch-financial-overview` | `--sample` |
| Fetch Financial Time Series | `snickerdoodle run n8n-comparativeanalysisagent --step fetch-financial-time-series` | `--sample` |
| Code in JavaScript | `snickerdoodle run n8n-comparativeanalysisagent --step code-in-javascript` |  |
| HTTP Request | `snickerdoodle run n8n-comparativeanalysisagent --step http-request` | `--sample` |
| Code in Python (Beta)1 | `snickerdoodle run n8n-comparativeanalysisagent --step code-in-python-beta-1` |  |
| HTTP Request1 | `snickerdoodle run n8n-comparativeanalysisagent --step http-request1` | `--sample` |
| Code in Python (Beta) | `snickerdoodle run n8n-comparativeanalysisagent --step code-in-python-beta` |  |
| Aggregate | `snickerdoodle run n8n-comparativeanalysisagent --step aggregate` |  |
| Aggregate1 | `snickerdoodle run n8n-comparativeanalysisagent --step aggregate1` |  |
| Produce human report | `snickerdoodle run n8n-comparativeanalysisagent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-comparativeanalysisagent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-comparativeanalysisagent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-comparativeanalysisagent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Peer Company List | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__peer-company-list.py` | gigo |
| Subsector | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__subsector.py` | gigo |
| Store Variables & Keys | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__store-variables-and-keys.py` | gigo |
| Fetch Financial Overview | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__fetch-financial-overview.py` | ingest |
| Fetch Financial Time Series | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__fetch-financial-time-series.py` | ingest |
| Code in JavaScript | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__code-in-javascript.py` | gigo |
| HTTP Request | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__http-request.py` | ingest |
| Code in Python (Beta)1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__code-in-python-beta-1.py` | gigo |
| HTTP Request1 | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-comparativeanalysisagent__http-request1.py` | ingest |
| Code in Python (Beta) | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__code-in-python-beta.py` | gigo |
| Aggregate | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__aggregate.py` | gigo |
| Aggregate1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-comparativeanalysisagent__aggregate1.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-comparativeanalysisagent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-comparativeanalysisagent/` | JSON |
| Verified data | `data/verified/n8n-comparativeanalysisagent/` | JSON |
| Agent log | `logs/n8n-comparativeanalysisagent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-comparativeanalysisagent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json`

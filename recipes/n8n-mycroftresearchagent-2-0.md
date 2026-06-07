# MycroftResearchAgent_2.0

## Purpose

MycroftResearchAgent_2.0 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroftresearchagent_2.0. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Get Financial Overview1 | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Get Income Statement1 | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Google Search Patent | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Get Earnings Data | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When clicking ‘Execute workflow’ | manualTrigger | conductor |
| Company Input | set | gigo |
| Get Financial Overview1 | httpRequest | ingest |
| Get Income Statement1 | httpRequest | ingest |
| Process Company Data1 | code | gigo |
| Google Search Patent | httpRequest | ingest |
| Process Patent Data1 | code | gigo |
| Process Financial Data1 | code | gigo |
| Generate Analysis1 | code | gigo |
| Generate Final Report1 | code | gigo |
| Merge | merge | conductor |
| Get Earnings Data | httpRequest | ingest |
| Process Earnings Data | code | gigo |
| Get Competitive Analysis | code | gigo |
| Merge Competitive Analysis | code | conductor |
| Investment Report | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroftresearchagent-2-0.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroftresearchagent-2-0 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroftresearchagent-2-0 data/verified/n8n-mycroftresearchagent-2-0 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroftresearchagent-2-0.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Company Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__company-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
3. Step name: Get Financial Overview1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__get-financial-overview1.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroftresearchagent-2-0/.
4. Step name: Get Income Statement1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__get-income-statement1.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroftresearchagent-2-0/.
5. Step name: Process Company Data1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-company-data1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
6. Step name: Google Search Patent. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__google-search-patent.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroftresearchagent-2-0/.
7. Step name: Process Patent Data1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-patent-data1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
8. Step name: Process Financial Data1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-financial-data1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
9. Step name: Generate Analysis1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__generate-analysis1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
10. Step name: Generate Final Report1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__generate-final-report1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
11. Step name: Get Earnings Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__get-earnings-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroftresearchagent-2-0/.
12. Step name: Process Earnings Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-earnings-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
13. Step name: Get Competitive Analysis. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__get-competitive-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
14. Step name: Investment Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__investment-report.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroftresearchagent-2-0/.
15. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroftresearchagent-2-0__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroftresearchagent-2-0-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroftresearchagent-2-0-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `MycroftResearchAgent_2.0` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroftresearchagent-2-0 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroftresearchagent-2-0 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Company Input | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step company-input` |  |
| Get Financial Overview1 | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step get-financial-overview1` | `--sample` |
| Get Income Statement1 | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step get-income-statement1` | `--sample` |
| Process Company Data1 | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step process-company-data1` |  |
| Google Search Patent | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step google-search-patent` | `--sample` |
| Process Patent Data1 | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step process-patent-data1` |  |
| Process Financial Data1 | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step process-financial-data1` |  |
| Generate Analysis1 | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step generate-analysis1` |  |
| Generate Final Report1 | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step generate-final-report1` |  |
| Get Earnings Data | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step get-earnings-data` | `--sample` |
| Process Earnings Data | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step process-earnings-data` |  |
| Get Competitive Analysis | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step get-competitive-analysis` |  |
| Investment Report | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step investment-report` |  |
| Produce human report | `snickerdoodle run n8n-mycroftresearchagent-2-0 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroftresearchagent-2-0 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroftresearchagent-2-0 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroftresearchagent-2-0 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Company Input | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__company-input.py` | gigo |
| Get Financial Overview1 | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__get-financial-overview1.py` | ingest |
| Get Income Statement1 | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__get-income-statement1.py` | ingest |
| Process Company Data1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-company-data1.py` | gigo |
| Google Search Patent | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__google-search-patent.py` | ingest |
| Process Patent Data1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-patent-data1.py` | gigo |
| Process Financial Data1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-financial-data1.py` | gigo |
| Generate Analysis1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__generate-analysis1.py` | gigo |
| Generate Final Report1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__generate-final-report1.py` | gigo |
| Get Earnings Data | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroftresearchagent-2-0__get-earnings-data.py` | ingest |
| Process Earnings Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__process-earnings-data.py` | gigo |
| Get Competitive Analysis | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__get-competitive-analysis.py` | gigo |
| Investment Report | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroftresearchagent-2-0__investment-report.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroftresearchagent-2-0__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroftresearchagent-2-0/` | JSON |
| Verified data | `data/verified/n8n-mycroftresearchagent-2-0/` | JSON |
| Agent log | `logs/n8n-mycroftresearchagent-2-0-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroftresearchagent-2-0-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json`

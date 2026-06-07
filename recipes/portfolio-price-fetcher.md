# Portfolio Price Fetcher

## Purpose

Portfolio Price Fetcher defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to portfolio price fetcher. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Define Portfolio | `code` | conductor |
| Fetch Stock Prices | `httpRequest` | ingest |
| Calculate Metrics | `code` | tool |
| Aggregate Summary | `code` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (3 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Visualization_Agent/Portfolio Price Fetcher.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Visualization_Agent/Portfolio Price Fetcher.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/portfolio-price-fetcher.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run portfolio-price-fetcher --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/portfolio-price-fetcher data/verified/portfolio-price-fetcher -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/portfolio-price-fetcher.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Visualization_Agent/Portfolio Price Fetcher.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Fetch Stock Prices. Labor: AI with Human gate.
   Script called: `scripts/ingest/portfolio-price-fetcher__fetch-stock-prices.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/portfolio-price-fetcher/.
3. Step name: Calculate Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-price-fetcher__calculate-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/portfolio-price-fetcher__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/portfolio-price-fetcher-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/portfolio-price-fetcher-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Portfolio Price Fetcher` run.
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
`snickerdoodle run portfolio-price-fetcher --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run portfolio-price-fetcher --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Fetch Stock Prices | `snickerdoodle run portfolio-price-fetcher --step fetch-stock-prices` | `--sample` |
| Calculate Metrics | `snickerdoodle run portfolio-price-fetcher --step calculate-metrics` | `--no-write` |
| Produce human report | `snickerdoodle run portfolio-price-fetcher --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate portfolio-price-fetcher --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate portfolio-price-fetcher --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate portfolio-price-fetcher --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Fetch Stock Prices | `scripts/ingest/portfolio-price-fetcher__fetch-stock-prices.py` | ingest |
| Calculate Metrics | `scripts/tools/portfolio-price-fetcher__calculate-metrics.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/portfolio-price-fetcher__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/portfolio-price-fetcher/` | JSON |
| Verified data | `data/verified/portfolio-price-fetcher/` | JSON |
| Agent log | `logs/portfolio-price-fetcher-[DATE].json` | JSON |
| Human report | `reports/generated/portfolio-price-fetcher-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Visualization_Agent/Portfolio Price Fetcher.json`

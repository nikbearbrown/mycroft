# ComparativeAnalysisAgent

## Purpose

ComparativeAnalysisAgent compares peer companies within an AI subsector using financial fundamentals, price momentum, recent news sentiment, and AI patent activity so a human analyst can see relative position without treating any single signal as an investment decision.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Subsector | String | Recipe default: `Cloud Infrastructure` | Confirm source is allowed, current, and rate-safe before live fetch. |
| Peer company list | JSON | `scripts/gigo/comparative_peer_company_list.py` | Confirm source is allowed, current, and rate-safe before live fetch. |
| Financial overview | JSON | Alpha Vantage or local export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Financial time series | JSON | Alpha Vantage or local export | Confirm source is allowed, current, and rate-safe before live fetch. |
| News articles | JSON | NewsAPI or local export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Patent results | JSON | SerpAPI Google Patents or local export | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json` | Yes |
| Subsector | String | Recipe default: `Cloud Infrastructure` | Yes |
| Peer company list | JSON | `scripts/gigo/comparative_peer_company_list.py` | Yes |
| Financial overview | JSON | Alpha Vantage or local export | Yes |
| Financial time series | JSON | Alpha Vantage or local export | Yes |
| News articles | JSON | NewsAPI or local export | No |
| Patent results | JSON | SerpAPI Google Patents or local export | No |
| API credentials | Environment variables | `ALPHA_VANTAGE_API_KEY`, `NEWSAPI_KEY`, `SERPAPI_KEY` | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/comparativeanalysisagent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run comparativeanalysisagent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/comparativeanalysisagent data/verified/comparativeanalysisagent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/comparativeanalysisagent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: comparative_peer_company_list. Labor: AI with Human gate.
   Script called: `scripts/gigo/comparative_peer_company_list.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/comparativeanalysisagent/.
3. Step name: comparative_store_variables. Labor: AI with Human gate.
   Script called: `scripts/gigo/comparative_store_variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/comparativeanalysisagent/.
4. Step name: fetch_comparative_financial_overview. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_comparative_financial_overview.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/comparativeanalysisagent/.
5. Step name: calculate_comparative_financial_metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/calculate_comparative_financial_metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: fetch_comparative_news. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_comparative_news.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/comparativeanalysisagent/.
7. Step name: fetch_comparative_patents. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_comparative_patents.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/comparativeanalysisagent/.
8. Step name: aggregate_comparative_financials. Labor: AI with Human gate.
   Script called: `scripts/tools/aggregate_comparative_financials.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/comparativeanalysisagent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/comparativeanalysisagent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/comparativeanalysisagent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `ComparativeAnalysisAgent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if subsector is not mapped to a peer group.
- Stop if live API calls are requested without env-var credentials and approval.
- Stop if financial metric payloads are missing for every peer.
- Stop if any script invents financial values rather than marking them missing.
- Stop before investment conclusions without human interpretation.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run comparativeanalysisagent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run comparativeanalysisagent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| comparative_peer_company_list | `snickerdoodle run comparativeanalysisagent --step comparative-peer-company-list` |  |
| comparative_store_variables | `snickerdoodle run comparativeanalysisagent --step comparative-store-variables` |  |
| fetch_comparative_financial_overview | `snickerdoodle run comparativeanalysisagent --step fetch-comparative-financial-overview` | `--sample` |
| calculate_comparative_financial_metrics | `snickerdoodle run comparativeanalysisagent --step calculate-comparative-financial-metrics` | `--no-write` |
| fetch_comparative_news | `snickerdoodle run comparativeanalysisagent --step fetch-comparative-news` | `--sample` |
| fetch_comparative_patents | `snickerdoodle run comparativeanalysisagent --step fetch-comparative-patents` | `--sample` |
| aggregate_comparative_financials | `snickerdoodle run comparativeanalysisagent --step aggregate-comparative-financials` | `--no-write` |
| Produce human report | `snickerdoodle run comparativeanalysisagent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate comparativeanalysisagent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate comparativeanalysisagent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate comparativeanalysisagent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| comparative_peer_company_list | `scripts/gigo/comparative_peer_company_list.py` | gigo |
| comparative_store_variables | `scripts/gigo/comparative_store_variables.py` | gigo |
| fetch_comparative_financial_overview | `scripts/ingest/fetch_comparative_financial_overview.py` | ingest |
| calculate_comparative_financial_metrics | `scripts/tools/calculate_comparative_financial_metrics.py` | tool |
| fetch_comparative_news | `scripts/ingest/fetch_comparative_news.py` | ingest |
| fetch_comparative_patents | `scripts/ingest/fetch_comparative_patents.py` | ingest |
| aggregate_comparative_financials | `scripts/tools/aggregate_comparative_financials.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/comparativeanalysisagent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/comparativeanalysisagent/` | JSON |
| Verified data | `data/verified/comparativeanalysisagent/` | JSON |
| Agent log | `logs/comparativeanalysisagent-[DATE].json` | JSON |
| Human report | `reports/generated/comparativeanalysisagent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json`

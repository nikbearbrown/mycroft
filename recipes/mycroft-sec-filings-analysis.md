# Mycroft - SEC_Filings_Analysis

## Purpose

Mycroft - SEC_Filings_Analysis defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - sec_filings_analysis. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Original workflow sources | [TODO: DEV] Parse original workflow node types. | [TODO: DATA SOURCE] Extract source URLs or paths from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When clicking 'Execute workflow' | `manualTrigger` | conductor |
| If | `if` | conductor |
| Set Variables | `set` | conductor |
| Setup Github Repo | `executeCommand` | tool |
| Set Path Variables | `code` | conductor |
| Setup Python Enviornment and Output Directories | `executeCommand` | tool |
| Edgar_Fetcher | `executeCommand` | tool |
| Validate Fetcher | `code` | conductor |
| Financial Analyzer | `executeCommand` | tool |
| Narrative Parser | `executeCommand` | tool |
| Validate Financial Metrics | `code` | tool |
| Validate Narrative Content | `code` | conductor |
| Cleanup Temp Directories | `executeCommand` | tool |
| Error Handling | `code` | conductor |
| Cleanup | `executeCommand` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (8 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (7 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-sec-filings-analysis.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-sec-filings-analysis --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-sec-filings-analysis data/verified/mycroft-sec-filings-analysis -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-sec-filings-analysis.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Setup Python Enviornment and Output Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__setup-python-enviornment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Edgar_Fetcher. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__edgar-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Financial Analyzer. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__financial-analyzer.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Narrative Parser. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__narrative-parser.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Validate Financial Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__validate-financial-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Cleanup Temp Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__cleanup-temp-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Cleanup. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis__cleanup-temp-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-sec-filings-analysis-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-sec-filings-analysis-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - SEC_Filings_Analysis` run.
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
`snickerdoodle run mycroft-sec-filings-analysis --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-sec-filings-analysis --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Setup Github Repo | `snickerdoodle run mycroft-sec-filings-analysis --step setup-github-repo` | `--no-write` |
| Setup Python Enviornment and Output Directories | `snickerdoodle run mycroft-sec-filings-analysis --step setup-python-enviornment-and-output-directories` | `--no-write` |
| Edgar_Fetcher | `snickerdoodle run mycroft-sec-filings-analysis --step edgar-fetcher` | `--no-write` |
| Financial Analyzer | `snickerdoodle run mycroft-sec-filings-analysis --step financial-analyzer` | `--no-write` |
| Narrative Parser | `snickerdoodle run mycroft-sec-filings-analysis --step narrative-parser` | `--no-write` |
| Validate Financial Metrics | `snickerdoodle run mycroft-sec-filings-analysis --step validate-financial-metrics` | `--no-write` |
| Cleanup Temp Directories | `snickerdoodle run mycroft-sec-filings-analysis --step cleanup-temp-directories` | `--no-write` |
| Cleanup | `snickerdoodle run mycroft-sec-filings-analysis --step cleanup` | `--no-write` |
| Produce human report | `snickerdoodle run mycroft-sec-filings-analysis --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-sec-filings-analysis --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-sec-filings-analysis --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-sec-filings-analysis --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Setup Github Repo | `scripts/tools/mycroft-sec-filings-analysis__setup-github-repo.py` | tool |
| Setup Python Enviornment and Output Directories | `scripts/tools/mycroft-sec-filings-analysis__setup-python-enviornment-and-output-directories.py` | tool |
| Edgar_Fetcher | `scripts/tools/mycroft-sec-filings-analysis__edgar-fetcher.py` | tool |
| Financial Analyzer | `scripts/tools/mycroft-sec-filings-analysis__financial-analyzer.py` | tool |
| Narrative Parser | `scripts/tools/mycroft-sec-filings-analysis__narrative-parser.py` | tool |
| Validate Financial Metrics | `scripts/tools/mycroft-sec-filings-analysis__validate-financial-metrics.py` | tool |
| Cleanup Temp Directories | `scripts/tools/mycroft-sec-filings-analysis__cleanup-temp-directories.py` | tool |
| Cleanup | `scripts/tools/mycroft-sec-filings-analysis__cleanup-temp-directories.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-sec-filings-analysis/` | JSON |
| Verified data | `data/verified/mycroft-sec-filings-analysis/` | JSON |
| Agent log | `logs/mycroft-sec-filings-analysis-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-sec-filings-analysis-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/SEC_Filings_Analysis_Agent/Mycroft - SEC_Filings_Analysis.json`

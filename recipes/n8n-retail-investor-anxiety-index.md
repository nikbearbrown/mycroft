# Retail Investor Anxiety Index

## Purpose

Retail Investor Anxiety Index defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to retail investor anxiety index. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch WSB | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch Investing | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch Stocks | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Insert to Supabase | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Schedule Trigger | scheduleTrigger | conductor |
| Manual Run Trigger | webhook | conductor |
| Fetch WSB | httpRequest | ingest |
| Fetch Investing | httpRequest | ingest |
| Fetch Stocks | httpRequest | ingest |
| Merge Reddit Feeds | merge | conductor |
| 1A: Raw Merge & Structural Clean | code | conductor |
| 1B: Linguistic & Relevance Filter | code | conductor |
| Keyword Pre-Scorer | code | gigo |
| Aggregate for Claude | code | gigo |
| Claude 1: Anxiety Score | chainLlm | gigo |
| Claude 2: Narrative Velocity | chainLlm | gigo |
| Claude 3: Herd Detection | chainLlm | gigo |
| Claude 4: Conviction vs Uncertainty | chainLlm | gigo |
| Claude 5: Crowd Cycle Stage | chainLlm | gigo |
| Anthropic Model 1 | lmChatAnthropic | gigo |
| Anthropic Model 2 | lmChatAnthropic | gigo |
| Anthropic Model 3 | lmChatAnthropic | gigo |
| Anthropic Model 4 | lmChatAnthropic | gigo |
| Anthropic Model 5 | lmChatAnthropic | gigo |
| Merge Claude Outputs | merge | conductor |
| Signal Aggregator | code | gigo |
| Persist to File | code | gigo |
| Generate Quickchart URLs | code | gigo |
| Write output.json | code | tool |
| Insert to Supabase | httpRequest | ingest |
| Pipeline Response | respondToWebhook | conductor |
| Dashboard Webhook | webhook | conductor |
| Build Dashboard Response | code | gigo |
| Serve Dashboard HTML | respondToWebhook | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-retail-investor-anxiety-index.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-retail-investor-anxiety-index --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-retail-investor-anxiety-index data/verified/n8n-retail-investor-anxiety-index -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-retail-investor-anxiety-index.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Fetch WSB. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__fetch-wsb.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-retail-investor-anxiety-index/.
3. Step name: Fetch Investing. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__fetch-investing.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-retail-investor-anxiety-index/.
4. Step name: Fetch Stocks. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__fetch-stocks.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-retail-investor-anxiety-index/.
5. Step name: Keyword Pre-Scorer. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__keyword-pre-scorer.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
6. Step name: Aggregate for Claude. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__aggregate-for-claude.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
7. Step name: Claude 1: Anxiety Score. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-1-anxiety-score.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
8. Step name: Claude 2: Narrative Velocity. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-2-narrative-velocity.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
9. Step name: Claude 3: Herd Detection. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-3-herd-detection.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
10. Step name: Claude 4: Conviction vs Uncertainty. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-4-conviction-vs-uncertainty.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
11. Step name: Claude 5: Crowd Cycle Stage. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-5-crowd-cycle-stage.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
12. Step name: Anthropic Model 1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
13. Step name: Anthropic Model 2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
14. Step name: Anthropic Model 3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
15. Step name: Anthropic Model 4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
16. Step name: Anthropic Model 5. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-5.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
17. Step name: Signal Aggregator. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__signal-aggregator.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
18. Step name: Persist to File. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__persist-to-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
19. Step name: Generate Quickchart URLs. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__generate-quickchart-urls.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
20. Step name: Write output.json. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-retail-investor-anxiety-index__write-output-json.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
21. Step name: Insert to Supabase. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__insert-to-supabase.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-retail-investor-anxiety-index/.
22. Step name: Build Dashboard Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__build-dashboard-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-retail-investor-anxiety-index/.
23. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-retail-investor-anxiety-index__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-retail-investor-anxiety-index-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-retail-investor-anxiety-index-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Retail Investor Anxiety Index` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-retail-investor-anxiety-index --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-retail-investor-anxiety-index --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Fetch WSB | `snickerdoodle run n8n-retail-investor-anxiety-index --step fetch-wsb` | `--sample` |
| Fetch Investing | `snickerdoodle run n8n-retail-investor-anxiety-index --step fetch-investing` | `--sample` |
| Fetch Stocks | `snickerdoodle run n8n-retail-investor-anxiety-index --step fetch-stocks` | `--sample` |
| Keyword Pre-Scorer | `snickerdoodle run n8n-retail-investor-anxiety-index --step keyword-pre-scorer` |  |
| Aggregate for Claude | `snickerdoodle run n8n-retail-investor-anxiety-index --step aggregate-for-claude` |  |
| Claude 1: Anxiety Score | `snickerdoodle run n8n-retail-investor-anxiety-index --step claude-1-anxiety-score` |  |
| Claude 2: Narrative Velocity | `snickerdoodle run n8n-retail-investor-anxiety-index --step claude-2-narrative-velocity` |  |
| Claude 3: Herd Detection | `snickerdoodle run n8n-retail-investor-anxiety-index --step claude-3-herd-detection` |  |
| Claude 4: Conviction vs Uncertainty | `snickerdoodle run n8n-retail-investor-anxiety-index --step claude-4-conviction-vs-uncertainty` |  |
| Claude 5: Crowd Cycle Stage | `snickerdoodle run n8n-retail-investor-anxiety-index --step claude-5-crowd-cycle-stage` |  |
| Anthropic Model 1 | `snickerdoodle run n8n-retail-investor-anxiety-index --step anthropic-model-1` |  |
| Anthropic Model 2 | `snickerdoodle run n8n-retail-investor-anxiety-index --step anthropic-model-2` |  |
| Anthropic Model 3 | `snickerdoodle run n8n-retail-investor-anxiety-index --step anthropic-model-3` |  |
| Anthropic Model 4 | `snickerdoodle run n8n-retail-investor-anxiety-index --step anthropic-model-4` |  |
| Anthropic Model 5 | `snickerdoodle run n8n-retail-investor-anxiety-index --step anthropic-model-5` |  |
| Signal Aggregator | `snickerdoodle run n8n-retail-investor-anxiety-index --step signal-aggregator` |  |
| Persist to File | `snickerdoodle run n8n-retail-investor-anxiety-index --step persist-to-file` |  |
| Generate Quickchart URLs | `snickerdoodle run n8n-retail-investor-anxiety-index --step generate-quickchart-urls` |  |
| Write output.json | `snickerdoodle run n8n-retail-investor-anxiety-index --step write-output-json` | `--no-write` |
| Insert to Supabase | `snickerdoodle run n8n-retail-investor-anxiety-index --step insert-to-supabase` | `--sample` |
| Build Dashboard Response | `snickerdoodle run n8n-retail-investor-anxiety-index --step build-dashboard-response` |  |
| Produce human report | `snickerdoodle run n8n-retail-investor-anxiety-index --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-retail-investor-anxiety-index --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-retail-investor-anxiety-index --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-retail-investor-anxiety-index --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Fetch WSB | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__fetch-wsb.py` | ingest |
| Fetch Investing | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__fetch-investing.py` | ingest |
| Fetch Stocks | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__fetch-stocks.py` | ingest |
| Keyword Pre-Scorer | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__keyword-pre-scorer.py` | gigo |
| Aggregate for Claude | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__aggregate-for-claude.py` | gigo |
| Claude 1: Anxiety Score | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-1-anxiety-score.py` | gigo |
| Claude 2: Narrative Velocity | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-2-narrative-velocity.py` | gigo |
| Claude 3: Herd Detection | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-3-herd-detection.py` | gigo |
| Claude 4: Conviction vs Uncertainty | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-4-conviction-vs-uncertainty.py` | gigo |
| Claude 5: Crowd Cycle Stage | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__claude-5-crowd-cycle-stage.py` | gigo |
| Anthropic Model 1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-1.py` | gigo |
| Anthropic Model 2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-2.py` | gigo |
| Anthropic Model 3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-3.py` | gigo |
| Anthropic Model 4 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-4.py` | gigo |
| Anthropic Model 5 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__anthropic-model-5.py` | gigo |
| Signal Aggregator | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__signal-aggregator.py` | gigo |
| Persist to File | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__persist-to-file.py` | gigo |
| Generate Quickchart URLs | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__generate-quickchart-urls.py` | gigo |
| Write output.json | `[TODO: DEV] Create or map script path: scripts/tools/n8n-retail-investor-anxiety-index__write-output-json.py` | tool |
| Insert to Supabase | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-retail-investor-anxiety-index__insert-to-supabase.py` | ingest |
| Build Dashboard Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-retail-investor-anxiety-index__build-dashboard-response.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-retail-investor-anxiety-index__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-retail-investor-anxiety-index/` | JSON |
| Verified data | `data/verified/n8n-retail-investor-anxiety-index/` | JSON |
| Agent log | `logs/n8n-retail-investor-anxiety-index-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-retail-investor-anxiety-index-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json`

# Retail Investor Anxiety Index

## Purpose

Retail Investor Anxiety Index defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to retail investor anxiety index. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (4 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Schedule Trigger | `scheduleTrigger` | conductor |
| Manual Run Trigger | `webhook` | tool |
| Fetch WSB | `httpRequest` | ingest |
| Fetch Investing | `httpRequest` | ingest |
| Fetch Stocks | `httpRequest` | ingest |
| Merge Reddit Feeds | `merge` | conductor |
| 1A: Raw Merge & Structural Clean | `code` | gigo |
| 1B: Linguistic & Relevance Filter | `code` | gigo |
| Keyword Pre-Scorer | `code` | tool |
| Aggregate for Claude | `code` | conductor |
| Claude 1: Anxiety Score | `chainLlm` | tool |
| Claude 2: Narrative Velocity | `chainLlm` | tool |
| Claude 3: Herd Detection | `chainLlm` | tool |
| Claude 4: Conviction vs Uncertainty | `chainLlm` | tool |
| Claude 5: Crowd Cycle Stage | `chainLlm` | tool |
| Anthropic Model 1 | `lmChatAnthropic` | tool |
| Anthropic Model 2 | `lmChatAnthropic` | tool |
| Anthropic Model 3 | `lmChatAnthropic` | tool |
| Anthropic Model 4 | `lmChatAnthropic` | tool |
| Anthropic Model 5 | `lmChatAnthropic` | tool |
| Merge Claude Outputs | `merge` | conductor |
| Signal Aggregator | `code` | conductor |
| Persist to File | `code` | conductor |
| Generate Quickchart URLs | `code` | conductor |
| Write output.json | `code` | conductor |
| Insert to Supabase | `httpRequest` | ingest |
| Pipeline Response | `respondToWebhook` | report |
| Dashboard Webhook | `webhook` | tool |
| Build Dashboard Response | `code` | conductor |
| Serve Dashboard HTML | `respondToWebhook` | report |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (4 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (13 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (9 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/retail-investor-anxiety-index.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run retail-investor-anxiety-index --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/retail-investor-anxiety-index data/verified/retail-investor-anxiety-index -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/retail-investor-anxiety-index.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Manual Run Trigger. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__manual-run-trigger.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Fetch WSB. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index__fetch-wsb.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
4. Step name: Fetch Investing. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index__fetch-investing.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
5. Step name: Fetch Stocks. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index__fetch-stocks.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
6. Step name: 1A: Raw Merge & Structural Clean. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/retail-investor-anxiety-index__1a-raw-merge-and-structural-clean.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/retail-investor-anxiety-index/.
7. Step name: 1B: Linguistic & Relevance Filter. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/retail-investor-anxiety-index__1b-linguistic-and-relevance-filter.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/retail-investor-anxiety-index/.
8. Step name: Keyword Pre-Scorer. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__keyword-pre-scorer.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Claude 1: Anxiety Score. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__claude-1-anxiety-score.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Claude 2: Narrative Velocity. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__claude-2-narrative-velocity.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Claude 3: Herd Detection. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__claude-3-herd-detection.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Claude 4: Conviction vs Uncertainty. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__claude-4-conviction-vs-uncertainty.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Claude 5: Crowd Cycle Stage. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__claude-5-crowd-cycle-stage.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Anthropic Model 1. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Anthropic Model 2. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-2.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Anthropic Model 3. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-3.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Anthropic Model 4. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-4.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
18. Step name: Anthropic Model 5. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-5.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Insert to Supabase. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index__insert-to-supabase.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
20. Step name: Pipeline Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index__pipeline-response.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
21. Step name: Dashboard Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index__dashboard-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
22. Step name: Serve Dashboard HTML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index__serve-dashboard-html.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
23. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/retail-investor-anxiety-index-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/retail-investor-anxiety-index-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Retail Investor Anxiety Index` run.
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
`snickerdoodle run retail-investor-anxiety-index --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run retail-investor-anxiety-index --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Manual Run Trigger | `snickerdoodle run retail-investor-anxiety-index --step manual-run-trigger` | `--no-write` |
| Fetch WSB | `snickerdoodle run retail-investor-anxiety-index --step fetch-wsb` | `--sample` |
| Fetch Investing | `snickerdoodle run retail-investor-anxiety-index --step fetch-investing` | `--sample` |
| Fetch Stocks | `snickerdoodle run retail-investor-anxiety-index --step fetch-stocks` | `--sample` |
| 1A: Raw Merge & Structural Clean | `snickerdoodle run retail-investor-anxiety-index --step 1a-raw-merge-and-structural-clean` |  |
| 1B: Linguistic & Relevance Filter | `snickerdoodle run retail-investor-anxiety-index --step 1b-linguistic-and-relevance-filter` |  |
| Keyword Pre-Scorer | `snickerdoodle run retail-investor-anxiety-index --step keyword-pre-scorer` | `--no-write` |
| Claude 1: Anxiety Score | `snickerdoodle run retail-investor-anxiety-index --step claude-1-anxiety-score` | `--no-write` |
| Claude 2: Narrative Velocity | `snickerdoodle run retail-investor-anxiety-index --step claude-2-narrative-velocity` | `--no-write` |
| Claude 3: Herd Detection | `snickerdoodle run retail-investor-anxiety-index --step claude-3-herd-detection` | `--no-write` |
| Claude 4: Conviction vs Uncertainty | `snickerdoodle run retail-investor-anxiety-index --step claude-4-conviction-vs-uncertainty` | `--no-write` |
| Claude 5: Crowd Cycle Stage | `snickerdoodle run retail-investor-anxiety-index --step claude-5-crowd-cycle-stage` | `--no-write` |
| Anthropic Model 1 | `snickerdoodle run retail-investor-anxiety-index --step anthropic-model-1` | `--no-write` |
| Anthropic Model 2 | `snickerdoodle run retail-investor-anxiety-index --step anthropic-model-2` | `--no-write` |
| Anthropic Model 3 | `snickerdoodle run retail-investor-anxiety-index --step anthropic-model-3` | `--no-write` |
| Anthropic Model 4 | `snickerdoodle run retail-investor-anxiety-index --step anthropic-model-4` | `--no-write` |
| Anthropic Model 5 | `snickerdoodle run retail-investor-anxiety-index --step anthropic-model-5` | `--no-write` |
| Insert to Supabase | `snickerdoodle run retail-investor-anxiety-index --step insert-to-supabase` | `--sample` |
| Pipeline Response | `snickerdoodle run retail-investor-anxiety-index --step pipeline-response` | `--no-write` |
| Dashboard Webhook | `snickerdoodle run retail-investor-anxiety-index --step dashboard-webhook` | `--no-write` |
| Serve Dashboard HTML | `snickerdoodle run retail-investor-anxiety-index --step serve-dashboard-html` | `--no-write` |
| Produce human report | `snickerdoodle run retail-investor-anxiety-index --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate retail-investor-anxiety-index --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate retail-investor-anxiety-index --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate retail-investor-anxiety-index --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Manual Run Trigger | `scripts/tools/retail-investor-anxiety-index__manual-run-trigger.py` | tool |
| Fetch WSB | `scripts/ingest/retail-investor-anxiety-index__fetch-wsb.py` | ingest |
| Fetch Investing | `scripts/ingest/retail-investor-anxiety-index__fetch-investing.py` | ingest |
| Fetch Stocks | `scripts/ingest/retail-investor-anxiety-index__fetch-stocks.py` | ingest |
| 1A: Raw Merge & Structural Clean | `[TODO: DEV] Create or map script path: scripts/gigo/retail-investor-anxiety-index__1a-raw-merge-and-structural-clean.py` | gigo |
| 1B: Linguistic & Relevance Filter | `[TODO: DEV] Create or map script path: scripts/gigo/retail-investor-anxiety-index__1b-linguistic-and-relevance-filter.py` | gigo |
| Keyword Pre-Scorer | `scripts/tools/retail-investor-anxiety-index__keyword-pre-scorer.py` | tool |
| Claude 1: Anxiety Score | `scripts/tools/retail-investor-anxiety-index__claude-1-anxiety-score.py` | tool |
| Claude 2: Narrative Velocity | `scripts/tools/retail-investor-anxiety-index__claude-2-narrative-velocity.py` | tool |
| Claude 3: Herd Detection | `scripts/tools/retail-investor-anxiety-index__claude-3-herd-detection.py` | tool |
| Claude 4: Conviction vs Uncertainty | `scripts/tools/retail-investor-anxiety-index__claude-4-conviction-vs-uncertainty.py` | tool |
| Claude 5: Crowd Cycle Stage | `scripts/tools/retail-investor-anxiety-index__claude-5-crowd-cycle-stage.py` | tool |
| Anthropic Model 1 | `scripts/tools/retail-investor-anxiety-index__anthropic-model-1.py` | tool |
| Anthropic Model 2 | `scripts/tools/retail-investor-anxiety-index__anthropic-model-2.py` | tool |
| Anthropic Model 3 | `scripts/tools/retail-investor-anxiety-index__anthropic-model-3.py` | tool |
| Anthropic Model 4 | `scripts/tools/retail-investor-anxiety-index__anthropic-model-4.py` | tool |
| Anthropic Model 5 | `scripts/tools/retail-investor-anxiety-index__anthropic-model-5.py` | tool |
| Insert to Supabase | `scripts/ingest/retail-investor-anxiety-index__insert-to-supabase.py` | ingest |
| Pipeline Response | `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index__pipeline-response.py` | tool |
| Dashboard Webhook | `scripts/tools/retail-investor-anxiety-index__dashboard-webhook.py` | tool |
| Serve Dashboard HTML | `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index__serve-dashboard-html.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/retail-investor-anxiety-index/` | JSON |
| Verified data | `data/verified/retail-investor-anxiety-index/` | JSON |
| Agent log | `logs/retail-investor-anxiety-index-[DATE].json` | JSON |
| Human report | `reports/generated/retail-investor-anxiety-index-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json`

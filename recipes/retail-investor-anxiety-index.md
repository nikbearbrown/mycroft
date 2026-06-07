# Retail Investor Anxiety Index

## Purpose

Retail Investor Anxiety Index defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to retail investor anxiety index. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (4 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

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

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/retail-investor-anxiety-index.md" && rg -n "\[TODO: DEFINE]" "recipes/retail-investor-anxiety-index.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/retail-investor-anxiety-index/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/retail-investor-anxiety-index data/verified/retail-investor-anxiety-index -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/retail-investor-anxiety-index-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/retail-investor-anxiety-index.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/retail-investor-anxiety-index-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/retail-investor-anxiety-index.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/retail-investor-anxiety-index-[DATE].json && test -f reports/generated/retail-investor-anxiety-index-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `retail-investor-anxiety-index`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `retail-investor-anxiety-index`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/retail-investor-anxiety-index/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/retail-investor-anxiety-index-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `retail-investor-anxiety-index`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/retail-investor-anxiety-index/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/retail-investor-anxiety-index-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `retail-investor-anxiety-index`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/retail-investor-anxiety-index/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `retail-investor-anxiety-index`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `retail-investor-anxiety-index`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/retail-investor-anxiety-index-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/retail-investor-anxiety-index-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Retail Investor Anxiety Index` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

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
| Verify provenance | `snickerdoodle run retail-investor-anxiety-index --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run retail-investor-anxiety-index --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run retail-investor-anxiety-index --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run retail-investor-anxiety-index --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run retail-investor-anxiety-index --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run retail-investor-anxiety-index --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate retail-investor-anxiety-index --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate retail-investor-anxiety-index --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate retail-investor-anxiety-index --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate retail-investor-anxiety-index --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate retail-investor-anxiety-index --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate retail-investor-anxiety-index --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/retail-investor-anxiety-index-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/retail-investor-anxiety-index-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/retail-investor-anxiety-index-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/retail-investor-anxiety-index-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/retail-investor-anxiety-index-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/retail-investor-anxiety-index-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/retail-investor-anxiety-index/` | JSON |
| Verified data | `data/verified/retail-investor-anxiety-index/` | JSON |
| Agent log | `logs/retail-investor-anxiety-index-[DATE].json` | JSON |
| Human report | `reports/generated/retail-investor-anxiety-index-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Retail Investor Anxiety Index defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to retail investor anxiety index. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

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

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Manual Run Trigger. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-manual-run-trigger.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Fetch WSB. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index-fetch-wsb.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
4. Step name: Fetch Investing. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index-fetch-investing.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
5. Step name: Fetch Stocks. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index-fetch-stocks.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
6. Step name: 1A: Raw Merge & Structural Clean. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/retail-investor-anxiety-index-1a-raw-merge-and-structural-clean.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/retail-investor-anxiety-index/.
7. Step name: 1B: Linguistic & Relevance Filter. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/retail-investor-anxiety-index-1b-linguistic-and-relevance-filter.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/retail-investor-anxiety-index/.
8. Step name: Keyword Pre-Scorer. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-keyword-pre-scorer.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Claude 1: Anxiety Score. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-claude-1-anxiety-score.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Claude 2: Narrative Velocity. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-claude-2-narrative-velocity.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Claude 3: Herd Detection. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-claude-3-herd-detection.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Claude 4: Conviction vs Uncertainty. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-claude-4-conviction-vs-uncertainty.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Claude 5: Crowd Cycle Stage. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-claude-5-crowd-cycle-stage.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Anthropic Model 1. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-anthropic-model-1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Anthropic Model 2. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-anthropic-model-2.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Anthropic Model 3. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-anthropic-model-3.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Anthropic Model 4. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-anthropic-model-4.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
18. Step name: Anthropic Model 5. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-anthropic-model-5.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Insert to Supabase. Labor: AI with Human gate.
   Script called: `scripts/ingest/retail-investor-anxiety-index-insert-to-supabase.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/retail-investor-anxiety-index/.
20. Step name: Pipeline Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index-pipeline-response.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
21. Step name: Dashboard Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/retail-investor-anxiety-index-dashboard-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
22. Step name: Serve Dashboard HTML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index-serve-dashboard-html.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
23. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/retail-investor-anxiety-index-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

# Patent Filing Velocity Tracker

## Purpose

Patent Filing Velocity Tracker defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to patent filing velocity tracker. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Run Trigger | `webhook` | tool |
| Dashboard Webhook | `webhook` | tool |
| Fetch Patent Data | `code` | conductor |
| 1A: Structural Clean | `code` | gigo |
| 1B: Category Classifier + Velocity Pre-Scorer | `code` | tool |
| Aggregate for Claude | `code` | conductor |
| Claude 1: Velocity Score | `chainLlm` | tool |
| Claude 2: Concept Novelty | `chainLlm` | tool |
| Claude 3: Inventor Network | `chainLlm` | tool |
| Claude 4: Cross-Company Convergence | `chainLlm` | tool |
| Claude 5: Strategic Intent | `chainLlm` | tool |
| Anthropic Model 1 | `lmChatAnthropic` | tool |
| Anthropic Model 2 | `lmChatAnthropic` | tool |
| Anthropic Model 3 | `lmChatAnthropic` | tool |
| Anthropic Model 4 | `lmChatAnthropic` | tool |
| Anthropic Model 5 | `lmChatAnthropic` | tool |
| Merge Claude Outputs | `merge` | conductor |
| Signal Aggregator | `code` | conductor |
| Insert to Supabase | `httpRequest` | ingest |
| Check Trigger Type | `code` | conductor |
| If Webhook | `if` | conductor |
| Pipeline Response | `respondToWebhook` | report |
| Build Dashboard HTML | `code` | conductor |
| Serve Dashboard HTML | `respondToWebhook` | report |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (13 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (7 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/patent-filing-velocity-tracker.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run patent-filing-velocity-tracker --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/patent-filing-velocity-tracker data/verified/patent-filing-velocity-tracker -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/patent-filing-velocity-tracker.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Manual Run Trigger. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__manual-run-trigger.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Dashboard Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__dashboard-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: 1A: Structural Clean. Labor: AI with Human gate.
   Script called: `scripts/gigo/patent-filing-velocity-tracker__1a-structural-clean.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/patent-filing-velocity-tracker/.
5. Step name: 1B: Category Classifier + Velocity Pre-Scorer. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__1b-category-classifier-velocity-pre-scorer.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Claude 1: Velocity Score. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__claude-1-velocity-score.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Claude 2: Concept Novelty. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__claude-2-concept-novelty.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Claude 3: Inventor Network. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__claude-3-inventor-network.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Claude 4: Cross-Company Convergence. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__claude-4-cross-company-convergence.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Claude 5: Strategic Intent. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__claude-5-strategic-intent.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Anthropic Model 1. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Anthropic Model 2. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-2.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Anthropic Model 3. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-3.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Anthropic Model 4. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-4.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Anthropic Model 5. Labor: AI with Human gate.
   Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-5.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Insert to Supabase. Labor: AI with Human gate.
   Script called: `scripts/ingest/patent-filing-velocity-tracker__insert-to-supabase.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/patent-filing-velocity-tracker/.
17. Step name: Pipeline Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/patent-filing-velocity-tracker__pipeline-response.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
18. Step name: Serve Dashboard HTML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/patent-filing-velocity-tracker__serve-dashboard-html.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
19. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/patent-filing-velocity-tracker__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/patent-filing-velocity-tracker-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/patent-filing-velocity-tracker-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Patent Filing Velocity Tracker` run.
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
`snickerdoodle run patent-filing-velocity-tracker --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run patent-filing-velocity-tracker --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Manual Run Trigger | `snickerdoodle run patent-filing-velocity-tracker --step manual-run-trigger` | `--no-write` |
| Dashboard Webhook | `snickerdoodle run patent-filing-velocity-tracker --step dashboard-webhook` | `--no-write` |
| 1A: Structural Clean | `snickerdoodle run patent-filing-velocity-tracker --step 1a-structural-clean` |  |
| 1B: Category Classifier + Velocity Pre-Scorer | `snickerdoodle run patent-filing-velocity-tracker --step 1b-category-classifier-velocity-pre-scorer` | `--no-write` |
| Claude 1: Velocity Score | `snickerdoodle run patent-filing-velocity-tracker --step claude-1-velocity-score` | `--no-write` |
| Claude 2: Concept Novelty | `snickerdoodle run patent-filing-velocity-tracker --step claude-2-concept-novelty` | `--no-write` |
| Claude 3: Inventor Network | `snickerdoodle run patent-filing-velocity-tracker --step claude-3-inventor-network` | `--no-write` |
| Claude 4: Cross-Company Convergence | `snickerdoodle run patent-filing-velocity-tracker --step claude-4-cross-company-convergence` | `--no-write` |
| Claude 5: Strategic Intent | `snickerdoodle run patent-filing-velocity-tracker --step claude-5-strategic-intent` | `--no-write` |
| Anthropic Model 1 | `snickerdoodle run patent-filing-velocity-tracker --step anthropic-model-1` | `--no-write` |
| Anthropic Model 2 | `snickerdoodle run patent-filing-velocity-tracker --step anthropic-model-2` | `--no-write` |
| Anthropic Model 3 | `snickerdoodle run patent-filing-velocity-tracker --step anthropic-model-3` | `--no-write` |
| Anthropic Model 4 | `snickerdoodle run patent-filing-velocity-tracker --step anthropic-model-4` | `--no-write` |
| Anthropic Model 5 | `snickerdoodle run patent-filing-velocity-tracker --step anthropic-model-5` | `--no-write` |
| Insert to Supabase | `snickerdoodle run patent-filing-velocity-tracker --step insert-to-supabase` | `--sample` |
| Pipeline Response | `snickerdoodle run patent-filing-velocity-tracker --step pipeline-response` | `--no-write` |
| Serve Dashboard HTML | `snickerdoodle run patent-filing-velocity-tracker --step serve-dashboard-html` | `--no-write` |
| Produce human report | `snickerdoodle run patent-filing-velocity-tracker --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate patent-filing-velocity-tracker --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate patent-filing-velocity-tracker --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate patent-filing-velocity-tracker --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Manual Run Trigger | `scripts/tools/patent-filing-velocity-tracker__manual-run-trigger.py` | tool |
| Dashboard Webhook | `scripts/tools/patent-filing-velocity-tracker__dashboard-webhook.py` | tool |
| 1A: Structural Clean | `scripts/gigo/patent-filing-velocity-tracker__1a-structural-clean.py` | gigo |
| 1B: Category Classifier + Velocity Pre-Scorer | `scripts/tools/patent-filing-velocity-tracker__1b-category-classifier-velocity-pre-scorer.py` | tool |
| Claude 1: Velocity Score | `scripts/tools/patent-filing-velocity-tracker__claude-1-velocity-score.py` | tool |
| Claude 2: Concept Novelty | `scripts/tools/patent-filing-velocity-tracker__claude-2-concept-novelty.py` | tool |
| Claude 3: Inventor Network | `scripts/tools/patent-filing-velocity-tracker__claude-3-inventor-network.py` | tool |
| Claude 4: Cross-Company Convergence | `scripts/tools/patent-filing-velocity-tracker__claude-4-cross-company-convergence.py` | tool |
| Claude 5: Strategic Intent | `scripts/tools/patent-filing-velocity-tracker__claude-5-strategic-intent.py` | tool |
| Anthropic Model 1 | `scripts/tools/patent-filing-velocity-tracker__anthropic-model-1.py` | tool |
| Anthropic Model 2 | `scripts/tools/patent-filing-velocity-tracker__anthropic-model-2.py` | tool |
| Anthropic Model 3 | `scripts/tools/patent-filing-velocity-tracker__anthropic-model-3.py` | tool |
| Anthropic Model 4 | `scripts/tools/patent-filing-velocity-tracker__anthropic-model-4.py` | tool |
| Anthropic Model 5 | `scripts/tools/patent-filing-velocity-tracker__anthropic-model-5.py` | tool |
| Insert to Supabase | `scripts/ingest/patent-filing-velocity-tracker__insert-to-supabase.py` | ingest |
| Pipeline Response | `[TODO: DEV] Create or map script path: scripts/tools/patent-filing-velocity-tracker__pipeline-response.py` | tool |
| Serve Dashboard HTML | `[TODO: DEV] Create or map script path: scripts/tools/patent-filing-velocity-tracker__serve-dashboard-html.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/patent-filing-velocity-tracker__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/patent-filing-velocity-tracker/` | JSON |
| Verified data | `data/verified/patent-filing-velocity-tracker/` | JSON |
| Agent log | `logs/patent-filing-velocity-tracker-[DATE].json` | JSON |
| Human report | `reports/generated/patent-filing-velocity-tracker-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json`

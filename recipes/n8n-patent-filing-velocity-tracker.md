# Patent Filing Velocity Tracker

## Purpose

Patent Filing Velocity Tracker defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to patent filing velocity tracker. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch Patent Data | code | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Insert to Supabase | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Run Trigger | webhook | conductor |
| Dashboard Webhook | webhook | conductor |
| Fetch Patent Data | code | ingest |
| 1A: Structural Clean | code | gigo |
| 1B: Category Classifier + Velocity Pre-Scorer | code | conductor |
| Aggregate for Claude | code | gigo |
| Claude 1: Velocity Score | chainLlm | gigo |
| Claude 2: Concept Novelty | chainLlm | gigo |
| Claude 3: Inventor Network | chainLlm | gigo |
| Claude 4: Cross-Company Convergence | chainLlm | gigo |
| Claude 5: Strategic Intent | chainLlm | gigo |
| Anthropic Model 1 | lmChatAnthropic | gigo |
| Anthropic Model 2 | lmChatAnthropic | gigo |
| Anthropic Model 3 | lmChatAnthropic | gigo |
| Anthropic Model 4 | lmChatAnthropic | gigo |
| Anthropic Model 5 | lmChatAnthropic | gigo |
| Merge Claude Outputs | merge | conductor |
| Signal Aggregator | code | gigo |
| Insert to Supabase | httpRequest | ingest |
| Check Trigger Type | code | conductor |
| If Webhook | if | conductor |
| Pipeline Response | respondToWebhook | conductor |
| Build Dashboard HTML | code | gigo |
| Serve Dashboard HTML | respondToWebhook | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-patent-filing-velocity-tracker.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-patent-filing-velocity-tracker --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-patent-filing-velocity-tracker data/verified/n8n-patent-filing-velocity-tracker -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-patent-filing-velocity-tracker.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Fetch Patent Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-patent-filing-velocity-tracker__fetch-patent-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-patent-filing-velocity-tracker/.
3. Step name: 1A: Structural Clean. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__1a-structural-clean.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
4. Step name: Aggregate for Claude. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__aggregate-for-claude.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
5. Step name: Claude 1: Velocity Score. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-1-velocity-score.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
6. Step name: Claude 2: Concept Novelty. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-2-concept-novelty.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
7. Step name: Claude 3: Inventor Network. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-3-inventor-network.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
8. Step name: Claude 4: Cross-Company Convergence. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-4-cross-company-convergence.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
9. Step name: Claude 5: Strategic Intent. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-5-strategic-intent.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
10. Step name: Anthropic Model 1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
11. Step name: Anthropic Model 2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
12. Step name: Anthropic Model 3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
13. Step name: Anthropic Model 4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
14. Step name: Anthropic Model 5. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-5.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
15. Step name: Signal Aggregator. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__signal-aggregator.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
16. Step name: Insert to Supabase. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-patent-filing-velocity-tracker__insert-to-supabase.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-patent-filing-velocity-tracker/.
17. Step name: Build Dashboard HTML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__build-dashboard-html.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-patent-filing-velocity-tracker/.
18. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-patent-filing-velocity-tracker__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-patent-filing-velocity-tracker-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-patent-filing-velocity-tracker-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Patent Filing Velocity Tracker` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-patent-filing-velocity-tracker --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-patent-filing-velocity-tracker --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Fetch Patent Data | `snickerdoodle run n8n-patent-filing-velocity-tracker --step fetch-patent-data` | `--sample` |
| 1A: Structural Clean | `snickerdoodle run n8n-patent-filing-velocity-tracker --step 1a-structural-clean` |  |
| Aggregate for Claude | `snickerdoodle run n8n-patent-filing-velocity-tracker --step aggregate-for-claude` |  |
| Claude 1: Velocity Score | `snickerdoodle run n8n-patent-filing-velocity-tracker --step claude-1-velocity-score` |  |
| Claude 2: Concept Novelty | `snickerdoodle run n8n-patent-filing-velocity-tracker --step claude-2-concept-novelty` |  |
| Claude 3: Inventor Network | `snickerdoodle run n8n-patent-filing-velocity-tracker --step claude-3-inventor-network` |  |
| Claude 4: Cross-Company Convergence | `snickerdoodle run n8n-patent-filing-velocity-tracker --step claude-4-cross-company-convergence` |  |
| Claude 5: Strategic Intent | `snickerdoodle run n8n-patent-filing-velocity-tracker --step claude-5-strategic-intent` |  |
| Anthropic Model 1 | `snickerdoodle run n8n-patent-filing-velocity-tracker --step anthropic-model-1` |  |
| Anthropic Model 2 | `snickerdoodle run n8n-patent-filing-velocity-tracker --step anthropic-model-2` |  |
| Anthropic Model 3 | `snickerdoodle run n8n-patent-filing-velocity-tracker --step anthropic-model-3` |  |
| Anthropic Model 4 | `snickerdoodle run n8n-patent-filing-velocity-tracker --step anthropic-model-4` |  |
| Anthropic Model 5 | `snickerdoodle run n8n-patent-filing-velocity-tracker --step anthropic-model-5` |  |
| Signal Aggregator | `snickerdoodle run n8n-patent-filing-velocity-tracker --step signal-aggregator` |  |
| Insert to Supabase | `snickerdoodle run n8n-patent-filing-velocity-tracker --step insert-to-supabase` | `--sample` |
| Build Dashboard HTML | `snickerdoodle run n8n-patent-filing-velocity-tracker --step build-dashboard-html` |  |
| Produce human report | `snickerdoodle run n8n-patent-filing-velocity-tracker --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-patent-filing-velocity-tracker --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-patent-filing-velocity-tracker --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-patent-filing-velocity-tracker --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Fetch Patent Data | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-patent-filing-velocity-tracker__fetch-patent-data.py` | ingest |
| 1A: Structural Clean | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__1a-structural-clean.py` | gigo |
| Aggregate for Claude | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__aggregate-for-claude.py` | gigo |
| Claude 1: Velocity Score | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-1-velocity-score.py` | gigo |
| Claude 2: Concept Novelty | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-2-concept-novelty.py` | gigo |
| Claude 3: Inventor Network | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-3-inventor-network.py` | gigo |
| Claude 4: Cross-Company Convergence | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-4-cross-company-convergence.py` | gigo |
| Claude 5: Strategic Intent | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__claude-5-strategic-intent.py` | gigo |
| Anthropic Model 1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-1.py` | gigo |
| Anthropic Model 2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-2.py` | gigo |
| Anthropic Model 3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-3.py` | gigo |
| Anthropic Model 4 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-4.py` | gigo |
| Anthropic Model 5 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__anthropic-model-5.py` | gigo |
| Signal Aggregator | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__signal-aggregator.py` | gigo |
| Insert to Supabase | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-patent-filing-velocity-tracker__insert-to-supabase.py` | ingest |
| Build Dashboard HTML | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-patent-filing-velocity-tracker__build-dashboard-html.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-patent-filing-velocity-tracker__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-patent-filing-velocity-tracker/` | JSON |
| Verified data | `data/verified/n8n-patent-filing-velocity-tracker/` | JSON |
| Agent log | `logs/n8n-patent-filing-velocity-tracker-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-patent-filing-velocity-tracker-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json`

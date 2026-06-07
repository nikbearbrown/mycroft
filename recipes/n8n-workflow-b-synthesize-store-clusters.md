# Workflow B — Synthesize & Store Clusters

## Purpose

Workflow B — Synthesize & Store Clusters defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to workflow b — synthesize & store clusters. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch Unprocessed Items | postgres | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Workflow Trigger | executeWorkflowTrigger | conductor |
| Fetch Unprocessed Items | postgres | ingest |
| Group By Topic Tag | code | gigo |
| Claude — Synthesize Cluster | lmChatAnthropic | gigo |
| Parse Claude Response | code | gigo |
| Store — Insert Cluster | postgres | gigo |
| Build Cluster Source Links | code | gigo |
| Store — Insert Source Links | postgres | gigo |
| Mark Raw Items Processed | postgres | gigo |
| Fetch Clusters for Webhook | postgres | conductor |
| Format Webhook Output | code | conductor |
| Webhook — Receive Request | webhook | conductor |
| Webhook — Send Response | respondToWebhook | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-workflow-b-synthesize-store-clusters.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-workflow-b-synthesize-store-clusters data/verified/n8n-workflow-b-synthesize-store-clusters -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-workflow-b-synthesize-store-clusters.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Fetch Unprocessed Items. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-b-synthesize-store-clusters__fetch-unprocessed-items.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-workflow-b-synthesize-store-clusters/.
3. Step name: Group By Topic Tag. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__group-by-topic-tag.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-b-synthesize-store-clusters/.
4. Step name: Claude — Synthesize Cluster. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__claude-synthesize-cluster.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-b-synthesize-store-clusters/.
5. Step name: Parse Claude Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__parse-claude-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-b-synthesize-store-clusters/.
6. Step name: Store — Insert Cluster. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__store-insert-cluster.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-b-synthesize-store-clusters/.
7. Step name: Build Cluster Source Links. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__build-cluster-source-links.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-b-synthesize-store-clusters/.
8. Step name: Store — Insert Source Links. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__store-insert-source-links.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-b-synthesize-store-clusters/.
9. Step name: Mark Raw Items Processed. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__mark-raw-items-processed.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-workflow-b-synthesize-store-clusters/.
10. Step name: Webhook — Send Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-workflow-b-synthesize-store-clusters__webhook-send-response.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-workflow-b-synthesize-store-clusters__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-workflow-b-synthesize-store-clusters-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-workflow-b-synthesize-store-clusters-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Workflow B — Synthesize & Store Clusters` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-workflow-b-synthesize-store-clusters --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-workflow-b-synthesize-store-clusters --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Fetch Unprocessed Items | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step fetch-unprocessed-items` | `--sample` |
| Group By Topic Tag | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step group-by-topic-tag` |  |
| Claude — Synthesize Cluster | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step claude-synthesize-cluster` |  |
| Parse Claude Response | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step parse-claude-response` |  |
| Store — Insert Cluster | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step store-insert-cluster` |  |
| Build Cluster Source Links | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step build-cluster-source-links` |  |
| Store — Insert Source Links | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step store-insert-source-links` |  |
| Mark Raw Items Processed | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step mark-raw-items-processed` |  |
| Webhook — Send Response | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step webhook-send-response` | `--no-write` |
| Produce human report | `snickerdoodle run n8n-workflow-b-synthesize-store-clusters --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-workflow-b-synthesize-store-clusters --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-workflow-b-synthesize-store-clusters --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-workflow-b-synthesize-store-clusters --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Fetch Unprocessed Items | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-workflow-b-synthesize-store-clusters__fetch-unprocessed-items.py` | ingest |
| Group By Topic Tag | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__group-by-topic-tag.py` | gigo |
| Claude — Synthesize Cluster | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__claude-synthesize-cluster.py` | gigo |
| Parse Claude Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__parse-claude-response.py` | gigo |
| Store — Insert Cluster | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__store-insert-cluster.py` | gigo |
| Build Cluster Source Links | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__build-cluster-source-links.py` | gigo |
| Store — Insert Source Links | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__store-insert-source-links.py` | gigo |
| Mark Raw Items Processed | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-workflow-b-synthesize-store-clusters__mark-raw-items-processed.py` | gigo |
| Webhook — Send Response | `[TODO: DEV] Create or map script path: scripts/tools/n8n-workflow-b-synthesize-store-clusters__webhook-send-response.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-workflow-b-synthesize-store-clusters__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-workflow-b-synthesize-store-clusters/` | JSON |
| Verified data | `data/verified/n8n-workflow-b-synthesize-store-clusters/` | JSON |
| Agent log | `logs/n8n-workflow-b-synthesize-store-clusters-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-workflow-b-synthesize-store-clusters-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json`

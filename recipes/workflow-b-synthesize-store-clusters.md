# Workflow B — Synthesize & Store Clusters

## Purpose

Workflow B turns unprocessed raw AI-market intelligence into topic clusters that downstream AEO FAQ generation can use, while preserving source links and requiring review before database state changes or webhook publication.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Unprocessed raw intelligence | JSON/table export | `data/verified/aeo-workflow-a/` or approved `raw_intelligence` export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Topic tag | String | Raw intelligence rows | Confirm source is allowed, current, and rate-safe before live fetch. |
| Raw item IDs | Integer/string list | Raw intelligence rows | Confirm source is allowed, current, and rate-safe before live fetch. |
| Pending cluster request | Webhook/manual payload | Local conductor or caller workflow | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json` | Yes |
| Unprocessed raw intelligence | JSON/table export | `data/verified/aeo-workflow-a/` or approved `raw_intelligence` export | Yes |
| Topic tag | String | Raw intelligence rows | Yes |
| Raw item IDs | Integer/string list | Raw intelligence rows | Yes |
| Anthropic credential | Environment variable | `ANTHROPIC_API_KEY` for future live adapter | No |
| Pending cluster request | Webhook/manual payload | Local conductor or caller workflow | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/workflow-b-synthesize-store-clusters.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run workflow-b-synthesize-store-clusters --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/workflow-b-synthesize-store-clusters data/verified/workflow-b-synthesize-store-clusters -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/workflow-b-synthesize-store-clusters.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: fetch_unprocessed_items. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_unprocessed_items.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-b-synthesize-store-clusters/.
3. Step name: group_by_topic_tag. Labor: AI with Human gate.
   Script called: `scripts/gigo/group_by_topic_tag.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-b-synthesize-store-clusters/.
4. Step name: synthesize_cluster. Labor: AI with Human gate.
   Script called: `scripts/tools/synthesize_cluster.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: parse_cluster_response. Labor: AI with Human gate.
   Script called: `scripts/gigo/parse_cluster_response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-b-synthesize-store-clusters/.
6. Step name: store_insert_cluster. Labor: AI with Human gate.
   Script called: `scripts/gigo/store_insert_cluster.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-b-synthesize-store-clusters/.
7. Step name: build_cluster_source_links. Labor: AI with Human gate.
   Script called: `scripts/gigo/build_cluster_source_links.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-b-synthesize-store-clusters/.
8. Step name: mark_raw_items_processed. Labor: AI with Human gate.
   Script called: `scripts/gigo/mark_raw_items_processed.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-b-synthesize-store-clusters/.
9. Step name: format_cluster_webhook_output. Labor: AI with Human gate.
   Script called: `scripts/tools/format_cluster_webhook_output.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/workflow-b-synthesize-store-clusters__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/workflow-b-synthesize-store-clusters-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/workflow-b-synthesize-store-clusters-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Workflow B — Synthesize & Store Clusters` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if no unprocessed rows are available.
- Stop if any group lacks source URLs or raw IDs.
- Stop if a cluster summary is empty or confidence score is outside 1-10.
- Stop before live Anthropic calls without `ANTHROPIC_API_KEY` and explicit human approval.
- Stop before database inserts or processed-state updates without an approved database destination.
- Stop before sending webhook responses containing unreviewed or malformed cluster records.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run workflow-b-synthesize-store-clusters --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run workflow-b-synthesize-store-clusters --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| fetch_unprocessed_items | `snickerdoodle run workflow-b-synthesize-store-clusters --step fetch-unprocessed-items` | `--sample` |
| group_by_topic_tag | `snickerdoodle run workflow-b-synthesize-store-clusters --step group-by-topic-tag` |  |
| synthesize_cluster | `snickerdoodle run workflow-b-synthesize-store-clusters --step synthesize-cluster` | `--no-write` |
| parse_cluster_response | `snickerdoodle run workflow-b-synthesize-store-clusters --step parse-cluster-response` |  |
| store_insert_cluster | `snickerdoodle run workflow-b-synthesize-store-clusters --step store-insert-cluster` |  |
| build_cluster_source_links | `snickerdoodle run workflow-b-synthesize-store-clusters --step build-cluster-source-links` |  |
| mark_raw_items_processed | `snickerdoodle run workflow-b-synthesize-store-clusters --step mark-raw-items-processed` |  |
| format_cluster_webhook_output | `snickerdoodle run workflow-b-synthesize-store-clusters --step format-cluster-webhook-output` | `--no-write` |
| Produce human report | `snickerdoodle run workflow-b-synthesize-store-clusters --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate workflow-b-synthesize-store-clusters --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate workflow-b-synthesize-store-clusters --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate workflow-b-synthesize-store-clusters --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| fetch_unprocessed_items | `scripts/ingest/fetch_unprocessed_items.py` | ingest |
| group_by_topic_tag | `scripts/gigo/group_by_topic_tag.py` | gigo |
| synthesize_cluster | `scripts/tools/synthesize_cluster.py` | tool |
| parse_cluster_response | `scripts/gigo/parse_cluster_response.py` | gigo |
| store_insert_cluster | `scripts/gigo/store_insert_cluster.py` | gigo |
| build_cluster_source_links | `scripts/gigo/build_cluster_source_links.py` | gigo |
| mark_raw_items_processed | `scripts/gigo/mark_raw_items_processed.py` | gigo |
| format_cluster_webhook_output | `scripts/tools/format_cluster_webhook_output.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/workflow-b-synthesize-store-clusters__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/workflow-b-synthesize-store-clusters/` | JSON |
| Verified data | `data/verified/workflow-b-synthesize-store-clusters/` | JSON |
| Agent log | `logs/workflow-b-synthesize-store-clusters-[DATE].json` | JSON |
| Human report | `reports/generated/workflow-b-synthesize-store-clusters-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json`

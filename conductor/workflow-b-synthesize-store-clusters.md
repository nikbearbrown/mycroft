# Workflow B — Synthesize & Store Clusters — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is in `conductor/verified/`.

## Entry Point

The flow is triggered by Workflow A when new raw intelligence exists, or by a webhook/manual request to return recently prepared pending clusters.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- Depends on: none
- AI task: Create a run ID, identify trigger source, and record original n8n JSON path.
- Handoff condition: Run ID and trigger mode are present.
- On failure: Stop and ask the human to identify the trigger.

### Step 2 — Load Unprocessed Rows

- Labor: AI
- Depends on: Step 1
- AI task: Run `scripts/ingest/fetch_unprocessed_items.py` against local verified rows or approved database export.
- Handoff condition: Rows are present or the run is logged as no-op.
- On failure: Stop and report missing input data.

### Step 3 — Group by Topic

- Labor: AI
- Depends on: Step 2
- AI task: Run `scripts/gigo/group_by_topic_tag.py`.
- Handoff condition: Every group has `topic_tag`, `item_count`, `raw_ids`, `source_urls`, and `combined_text`.
- On failure: Stop and preserve ungrouped rows.

### Step 4 — Synthesize Cluster

- Labor: AI
- Depends on: Step 3
- AI task: Run `scripts/tools/synthesize_cluster.py` for each group; use local synthesis unless live Anthropic is explicitly approved.
- Handoff condition: Each cluster has title, summary, source URLs, item count, and confidence score.
- On failure: Stop and report the failed group.

### Step 5 — Validate Cluster

- Labor: AI
- Depends on: Step 4
- AI task: Run `scripts/gigo/parse_cluster_response.py`.
- Handoff condition: Confidence score is numeric and cluster summary is non-empty.
- On failure: Stop and preserve raw synthesis output.

### Step 6 — Prepare Database Payloads

- Labor: AI
- Depends on: Step 5
- AI task: Run `scripts/gigo/store_insert_cluster.py`, `scripts/gigo/build_cluster_source_links.py`, `scripts/gigo/store_insert_source_links.py`, and `scripts/gigo/mark_raw_items_processed.py`.
- Handoff condition: Insert/link/update payloads are present and no live database write has occurred.
- On failure: Stop and report malformed database payloads.

### Step 7 — Human Storage Decision

- Labor: Human
- Depends on: Step 6
- Human task: Use [PA], [IJ], and [EI] to approve, reject, or revise prepared clusters and database updates.
- Handoff condition: Human records approve/reject/rerun.
- On failure: Do not mark raw items processed.

### Step 8 — Format Webhook Output

- Labor: AI
- Depends on: Step 7
- AI task: Run `scripts/tools/format_cluster_webhook_output.py` for approved pending clusters.
- Handoff condition: Response payload includes count, clusters, and generated timestamp.
- On failure: Do not send webhook response.

## Phase Gates

Hard gates: Step 2 input gate, Step 5 validation gate, Step 7 human storage decision, Step 8 webhook gate.

## Silent Mode Requirements

- Minimum three successful dialogic runs with accepted clusters.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for synthesis thresholds and database update behavior.
- Live Anthropic and database adapters must preserve raw prompts, responses, and operation payloads.

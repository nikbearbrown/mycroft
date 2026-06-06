# Workflow B — Synthesize & Store Clusters

## Purpose

Workflow B turns unprocessed raw AI-market intelligence into topic clusters that downstream AEO FAQ generation can use, while preserving source links and requiring review before database state changes or webhook publication.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Unprocessed raw intelligence | JSON/table export | `data/verified/aeo-workflow-a/` or approved `raw_intelligence` export | Yes |
| Topic tag | String | Raw intelligence rows | Yes |
| Raw item IDs | Integer/string list | Raw intelligence rows | Yes |
| Anthropic credential | Environment variable | `ANTHROPIC_API_KEY` for future live adapter | No for local dialogic mode |
| Pending cluster request | Webhook/manual payload | Local conductor or caller workflow | No |

## Phase Gates

1. Input gate: rows must include `id`, `title`, `url`, `raw_content`, `topic_tag`, and `processed`. Verification: run `python3 scripts/ingest/fetch_unprocessed_items.py` on a sample/export. Human capacity: [PA].
2. Grouping gate: every group must have a topic tag, item count, raw IDs, source URLs, and combined text. Verification: run `python3 scripts/gigo/group_by_topic_tag.py`. Human capacity: [PA], [PF].
3. Synthesis gate: cluster output must include title, summary, confidence score, source URLs, and item count. Verification: run `python3 scripts/tools/synthesize_cluster.py` and `python3 scripts/gigo/parse_cluster_response.py`. Human capacity: [IJ], [PA].
4. Storage gate: database insert/update payloads must be prepared but not executed until approved. Verification: run `python3 scripts/gigo/store_insert_cluster.py`, `scripts/gigo/build_cluster_source_links.py`, `scripts/gigo/store_insert_source_links.py`, and `scripts/gigo/mark_raw_items_processed.py`. Human capacity: [TO], [EI].
5. Webhook gate: response payload must expose only pending cluster fields intended for downstream use. Verification: run `python3 scripts/tools/format_cluster_webhook_output.py`. Human capacity: [EI].

## Steps

1. Receive Workflow A handoff or webhook request. Labor: AI. Script called: none; conductor trigger. Input: handoff payload. Output: run ID and mode. Where output goes: `logs/`.
2. Fetch unprocessed items. Labor: AI. Script called: `scripts/ingest/fetch_unprocessed_items.py`. Input: verified local rows or database export. Output: unprocessed raw intelligence rows. Where output goes: `data/raw/` or `data/verified/`.
3. Group rows by topic tag. Labor: AI. Script called: `scripts/gigo/group_by_topic_tag.py`. Input: unprocessed rows. Output: topic-group records. Where output goes: `data/verified/`.
4. Synthesize clusters. Labor: AI. Script called: `scripts/tools/synthesize_cluster.py`. Input: topic-group records. Output: cluster JSON. Where output goes: `logs/`.
5. Parse cluster output. Labor: AI. Script called: `scripts/gigo/parse_cluster_response.py`. Input: local/model cluster output. Output: validated cluster records. Where output goes: `data/verified/`.
6. Prepare cluster insert. Labor: AI. Script called: `scripts/gigo/store_insert_cluster.py`. Input: validated cluster records. Output: `topic_clusters` insert payloads. Where output goes: `data/verified/`.
7. Build and prepare source links. Labor: AI. Script called: `scripts/gigo/build_cluster_source_links.py` and `scripts/gigo/store_insert_source_links.py`. Input: cluster IDs and raw IDs. Output: `cluster_sources` insert payloads. Where output goes: `data/verified/`.
8. Prepare processed-state updates. Labor: AI. Script called: `scripts/gigo/mark_raw_items_processed.py`. Input: raw IDs. Output: `raw_intelligence` update payload. Where output goes: `data/verified/`.
9. Format pending clusters. Labor: AI. Script called: `scripts/tools/format_cluster_webhook_output.py`. Input: pending cluster records. Output: webhook/report payload. Where output goes: `reports/generated/` or `logs/`.
10. Human review and continuation. Labor: Human. Human action required: approve database writes, reject weak clusters, or rerun synthesis with revised grouping. Output: recorded decision. Where output goes: `logs/`.

## Output Contract

### Agent output

Agent output goes to `logs/aeo-workflow-b/<run-id>.json`. It must include input row count, group count, clusters prepared, confidence scores, source URLs, prepared database operations, skipped groups, scripts used, validation results, and whether any live model or database action was requested.

### Human report

The human report goes to `reports/generated/workflow-b-synthesize-store-clusters-<date>.md`. It surfaces the strongest new clusters, weak or sparse clusters, source coverage, and whether the cluster set is ready for downstream FAQ generation.

## Stop Conditions

- Stop if no unprocessed rows are available.
- Stop if any group lacks source URLs or raw IDs.
- Stop if a cluster summary is empty or confidence score is outside 1-10.
- Stop before live Anthropic calls without `ANTHROPIC_API_KEY` and explicit human approval.
- Stop before database inserts or processed-state updates without an approved database destination.
- Stop before sending webhook responses containing unreviewed or malformed cluster records.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json`

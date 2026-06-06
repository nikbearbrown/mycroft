# Recipe: Workflow B — Synthesize & Store Clusters

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json`
- Imported from pantry path: `n8n_Workflows/AEO_FAQ_Pipeline_Phase2/synthesize&store.json`
- Node count: 13

## Required Reads

1. Check `data/mycroft-main/` for verified local or database data that satisfies the request.
2. Check `scripts/mycroft-main/` for vetted scripts that already perform the needed extraction, transformation, or validation.
3. Read this workflow's original JSON before changing behavior.
4. Only use live web/API lookup when verified local data does not exist or is explicitly stale.

## Phase Gates

1. Data gate: identify the trusted data source, freshness, provenance, and missing fields.
2. Script gate: prefer an existing vetted script; if a new script is needed, write a narrow test before using it in a pipeline.
3. Dry-run gate: execute the smallest non-destructive sample and save logs or outputs.
4. Validation gate: compare outputs against expected schema, row counts, citations, or workflow invariants.
5. Automation gate: only run a full automated pipeline after the previous gates pass.

## Trigger Surface

Workflow Trigger, Webhook — Receive Request, Webhook — Send Response

## Agent/AI Nodes

Claude — Synthesize Cluster

## External Writes or Side Effects

Fetch Unprocessed Items, Store — Insert Cluster, Store — Insert Source Links, Mark Raw Items Processed, Fetch Clusters for Webhook, Format Webhook Output, Webhook — Receive Request, Webhook — Send Response

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 4 |
| executeWorkflowTrigger | 1 |
| lmChatAnthropic | 1 |
| postgres | 5 |
| respondToWebhook | 1 |
| webhook | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Workflow Trigger | executeWorkflowTrigger |
| 2 | Fetch Unprocessed Items | postgres |
| 3 | Group By Topic Tag | code |
| 4 | Claude — Synthesize Cluster | lmChatAnthropic |
| 5 | Parse Claude Response | code |
| 6 | Store — Insert Cluster | postgres |
| 7 | Build Cluster Source Links | code |
| 8 | Store — Insert Source Links | postgres |
| 9 | Mark Raw Items Processed | postgres |
| 10 | Fetch Clusters for Webhook | postgres |
| 11 | Format Webhook Output | code |
| 12 | Webhook — Receive Request | webhook |
| 13 | Webhook — Send Response | respondToWebhook |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

# Recipe: Product Recommendation Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Product_Recommendation_Agent/Product_Recommendation_Agent.json`
- Imported from pantry path: `n8n_Workflows/Product_Recommendation_Agent/Product_Recommendation_Agent.json`
- Node count: 9

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

When clicking ‘Execute workflow’

## Agent/AI Nodes

Message a model

## External Writes or Side Effects

Execute a SQL query, Execute a SQL query1, Execute a SQL query2, Send email

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 2 |
| emailSend | 1 |
| googleGemini | 1 |
| manualTrigger | 1 |
| postgres | 3 |
| set | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Execute a SQL query | postgres |
| 2 | When clicking ‘Execute workflow’ | manualTrigger |
| 3 | Execute a SQL query1 | postgres |
| 4 | Execute a SQL query2 | postgres |
| 5 | Collect User Requirements | set |
| 6 | Code | code |
| 7 | Message a model | googleGemini |
| 8 | Code1 | code |
| 9 | Send email | emailSend |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

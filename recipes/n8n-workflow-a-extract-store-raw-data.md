# Recipe: Workflow A — Extract & Store Raw Data

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json`
- Imported from pantry path: `n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json`
- Node count: 20

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

Schedule Trigger

## Agent/AI Nodes

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

Fetch TechCrunch, Fetch VentureBeat, Fetch HackerNews, Fetch ArXiv, Fetch Reddit, Store TechCrunch, Store VentureBeat, Store HackerNews, Store ArXiv, Store Reddit, Verify — Count Stored Items

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 6 |
| executeWorkflow | 1 |
| httpRequest | 5 |
| if | 1 |
| postgres | 6 |
| scheduleTrigger | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Schedule Trigger | scheduleTrigger |
| 2 | Fetch TechCrunch | httpRequest |
| 3 | Fetch VentureBeat | httpRequest |
| 4 | Fetch HackerNews | httpRequest |
| 5 | Fetch ArXiv | httpRequest |
| 6 | Fetch Reddit | httpRequest |
| 7 | Parse TechCrunch | code |
| 8 | Parse VentureBeat | code |
| 9 | Parse HackerNews | code |
| 10 | Parse ArXiv | code |
| 11 | Parse Reddit | code |
| 12 | Store TechCrunch | postgres |
| 13 | Store VentureBeat | postgres |
| 14 | Store HackerNews | postgres |
| 15 | Store ArXiv | postgres |
| 16 | Store Reddit | postgres |
| 17 | Verify — Count Stored Items | postgres |
| 18 | Check — New Items Exist? | if |
| 19 | Trigger — Start Workflow B | executeWorkflow |
| 20 | Log — Skip | code |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

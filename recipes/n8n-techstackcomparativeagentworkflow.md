# Recipe: TechStackComparativeAgentWorkflow

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json`
- Imported from pantry path: `n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json`
- Node count: 18

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

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

GitHub: Get Repos, GitHub: Get Languages, arXiv: Search Papers

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 2 |
| convertToFile | 1 |
| httpRequest | 3 |
| if | 1 |
| manualTrigger | 1 |
| set | 8 |
| splitInBatches | 1 |
| splitOut | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Validate Input | if |
| 2 | Prepare Variables | set |
| 3 | GitHub: Get Repos | httpRequest |
| 4 | Batch Repos (Top 5) | splitInBatches |
| 5 | GitHub: Get Languages | httpRequest |
| 6 | Aggregate Repo Data | set |
| 7 | arXiv: Search Papers | httpRequest |
| 8 | Error: Invalid Input | set |
| 9 | Parse arXiv XML | code |
| 10 | When clicking ‘Execute workflow’ | manualTrigger |
| 11 | Split Out | splitOut |
| 12 | set | set |
| 13 | set1 | set |
| 14 | Convert to File | convertToFile |
| 15 | Edit Fields | set |
| 16 | Edit Fields1 | set |
| 17 | Code | code |
| 18 | Edit Fields2 | set |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

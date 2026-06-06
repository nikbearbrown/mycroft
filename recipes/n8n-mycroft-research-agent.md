# Recipe: Mycroft Research Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/Mycroft_Research_Agent.json`
- Imported from pantry path: `n8n_Workflows/Research_Analytics_Agent/Mycroft_Research_Agent.json`
- Node count: 12

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

Get Financial Overview1, Get Income Statement1, Google Search Patent

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 6 |
| httpRequest | 3 |
| manualTrigger | 1 |
| merge | 1 |
| set | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | When clicking ‘Execute workflow’ | manualTrigger |
| 2 | Code in Python (Beta) | code |
| 3 | Company Input | set |
| 4 | Get Financial Overview1 | httpRequest |
| 5 | Get Income Statement1 | httpRequest |
| 6 | Process Company Data1 | code |
| 7 | Google Search Patent | httpRequest |
| 8 | Process Patent Data1 | code |
| 9 | Process Financial Data1 | code |
| 10 | Generate Analysis1 | code |
| 11 | Generate Final Report1 | code |
| 12 | Merge | merge |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

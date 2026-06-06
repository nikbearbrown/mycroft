# Recipe: MycroftResearchAgent_2.0

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json`
- Imported from pantry path: `n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json`
- Node count: 16

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

Get Financial Overview1, Get Income Statement1, Google Search Patent, Get Earnings Data

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 9 |
| httpRequest | 4 |
| manualTrigger | 1 |
| merge | 1 |
| set | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | When clicking ‘Execute workflow’ | manualTrigger |
| 2 | Company Input | set |
| 3 | Get Financial Overview1 | httpRequest |
| 4 | Get Income Statement1 | httpRequest |
| 5 | Process Company Data1 | code |
| 6 | Google Search Patent | httpRequest |
| 7 | Process Patent Data1 | code |
| 8 | Process Financial Data1 | code |
| 9 | Generate Analysis1 | code |
| 10 | Generate Final Report1 | code |
| 11 | Merge | merge |
| 12 | Get Earnings Data | httpRequest |
| 13 | Process Earnings Data | code |
| 14 | Get Competitive Analysis | code |
| 15 | Merge Competitive Analysis | code |
| 16 | Investment Report | code |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

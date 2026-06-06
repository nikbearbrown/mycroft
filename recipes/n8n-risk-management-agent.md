# Recipe: Risk Management Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Risk_Management_Agent/Json_code.json`
- Imported from pantry path: `n8n_Workflows/Risk_Management_Agent/Json_code.json`
- Node count: 8

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

Manual Trigger

## Agent/AI Nodes

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

Get Portfolio from Sheets, Fetch Live Prices, Call Groq API, Log to Sheets

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 3 |
| googleSheets | 2 |
| httpRequest | 2 |
| manualTrigger | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Manual Trigger | manualTrigger |
| 2 | Get Portfolio from Sheets | googleSheets |
| 3 | Fetch Live Prices | httpRequest |
| 4 | Calculate Advanced Risk | code |
| 5 | Prepare for LLM | code |
| 6 | Call Groq API | httpRequest |
| 7 | Format Report | code |
| 8 | Log to Sheets | googleSheets |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

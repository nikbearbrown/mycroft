# Recipe: Funding Intelligence Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json`
- Imported from pantry path: `n8n_Workflows/Funding_Intelligence_Agent/Funding Intelligence Agent .json`
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

Schedule Trigger

## Agent/AI Nodes

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

Zyte_TechCrunch_Scraper, Zyte_VentureBeat, Execute a SQL query, Insert rows in a table, Send email, Append row in sheet

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 6 |
| emailSend | 1 |
| googleSheets | 1 |
| html | 2 |
| httpRequest | 2 |
| merge | 1 |
| postgres | 2 |
| scheduleTrigger | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Schedule Trigger | scheduleTrigger |
| 2 | Zyte_TechCrunch_Scraper | httpRequest |
| 3 | HTML | html |
| 4 | Zyte_VentureBeat | httpRequest |
| 5 | Decode_VB | code |
| 6 | Decode_TC | code |
| 7 | HTML1 | html |
| 8 | Merge | merge |
| 9 | Filter and split VB | code |
| 10 | Filter and split tech_crunch | code |
| 11 | Filter_Funding_Keywords | code |
| 12 | Classify_Industry | code |
| 13 | Execute a SQL query | postgres |
| 14 | Insert rows in a table | postgres |
| 15 | Send email | emailSend |
| 16 | Append row in sheet | googleSheets |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

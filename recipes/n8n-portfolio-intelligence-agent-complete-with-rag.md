# Recipe: Portfolio Intelligence Agent - Complete with RAG

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json`
- Imported from pantry path: `n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json`
- Node count: 23

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

Manual Trigger, Schedule Trigger

## Agent/AI Nodes

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

Read Knowledge Base1, Read Portfolio History CSV, Generate AI Summary (Groq), Send a message, Append Portfolio History1, Append Daily Summary

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 10 |
| convertToFile | 2 |
| gmail | 1 |
| httpRequest | 1 |
| manualTrigger | 1 |
| readBinaryFile | 2 |
| readWriteFile | 4 |
| scheduleTrigger | 1 |
| splitOut | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Manual Trigger | manualTrigger |
| 2 | Schedule Trigger | scheduleTrigger |
| 3 | Read Holdings File | readBinaryFile |
| 4 | Parse JSON Holdings | code |
| 5 | Calculate Portfolio Metrics | code |
| 6 | Read Previous Summaries | readBinaryFile |
| 7 | Fetch & Extract Stock Prices | code |
| 8 | Parse Summaries CSV | code |
| 9 | Calculate Daily Return | code |
| 10 | Read Knowledge Base1 | readWriteFile |
| 11 | Parse Knowledge Base CSV | code |
| 12 | Read Portfolio History CSV | readWriteFile |
| 13 | Parse Portfolio History Data | code |
| 14 | Build Portfolio Analysis | code |
| 15 | RAG-Retrieve Context | code |
| 16 | Extract AI Summary | code |
| 17 | Split Out | splitOut |
| 18 | Generate AI Summary (Groq) | httpRequest |
| 19 | Send a message | gmail |
| 20 | Append Portfolio History1 | readWriteFile |
| 21 | Convert Holdings to CSV | convertToFile |
| 22 | Convert Summary to CSV | convertToFile |
| 23 | Append Daily Summary | readWriteFile |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

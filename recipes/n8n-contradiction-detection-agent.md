# Recipe: Contradiction_detection_agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json`
- Imported from pantry path: `n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json`
- Node count: 26

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

DB: Fetch Earnings Guidance Signals, DB: Fetch Risk Admissions, DB: Fetch QA Pressure Map, DB: Fetch News Signals, DB: Fetch Tech Stack Signals, Groq: Analyse Contradictions, DB: Insert Contradiction Report, DB: Insert Contradiction Flag, Execute a SQL query, Execute a SQL query1, Execute a SQL query2, Execute a SQL query3, HTTP Request, DB: Save News Signals

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 8 |
| httpRequest | 2 |
| if | 1 |
| manualTrigger | 1 |
| merge | 1 |
| postgres | 12 |
| set | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Manual Trigger | manualTrigger |
| 2 | Set Company Input | set |
| 3 | DB: Fetch Earnings Guidance Signals | postgres |
| 4 | DB: Fetch Risk Admissions | postgres |
| 5 | DB: Fetch QA Pressure Map | postgres |
| 6 | DB: Fetch News Signals | postgres |
| 7 | DB: Fetch Tech Stack Signals | postgres |
| 8 | Aggregate All Signals | code |
| 9 | Run Pattern Detection Engine | code |
| 10 | Build Groq Prompt | code |
| 11 | LLM Needed? | if |
| 12 | Groq: Analyse Contradictions | httpRequest |
| 13 | Process Groq Response | code |
| 14 | No-Flag Passthrough | code |
| 15 | DB: Insert Contradiction Report | postgres |
| 16 | Fan Out Flags | code |
| 17 | DB: Insert Contradiction Flag | postgres |
| 18 | Build Final Report | code |
| 19 | Execute a SQL query | postgres |
| 20 | Execute a SQL query1 | postgres |
| 21 | Execute a SQL query2 | postgres |
| 22 | Execute a SQL query3 | postgres |
| 23 | HTTP Request | httpRequest |
| 24 | Process News Response | code |
| 25 | DB: Save News Signals | postgres |
| 26 | Merge | merge |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

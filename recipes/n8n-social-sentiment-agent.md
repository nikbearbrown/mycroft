# Recipe: Social Sentiment Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json`
- Imported from pantry path: `n8n_Workflows/Social_Sentiment_Agent/workflow.json`
- Node count: 17

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

Get StackOverflow, Get Reddit ML, Get GitHub, Groq LLM Sentiment, Groq Topic Classification, Prepare for Google Sheets, Store in Google Sheets

## Node Type Summary

| Node Type | Count |
| --- | --- |
| function | 10 |
| googleSheets | 1 |
| httpRequest | 5 |
| manualTrigger | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Process StackOverflow | function |
| 2 | Get StackOverflow | httpRequest |
| 3 | Manual Trigger | manualTrigger |
| 4 | Combine All Data | function |
| 5 | Process Reddit ML | function |
| 6 | Get Reddit ML | httpRequest |
| 7 | Process GitHub | function |
| 8 | Get GitHub | httpRequest |
| 9 | Groq LLM Sentiment | httpRequest |
| 10 | Process Groq Sentiment | function |
| 11 | Groq Topic Classification | httpRequest |
| 12 | Topic Clustering Engine | function |
| 13 | Signal-to-Noise Filter | function |
| 14 | Social Sentiment Output | function |
| 15 | Enhanced Data Export | function |
| 16 | Prepare for Google Sheets | function |
| 17 | Store in Google Sheets | googleSheets |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

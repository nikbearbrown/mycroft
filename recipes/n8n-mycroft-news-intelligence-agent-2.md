# Recipe: Mycroft - News Intelligence Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json`
- Imported from pantry path: `n8n_Workflows/Orchestrator/v1/Mycroft - News Intelligence Agent.json`
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

Webhook, Respond to Webhook

## Agent/AI Nodes

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

NewsApiKey, HTTP Request, HTTP Request1, Insert rows in a table, Send email, Webhook, Respond to Webhook

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 7 |
| emailSend | 1 |
| httpRequest | 3 |
| merge | 1 |
| postgres | 1 |
| respondToWebhook | 1 |
| set | 2 |
| webhook | 1 |
| xml | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Company List | code |
| 2 | Build Query | code |
| 3 | Merge | merge |
| 4 | normalizenewsapi | code |
| 5 | NewsApiKey | httpRequest |
| 6 | HTTP Request | httpRequest |
| 7 | XML | xml |
| 8 | ProcessNewData | code |
| 9 | Edit Fields | set |
| 10 | HTTP Request1 | httpRequest |
| 11 | RiskCalculator | code |
| 12 | Insert rows in a table | postgres |
| 13 | Alert Generator Code Node | code |
| 14 | Send email | emailSend |
| 15 | DailyGeneratorCode | code |
| 16 | Webhook | webhook |
| 17 | Respond to Webhook | respondToWebhook |
| 18 | Set Variables | set |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

# Recipe: Mycroft - SEC Filings Analysis Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json`
- Imported from pantry path: `n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json`
- Node count: 19

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

Webhook, Respond to Webhook, Respond to Webhook1

## Agent/AI Nodes

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

Webhook, Respond to Webhook, Respond to Webhook1, Read/Write Files from Disk, Read/Write Files from Disk1

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 5 |
| executeCommand | 6 |
| if | 2 |
| readWriteFile | 2 |
| respondToWebhook | 2 |
| set | 1 |
| webhook | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | If | if |
| 2 | Set Variables | set |
| 3 | Setup Github Repo | executeCommand |
| 4 | Set Path Variables | code |
| 5 | Setup Python Enviornment and Output Directories | executeCommand |
| 6 | Edgar_Fetcher | executeCommand |
| 7 | Validate Fetcher | code |
| 8 | Financial Analyzer | executeCommand |
| 9 | Narrative Parser | executeCommand |
| 10 | Error Handling | code |
| 11 | Cleanup  | executeCommand |
| 12 | Webhook | webhook |
| 13 | Respond to Webhook | respondToWebhook |
| 14 | If1 | if |
| 15 | Respond to Webhook1 | respondToWebhook |
| 16 | Read/Write Files from Disk | readWriteFile |
| 17 | Read/Write Files from Disk1 | readWriteFile |
| 18 | Parse Results | code |
| 19 | Parse Both Results | code |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

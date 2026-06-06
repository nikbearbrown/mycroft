# Recipe: Mycroft - Patent Intelligence Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json`
- Imported from pantry path: `n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json`
- Node count: 15

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

Send Report Email, Error Notification, Webhook, Respond to Webhook

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 1 |
| emailSend | 2 |
| executeCommand | 6 |
| if | 1 |
| readBinaryFile | 2 |
| respondToWebhook | 1 |
| set | 1 |
| webhook | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Set Variables | set |
| 2 | Setup Github Repo | executeCommand |
| 3 | Set Path Variables | code |
| 4 | Setup Environment and Output Directories | executeCommand |
| 5 | Extract Patents | executeCommand |
| 6 | Check Extraction Success | if |
| 7 | Process Patents | executeCommand |
| 8 | Read Processed Data | readBinaryFile |
| 9 | Read Metrics | readBinaryFile |
| 10 | Send Report Email | emailSend |
| 11 | Error Notification | emailSend |
| 12 | Cleanup Repository | executeCommand |
| 13 | Cleanup Repository Error | executeCommand |
| 14 | Webhook | webhook |
| 15 | Respond to Webhook | respondToWebhook |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

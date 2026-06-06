# Recipe: Orchestrator

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Orchestrator.json`
- Imported from pantry path: `n8n_Workflows/Orchestrator/v1/Orchestrator.json`
- Node count: 5

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

When chat message received

## Agent/AI Nodes

When chat message received, Ollama Chat Model, The Brain

## External Writes or Side Effects

The Router

## Node Type Summary

| Node Type | Count |
| --- | --- |
| chainLlm | 1 |
| chatTrigger | 1 |
| code | 1 |
| httpRequest | 1 |
| lmChatOllama | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | When chat message received | chatTrigger |
| 2 | Ollama Chat Model | lmChatOllama |
| 3 | The Brain | chainLlm |
| 4 | The  Processor | code |
| 5 | The Router | httpRequest |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

# Recipe: Mycroft - Financial Intelligence Hub

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json`
- Imported from pantry path: `n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json`
- Node count: 22

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

When chat message received, LLM Chain Router, Ollama Chat Model, LLM Chain Analyst, Ollama Analyst Model, Structured Output Parser

## External Writes or Side Effects

Call SEC Workflow, Call Patent Workflow, Read/Write Files from Disk

## Node Type Summary

| Node Type | Count |
| --- | --- |
| chainLlm | 2 |
| chatTrigger | 1 |
| code | 9 |
| extractFromFile | 1 |
| httpRequest | 2 |
| if | 2 |
| lmChatOllama | 2 |
| outputParserStructured | 1 |
| readWriteFile | 1 |
| set | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | When chat message received | chatTrigger |
| 2 | Initialize Hub | set |
| 3 | Initialize Logging | code |
| 4 | LLM Chain Router | chainLlm |
| 5 | Ollama Chat Model | lmChatOllama |
| 6 | Call SEC? | if |
| 7 | Call Patent? | if |
| 8 | Call SEC Workflow | httpRequest |
| 9 | Call Patent Workflow | httpRequest |
| 10 | Log: SEC Called | code |
| 11 | Log: Patent Called | code |
| 12 | Aggregate Results | code |
| 13 | Log: Results Aggregated | code |
| 14 | LLM Chain Analyst | chainLlm |
| 15 | Ollama Analyst Model | lmChatOllama |
| 16 | Log: Analysis Complete | code |
| 17 | Format Chat Response | code |
| 18 | Log: Complete | code |
| 19 | No Tools Needed | code |
| 20 | Structured Output Parser | outputParserStructured |
| 21 | Read/Write Files from Disk | readWriteFile |
| 22 | Extract from File | extractFromFile |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

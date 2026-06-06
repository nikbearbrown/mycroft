# Recipe: ScenarioStressTestingAgent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json`
- Imported from pantry path: `n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json`
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

Webhook Trigger, When chat message received, Respond to Webhook

## Agent/AI Nodes

When chat message received, Basic LLM Chain, Groq Chat Model

## External Writes or Side Effects

Webhook Trigger, Respond to Webhook, Fetch_Data

## Node Type Summary

| Node Type | Count |
| --- | --- |
| chainLlm | 1 |
| chatTrigger | 1 |
| code | 5 |
| httpRequest | 1 |
| if | 1 |
| lmChatGroq | 1 |
| merge | 2 |
| respondToWebhook | 1 |
| set | 2 |
| webhook | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Webhook Trigger | webhook |
| 2 | Parse Input | set |
| 3 | Edit Fields | set |
| 4 | Validate Portfolio | code |
| 5 | Custom Scenario? | if |
| 6 | Load_Template_Scenario | code |
| 7 | When chat message received | chatTrigger |
| 8 | Basic LLM Chain | chainLlm |
| 9 | Groq Chat Model | lmChatGroq |
| 10 | Parse_LLM_Response | code |
| 11 | Stress_Test_Engine | code |
| 12 | Respond to Webhook | respondToWebhook |
| 13 | Fetch_Data | httpRequest |
| 14 | Merge | merge |
| 15 | Merge1 | merge |
| 16 | Save_Portfolio_Before_LLM | code |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

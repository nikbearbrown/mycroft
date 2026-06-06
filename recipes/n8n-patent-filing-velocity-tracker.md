# Recipe: Patent Filing Velocity Tracker

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json`
- Imported from pantry path: `n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json`
- Node count: 24

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

Manual Run Trigger, Dashboard Webhook, Pipeline Response, Serve Dashboard HTML

## Agent/AI Nodes

Claude 1: Velocity Score, Claude 2: Concept Novelty, Claude 3: Inventor Network, Claude 4: Cross-Company Convergence, Claude 5: Strategic Intent, Anthropic Model 1, Anthropic Model 2, Anthropic Model 3, Anthropic Model 4, Anthropic Model 5

## External Writes or Side Effects

Manual Run Trigger, Dashboard Webhook, Insert to Supabase, If Webhook, Pipeline Response, Serve Dashboard HTML

## Node Type Summary

| Node Type | Count |
| --- | --- |
| chainLlm | 5 |
| code | 7 |
| httpRequest | 1 |
| if | 1 |
| lmChatAnthropic | 5 |
| merge | 1 |
| respondToWebhook | 2 |
| webhook | 2 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Manual Run Trigger | webhook |
| 2 | Dashboard Webhook | webhook |
| 3 | Fetch Patent Data | code |
| 4 | 1A: Structural Clean | code |
| 5 | 1B: Category Classifier + Velocity Pre-Scorer | code |
| 6 | Aggregate for Claude | code |
| 7 | Claude 1: Velocity Score | chainLlm |
| 8 | Claude 2: Concept Novelty | chainLlm |
| 9 | Claude 3: Inventor Network | chainLlm |
| 10 | Claude 4: Cross-Company Convergence | chainLlm |
| 11 | Claude 5: Strategic Intent | chainLlm |
| 12 | Anthropic Model 1 | lmChatAnthropic |
| 13 | Anthropic Model 2 | lmChatAnthropic |
| 14 | Anthropic Model 3 | lmChatAnthropic |
| 15 | Anthropic Model 4 | lmChatAnthropic |
| 16 | Anthropic Model 5 | lmChatAnthropic |
| 17 | Merge Claude Outputs | merge |
| 18 | Signal Aggregator | code |
| 19 | Insert to Supabase | httpRequest |
| 20 | Check Trigger Type | code |
| 21 | If Webhook | if |
| 22 | Pipeline Response | respondToWebhook |
| 23 | Build Dashboard HTML | code |
| 24 | Serve Dashboard HTML | respondToWebhook |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

# Recipe: Retail Investor Anxiety Index

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json`
- Imported from pantry path: `n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json`
- Node count: 30

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

Schedule Trigger, Manual Run Trigger, Pipeline Response, Dashboard Webhook, Serve Dashboard HTML

## Agent/AI Nodes

Claude 1: Anxiety Score, Claude 2: Narrative Velocity, Claude 3: Herd Detection, Claude 4: Conviction vs Uncertainty, Claude 5: Crowd Cycle Stage, Anthropic Model 1, Anthropic Model 2, Anthropic Model 3, Anthropic Model 4, Anthropic Model 5

## External Writes or Side Effects

Manual Run Trigger, Fetch WSB, Fetch Investing, Fetch Stocks, Write output.json, Insert to Supabase, Pipeline Response, Dashboard Webhook, Serve Dashboard HTML

## Node Type Summary

| Node Type | Count |
| --- | --- |
| chainLlm | 5 |
| code | 9 |
| httpRequest | 4 |
| lmChatAnthropic | 5 |
| merge | 2 |
| respondToWebhook | 2 |
| scheduleTrigger | 1 |
| webhook | 2 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Schedule Trigger | scheduleTrigger |
| 2 | Manual Run Trigger | webhook |
| 3 | Fetch WSB | httpRequest |
| 4 | Fetch Investing | httpRequest |
| 5 | Fetch Stocks | httpRequest |
| 6 | Merge Reddit Feeds | merge |
| 7 | 1A: Raw Merge & Structural Clean | code |
| 8 | 1B: Linguistic & Relevance Filter | code |
| 9 | Keyword Pre-Scorer | code |
| 10 | Aggregate for Claude | code |
| 11 | Claude 1: Anxiety Score | chainLlm |
| 12 | Claude 2: Narrative Velocity | chainLlm |
| 13 | Claude 3: Herd Detection | chainLlm |
| 14 | Claude 4: Conviction vs Uncertainty | chainLlm |
| 15 | Claude 5: Crowd Cycle Stage | chainLlm |
| 16 | Anthropic Model 1 | lmChatAnthropic |
| 17 | Anthropic Model 2 | lmChatAnthropic |
| 18 | Anthropic Model 3 | lmChatAnthropic |
| 19 | Anthropic Model 4 | lmChatAnthropic |
| 20 | Anthropic Model 5 | lmChatAnthropic |
| 21 | Merge Claude Outputs | merge |
| 22 | Signal Aggregator | code |
| 23 | Persist to File | code |
| 24 | Generate Quickchart URLs | code |
| 25 | Write output.json | code |
| 26 | Insert to Supabase | httpRequest |
| 27 | Pipeline Response | respondToWebhook |
| 28 | Dashboard Webhook | webhook |
| 29 | Build Dashboard Response | code |
| 30 | Serve Dashboard HTML | respondToWebhook |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

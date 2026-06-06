# Recipe: Market Sentiment Analysis - Part 1

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json`
- Imported from pantry path: `n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json`
- Node count: 11

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

Webhook Trigger, Webhook Response

## Agent/AI Nodes

AI Analysis & Synthesis

## External Writes or Side Effects

Webhook Trigger, Fetch Price Data, Fetch News Headlines, Fetch Reddit Mentions, Send to Slack, Send Email, Webhook Response

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 3 |
| emailSend | 1 |
| httpRequest | 3 |
| lmChatAnthropic | 1 |
| respondToWebhook | 1 |
| slack | 1 |
| webhook | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Webhook Trigger | webhook |
| 2 | Parse Question & Extract Tickers | code |
| 3 | Fetch Price Data | httpRequest |
| 4 | Fetch News Headlines | httpRequest |
| 5 | Fetch Reddit Mentions | httpRequest |
| 6 | Aggregate & Calculate Sentiment | code |
| 7 | AI Analysis & Synthesis | lmChatAnthropic |
| 8 | Format Response | code |
| 9 | Send to Slack | slack |
| 10 | Send Email | emailSend |
| 11 | Webhook Response | respondToWebhook |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

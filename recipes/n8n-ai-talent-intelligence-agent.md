# Recipe: AI Talent Intelligence Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json`
- Imported from pantry path: `n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json`
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

▶️ START - Run Complete Analysis, When chat message received

## Agent/AI Nodes

When chat message received, Basic LLM Chain, Groq Chat Model

## External Writes or Side Effects

📚 SOURCE 1: ArXiv Papers, 📰 SOURCE 2: News Search, 💾 Save to Database, 📧 Format Email Report, 📬 Send Email Report

## Node Type Summary

| Node Type | Count |
| --- | --- |
| aggregate | 1 |
| chainLlm | 1 |
| chatTrigger | 1 |
| code | 5 |
| emailSend | 1 |
| httpRequest | 2 |
| if | 1 |
| lmChatGroq | 1 |
| manualTrigger | 1 |
| merge | 1 |
| postgres | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | ▶️ START - Run Complete Analysis | manualTrigger |
| 2 | 📚 SOURCE 1: ArXiv Papers | httpRequest |
| 3 | 📰 SOURCE 2: News Search | httpRequest |
| 4 | 🔄 Parse ArXiv Data | code |
| 5 | 🔄 Parse News Data | code |
| 6 | 🔍 FILTER: High Significance Only | if |
| 7 | 📊 AGGREGATE Statistics | aggregate |
| 8 | 📋 Generate Intelligence Report | code |
| 9 | 💾 Save to Database | postgres |
| 10 | 📧 Format Email Report | code |
| 11 | 📬 Send Email Report | emailSend |
| 12 | Code | code |
| 13 | Merge | merge |
| 14 | When chat message received | chatTrigger |
| 15 | Basic LLM Chain | chainLlm |
| 16 | Groq Chat Model | lmChatGroq |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

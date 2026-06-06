# Recipe: Mycroft - Financial Regulatory Intelligence System - Enhanced

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json`
- Imported from pantry path: `n8n_Workflows/Regulatory_Scanning_Agent/Mycroft - Financial Regulatory Intelligence System.json`
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

Schedule Every Day

## Agent/AI Nodes

No explicit AI-agent node detected by type/name. Treat transformation and decision nodes as candidates for agentic conversion.

## External Writes or Side Effects

Send Email Alert, Read/Write Files from Disk, Send email, Generate Email, Mark email sent, Insert data into DB

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 6 |
| emailSend | 2 |
| if | 4 |
| merge | 1 |
| postgres | 2 |
| readWriteFile | 1 |
| rssFeedRead | 5 |
| scheduleTrigger | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Federal Register - Securities | rssFeedRead |
| 2 | SEC Press Releases | rssFeedRead |
| 3 | FINRA Enforcement News | rssFeedRead |
| 4 | CFTC Regulations | rssFeedRead |
| 5 | Investment Advisor Rules | rssFeedRead |
| 6 | Merge All Sources | merge |
| 7 | Normalize Data | code |
| 8 | Filter Valid Content | if |
| 9 | Generate HTML Report | code |
| 10 | High Priority Filter | if |
| 11 | Send Email Alert | emailSend |
| 12 | Read/Write Files from Disk | readWriteFile |
| 13 | If | if |
| 14 | Send email | emailSend |
| 15 | Schedule Every Day | scheduleTrigger |
| 16 | Generate Email | code |
| 17 | Mark email sent | postgres |
| 18 | Keyword Analysis & Urgency Scoring | code |
| 19 | Insert data into DB | postgres |
| 20 | Prepare Data | code |
| 21 | Code in JavaScript | code |
| 22 | If2 | if |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

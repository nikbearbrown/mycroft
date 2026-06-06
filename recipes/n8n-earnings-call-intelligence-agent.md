# Recipe: Earnings Call Intelligence Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json`
- Imported from pantry path: `n8n_Workflows/Earnings Call Intelligence Agent/Earnings_Call_Intelligence_Agent.json`
- Node count: 26

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

Webhook: Receive Transcript, Webhook Response

## Agent/AI Nodes

DB: Log Agent Run

## External Writes or Side Effects

Webhook: Receive Transcript, DB: Insert earnings_call, DB: Insert transcript_section, DB: Insert guidance_signal, DB: Insert risk_admission, DB: Insert qa_pressure, DB: Log Agent Run, Fetch All Signals for Summary, DB: Insert call_summary, DB: Mark Call Complete, Webhook Response, Groq: Generate Call Summary, Groq: Parse Transcript Sections, Groq: Extract Guidance Signals, Groq: Extract Risk Admissions, Groq: Map QA Pressure, Execute a SQL query

## Node Type Summary

| Node Type | Count |
| --- | --- |
| code | 7 |
| httpRequest | 5 |
| postgres | 10 |
| respondToWebhook | 1 |
| set | 1 |
| switch | 1 |
| webhook | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | Webhook: Receive Transcript | webhook |
| 2 | Validate Input | code |
| 3 | DB: Insert earnings_call | postgres |
| 4 | Set Call Context | set |
| 5 | Process Section Response | code |
| 6 | DB: Insert transcript_section | postgres |
| 7 | Route by Section Type | switch |
| 8 | Process Guidance Response | code |
| 9 | Process Risk Response | code |
| 10 | Process QA Response | code |
| 11 | DB: Insert guidance_signal | postgres |
| 12 | DB: Insert risk_admission | postgres |
| 13 | DB: Insert qa_pressure | postgres |
| 14 | DB: Log Agent Run | postgres |
| 15 | Fetch All Signals for Summary | postgres |
| 16 | Process Summary Response | code |
| 17 | DB: Insert call_summary | postgres |
| 18 | DB: Mark Call Complete | postgres |
| 19 | Final Response | code |
| 20 | Webhook Response | respondToWebhook |
| 21 | Groq: Generate Call Summary | httpRequest |
| 22 | Groq: Parse Transcript Sections | httpRequest |
| 23 | Groq: Extract Guidance Signals | httpRequest |
| 24 | Groq: Extract Risk Admissions | httpRequest |
| 25 | Groq: Map QA Pressure | httpRequest |
| 26 | Execute a SQL query | postgres |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

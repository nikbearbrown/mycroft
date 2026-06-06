# Recipe: Finance Literacy Bot - Chatbot w/ Memory

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json`
- Imported from pantry path: `n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json`
- Node count: 13

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

When chat message received, Respond to Webhook

## Agent/AI Nodes

When chat message received, AI Agent, Groq Chat Model, Pinecone Vector Store, Embeddings HuggingFace Inference1, Simple Memory

## External Writes or Side Effects

Pinecone Vector Store, Fetch User History, Groq - Gap Analysis, Update DB - User Interactions, Update DB - User Knowledge Profile, Respond to Webhook

## Node Type Summary

| Node Type | Count |
| --- | --- |
| agent | 1 |
| chatTrigger | 1 |
| code | 1 |
| embeddingsHuggingFaceInference | 1 |
| httpRequest | 1 |
| lmChatGroq | 1 |
| memoryBufferWindow | 1 |
| postgres | 3 |
| respondToWebhook | 1 |
| set | 1 |
| vectorStorePinecone | 1 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | When chat message received | chatTrigger |
| 2 | AI Agent | agent |
| 3 | Groq Chat Model | lmChatGroq |
| 4 | Pinecone Vector Store | vectorStorePinecone |
| 5 | Embeddings HuggingFace Inference1 | embeddingsHuggingFaceInference |
| 6 | Fetch User History | postgres |
| 7 | Code in JavaScript | code |
| 8 | Parse Gap Analysis | set |
| 9 | Groq - Gap Analysis | httpRequest |
| 10 | Update DB - User Interactions | postgres |
| 11 | Update DB - User Knowledge Profile | postgres |
| 12 | Respond to Webhook | respondToWebhook |
| 13 | Simple Memory | memoryBufferWindow |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

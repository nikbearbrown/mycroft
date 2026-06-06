# Finance Literacy Bot - Chatbot w/ Memory

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (7 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (2 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/finance-literacy-bot-chatbot-w-memory.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `finance-literacy-bot-chatbot-w-memory__fetch-user-history`. Labor: AI. Script called: `scripts/ingest/finance-literacy-bot-chatbot-w-memory__fetch-user-history.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `finance-literacy-bot-chatbot-w-memory__update-db-user-interactions`. Labor: AI. Script called: `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-interactions.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `finance-literacy-bot-chatbot-w-memory__update-db-user-knowledge-profile`. Labor: AI. Script called: `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-knowledge-profile.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `finance-literacy-bot-chatbot-w-memory__ai-agent`. Labor: AI. Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__ai-agent.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `finance-literacy-bot-chatbot-w-memory__groq-chat-model`. Labor: AI. Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-chat-model.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `finance-literacy-bot-chatbot-w-memory__pinecone-vector-store`. Labor: AI. Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__pinecone-vector-store.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `finance-literacy-bot-chatbot-w-memory__embeddings-huggingface-inference1`. Labor: AI. Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__embeddings-huggingface-inference1.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `finance-literacy-bot-chatbot-w-memory__parse-gap-analysis`. Labor: AI. Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__parse-gap-analysis.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `finance-literacy-bot-chatbot-w-memory__groq-gap-analysis`. Labor: AI. Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-gap-analysis.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `finance-literacy-bot-chatbot-w-memory__simple-memory`. Labor: AI. Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__simple-memory.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/finance-literacy-bot-chatbot-w-memory/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/finance-literacy-bot-chatbot-w-memory-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | When chat message received | `chatTrigger` | conductor |
| 2 | AI Agent | `agent` | tool |
| 3 | Groq Chat Model | `lmChatGroq` | tool |
| 4 | Pinecone Vector Store | `vectorStorePinecone` | tool |
| 5 | Embeddings HuggingFace Inference1 | `embeddingsHuggingFaceInference` | tool |
| 6 | Fetch User History | `postgres` | ingest |
| 7 | Code in JavaScript | `code` | conductor |
| 8 | Parse Gap Analysis | `set` | tool |
| 9 | Groq - Gap Analysis | `httpRequest` | tool |
| 10 | Update DB - User Interactions | `postgres` | gigo |
| 11 | Update DB - User Knowledge Profile | `postgres` | gigo |
| 12 | Respond to Webhook | `respondToWebhook` | report |
| 13 | Simple Memory | `memoryBufferWindow` | tool |

## Script Index

- `scripts/ingest/finance-literacy-bot-chatbot-w-memory__fetch-user-history.py`
- `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-interactions.py`
- `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-knowledge-profile.py`
- `scripts/tools/finance-literacy-bot-chatbot-w-memory__ai-agent.py`
- `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-chat-model.py`
- `scripts/tools/finance-literacy-bot-chatbot-w-memory__pinecone-vector-store.py`
- `scripts/tools/finance-literacy-bot-chatbot-w-memory__embeddings-huggingface-inference1.py`
- `scripts/tools/finance-literacy-bot-chatbot-w-memory__parse-gap-analysis.py`
- `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-gap-analysis.py`
- `scripts/tools/finance-literacy-bot-chatbot-w-memory__simple-memory.py`

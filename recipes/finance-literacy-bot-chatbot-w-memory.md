# Finance Literacy Bot - Chatbot w/ Memory

## Purpose

Finance Literacy Bot - Chatbot w/ Memory defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to finance literacy bot - chatbot w/ memory. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When chat message received | `chatTrigger` | conductor |
| AI Agent | `agent` | tool |
| Groq Chat Model | `lmChatGroq` | tool |
| Pinecone Vector Store | `vectorStorePinecone` | tool |
| Embeddings HuggingFace Inference1 | `embeddingsHuggingFaceInference` | tool |
| Fetch User History | `postgres` | ingest |
| Code in JavaScript | `code` | conductor |
| Parse Gap Analysis | `set` | tool |
| Groq - Gap Analysis | `httpRequest` | tool |
| Update DB - User Interactions | `postgres` | gigo |
| Update DB - User Knowledge Profile | `postgres` | gigo |
| Respond to Webhook | `respondToWebhook` | report |
| Simple Memory | `memoryBufferWindow` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (7 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (2 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/finance-literacy-bot-chatbot-w-memory.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run finance-literacy-bot-chatbot-w-memory --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/finance-literacy-bot-chatbot-w-memory data/verified/finance-literacy-bot-chatbot-w-memory -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/finance-literacy-bot-chatbot-w-memory.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: AI Agent. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__ai-agent.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Groq Chat Model. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Pinecone Vector Store. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__pinecone-vector-store.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Embeddings HuggingFace Inference1. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__embeddings-huggingface-inference1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Fetch User History. Labor: AI with Human gate.
   Script called: `scripts/ingest/finance-literacy-bot-chatbot-w-memory__fetch-user-history.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/finance-literacy-bot-chatbot-w-memory/.
7. Step name: Parse Gap Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__parse-gap-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Groq - Gap Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-gap-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Update DB - User Interactions. Labor: AI with Human gate.
   Script called: `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-interactions.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/finance-literacy-bot-chatbot-w-memory/.
10. Step name: Update DB - User Knowledge Profile. Labor: AI with Human gate.
   Script called: `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-knowledge-profile.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/finance-literacy-bot-chatbot-w-memory/.
11. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/finance-literacy-bot-chatbot-w-memory__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
12. Step name: Simple Memory. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-chatbot-w-memory__simple-memory.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/finance-literacy-bot-chatbot-w-memory__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/finance-literacy-bot-chatbot-w-memory-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/finance-literacy-bot-chatbot-w-memory-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Finance Literacy Bot - Chatbot w/ Memory` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run finance-literacy-bot-chatbot-w-memory --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run finance-literacy-bot-chatbot-w-memory --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| AI Agent | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step ai-agent` | `--no-write` |
| Groq Chat Model | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step groq-chat-model` | `--no-write` |
| Pinecone Vector Store | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step pinecone-vector-store` | `--no-write` |
| Embeddings HuggingFace Inference1 | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step embeddings-huggingface-inference1` | `--no-write` |
| Fetch User History | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step fetch-user-history` | `--sample` |
| Parse Gap Analysis | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step parse-gap-analysis` | `--no-write` |
| Groq - Gap Analysis | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step groq-gap-analysis` | `--no-write` |
| Update DB - User Interactions | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step update-db-user-interactions` |  |
| Update DB - User Knowledge Profile | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step update-db-user-knowledge-profile` |  |
| Respond to Webhook | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step respond-to-webhook` | `--no-write` |
| Simple Memory | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step simple-memory` | `--no-write` |
| Produce human report | `snickerdoodle run finance-literacy-bot-chatbot-w-memory --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate finance-literacy-bot-chatbot-w-memory --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate finance-literacy-bot-chatbot-w-memory --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate finance-literacy-bot-chatbot-w-memory --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| AI Agent | `scripts/tools/finance-literacy-bot-chatbot-w-memory__ai-agent.py` | tool |
| Groq Chat Model | `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-chat-model.py` | tool |
| Pinecone Vector Store | `scripts/tools/finance-literacy-bot-chatbot-w-memory__pinecone-vector-store.py` | tool |
| Embeddings HuggingFace Inference1 | `scripts/tools/finance-literacy-bot-chatbot-w-memory__embeddings-huggingface-inference1.py` | tool |
| Fetch User History | `scripts/ingest/finance-literacy-bot-chatbot-w-memory__fetch-user-history.py` | ingest |
| Parse Gap Analysis | `scripts/tools/finance-literacy-bot-chatbot-w-memory__parse-gap-analysis.py` | tool |
| Groq - Gap Analysis | `scripts/tools/finance-literacy-bot-chatbot-w-memory__groq-gap-analysis.py` | tool |
| Update DB - User Interactions | `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-interactions.py` | gigo |
| Update DB - User Knowledge Profile | `scripts/gigo/finance-literacy-bot-chatbot-w-memory__update-db-user-knowledge-profile.py` | gigo |
| Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/finance-literacy-bot-chatbot-w-memory__respond-to-webhook.py` | tool |
| Simple Memory | `scripts/tools/finance-literacy-bot-chatbot-w-memory__simple-memory.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/finance-literacy-bot-chatbot-w-memory__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/finance-literacy-bot-chatbot-w-memory/` | JSON |
| Verified data | `data/verified/finance-literacy-bot-chatbot-w-memory/` | JSON |
| Agent log | `logs/finance-literacy-bot-chatbot-w-memory-[DATE].json` | JSON |
| Human report | `reports/generated/finance-literacy-bot-chatbot-w-memory-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - Chatbot w_ Memory.json`

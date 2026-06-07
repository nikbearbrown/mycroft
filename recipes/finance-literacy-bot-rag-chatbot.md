# Finance Literacy Bot - RAG & ChatBot

## Purpose

Finance Literacy Bot - RAG & ChatBot defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to finance literacy bot - rag & chatbot. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Original workflow sources | [TODO: DEV] Parse original workflow node types. | [TODO: DATA SOURCE] Extract source URLs or paths from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| When chat message received | `chatTrigger` | conductor |
| AI Agent | `agent` | tool |
| Groq Chat Model | `lmChatGroq` | tool |
| Pinecone Vector Store | `vectorStorePinecone` | tool |
| Embeddings HuggingFace Inference1 | `embeddingsHuggingFaceInference` | tool |
| SerpAPI | `toolSerpApi` | tool |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (5 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (1 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - RAG & ChatBot.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/finance-literacy-bot-rag-chatbot.md" && rg -n "\[TODO: DEFINE]" "recipes/finance-literacy-bot-rag-chatbot.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/finance-literacy-bot-rag-chatbot/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/finance-literacy-bot-rag-chatbot data/verified/finance-literacy-bot-rag-chatbot -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/finance-literacy-bot-rag-chatbot-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/finance-literacy-bot-rag-chatbot.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/finance-literacy-bot-rag-chatbot-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/finance-literacy-bot-rag-chatbot.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/finance-literacy-bot-rag-chatbot-[DATE].json && test -f reports/generated/finance-literacy-bot-rag-chatbot-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `finance-literacy-bot-rag-chatbot`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/finance-literacy-bot-rag-chatbot-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `finance-literacy-bot-rag-chatbot`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/finance-literacy-bot-rag-chatbot/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/finance-literacy-bot-rag-chatbot-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `finance-literacy-bot-rag-chatbot`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/finance-literacy-bot-rag-chatbot/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/finance-literacy-bot-rag-chatbot-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `finance-literacy-bot-rag-chatbot`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/finance-literacy-bot-rag-chatbot/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `finance-literacy-bot-rag-chatbot`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `finance-literacy-bot-rag-chatbot`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/finance-literacy-bot-rag-chatbot-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/finance-literacy-bot-rag-chatbot-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Finance Literacy Bot - RAG & ChatBot` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run finance-literacy-bot-rag-chatbot --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run finance-literacy-bot-rag-chatbot --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run finance-literacy-bot-rag-chatbot --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run finance-literacy-bot-rag-chatbot --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run finance-literacy-bot-rag-chatbot --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run finance-literacy-bot-rag-chatbot --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run finance-literacy-bot-rag-chatbot --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run finance-literacy-bot-rag-chatbot --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate finance-literacy-bot-rag-chatbot --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate finance-literacy-bot-rag-chatbot --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate finance-literacy-bot-rag-chatbot --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate finance-literacy-bot-rag-chatbot --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate finance-literacy-bot-rag-chatbot --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate finance-literacy-bot-rag-chatbot --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/finance-literacy-bot-rag-chatbot-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/finance-literacy-bot-rag-chatbot-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/finance-literacy-bot-rag-chatbot-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/finance-literacy-bot-rag-chatbot-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/finance-literacy-bot-rag-chatbot-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/finance-literacy-bot-rag-chatbot-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/finance-literacy-bot-rag-chatbot/` | JSON |
| Verified data | `data/verified/finance-literacy-bot-rag-chatbot/` | JSON |
| Agent log | `logs/finance-literacy-bot-rag-chatbot-[DATE].json` | JSON |
| Human report | `reports/generated/finance-literacy-bot-rag-chatbot-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - RAG & ChatBot.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - RAG & ChatBot.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Finance Literacy Bot - RAG & ChatBot defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to finance literacy bot - rag & chatbot. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - RAG & ChatBot.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/finance-literacy-bot-rag-chatbot.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run finance-literacy-bot-rag-chatbot --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/finance-literacy-bot-rag-chatbot data/verified/finance-literacy-bot-rag-chatbot -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/finance-literacy-bot-rag-chatbot.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Finance Literacy Bot - RAG & ChatBot.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: AI Agent. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-ai-agent.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Groq Chat Model. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-groq-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Pinecone Vector Store. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-pinecone-vector-store.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Embeddings HuggingFace Inference1. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-embeddings-huggingface-inference1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: SerpAPI. Labor: AI with Human gate.
   Script called: `scripts/tools/finance-literacy-bot-rag-chatbot-serpapi.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/finance-literacy-bot-rag-chatbot-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

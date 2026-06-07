# Financial Literacy Bot - Knowledge Base

## Purpose

Financial Literacy Bot - Knowledge Base defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to financial literacy bot - knowledge base. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Original workflow sources | [TODO: DEV] Parse original workflow node types. | [TODO: DATA SOURCE] Extract source URLs or paths from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Pinecone Vector Store | `vectorStorePinecone` | tool |
| Default Data Loader | `documentDefaultDataLoader` | tool |
| When clicking 'Execute workflow' | `manualTrigger` | conductor |
| Embeddings HuggingFace Inference | `embeddingsHuggingFaceInference` | tool |
| Recursive Character Text Splitter | `textSplitterRecursiveCharacterTextSplitter` | tool |
| Search Knowledge Base Files | `googleDrive` | tool |
| Download KB Files | `googleDrive` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Tool node outputs | JSON | Converted tool steps (6 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (1 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Financial Literacy Bot - Knowledge Base.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Financial Literacy Bot - Knowledge Base.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/financial-literacy-bot-knowledge-base.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run financial-literacy-bot-knowledge-base --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/financial-literacy-bot-knowledge-base data/verified/financial-literacy-bot-knowledge-base -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/financial-literacy-bot-knowledge-base.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Financial Literacy Bot - Knowledge Base.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Pinecone Vector Store. Labor: AI with Human gate.
   Script called: `scripts/tools/financial-literacy-bot-knowledge-base__pinecone-vector-store.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Default Data Loader. Labor: AI with Human gate.
   Script called: `scripts/tools/financial-literacy-bot-knowledge-base__default-data-loader.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Embeddings HuggingFace Inference. Labor: AI with Human gate.
   Script called: `scripts/tools/financial-literacy-bot-knowledge-base__embeddings-huggingface-inference.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Recursive Character Text Splitter. Labor: AI with Human gate.
   Script called: `scripts/tools/financial-literacy-bot-knowledge-base__recursive-character-text-splitter.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Search Knowledge Base Files. Labor: AI with Human gate.
   Script called: `scripts/tools/financial-literacy-bot-knowledge-base__search-knowledge-base-files.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Download KB Files. Labor: AI with Human gate.
   Script called: `scripts/tools/financial-literacy-bot-knowledge-base__download-kb-files.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/financial-literacy-bot-knowledge-base__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/financial-literacy-bot-knowledge-base-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/financial-literacy-bot-knowledge-base-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Financial Literacy Bot - Knowledge Base` run.
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
`snickerdoodle run financial-literacy-bot-knowledge-base --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run financial-literacy-bot-knowledge-base --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Pinecone Vector Store | `snickerdoodle run financial-literacy-bot-knowledge-base --step pinecone-vector-store` | `--no-write` |
| Default Data Loader | `snickerdoodle run financial-literacy-bot-knowledge-base --step default-data-loader` | `--no-write` |
| Embeddings HuggingFace Inference | `snickerdoodle run financial-literacy-bot-knowledge-base --step embeddings-huggingface-inference` | `--no-write` |
| Recursive Character Text Splitter | `snickerdoodle run financial-literacy-bot-knowledge-base --step recursive-character-text-splitter` | `--no-write` |
| Search Knowledge Base Files | `snickerdoodle run financial-literacy-bot-knowledge-base --step search-knowledge-base-files` | `--no-write` |
| Download KB Files | `snickerdoodle run financial-literacy-bot-knowledge-base --step download-kb-files` | `--no-write` |
| Produce human report | `snickerdoodle run financial-literacy-bot-knowledge-base --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate financial-literacy-bot-knowledge-base --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate financial-literacy-bot-knowledge-base --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate financial-literacy-bot-knowledge-base --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Pinecone Vector Store | `scripts/tools/financial-literacy-bot-knowledge-base__pinecone-vector-store.py` | tool |
| Default Data Loader | `scripts/tools/financial-literacy-bot-knowledge-base__default-data-loader.py` | tool |
| Embeddings HuggingFace Inference | `scripts/tools/financial-literacy-bot-knowledge-base__embeddings-huggingface-inference.py` | tool |
| Recursive Character Text Splitter | `scripts/tools/financial-literacy-bot-knowledge-base__recursive-character-text-splitter.py` | tool |
| Search Knowledge Base Files | `scripts/tools/financial-literacy-bot-knowledge-base__search-knowledge-base-files.py` | tool |
| Download KB Files | `scripts/tools/financial-literacy-bot-knowledge-base__download-kb-files.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/financial-literacy-bot-knowledge-base__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/financial-literacy-bot-knowledge-base/` | JSON |
| Verified data | `data/verified/financial-literacy-bot-knowledge-base/` | JSON |
| Agent log | `logs/financial-literacy-bot-knowledge-base-[DATE].json` | JSON |
| Human report | `reports/generated/financial-literacy-bot-knowledge-base-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Literacy_Bot/Financial Literacy Bot - Knowledge Base.json`

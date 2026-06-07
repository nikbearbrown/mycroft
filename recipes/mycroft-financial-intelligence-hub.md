# Mycroft - Financial Intelligence Hub

## Purpose

Mycroft - Financial Intelligence Hub defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - financial intelligence hub. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When chat message received | `chatTrigger` | conductor |
| Initialize Hub | `set` | conductor |
| Initialize Logging | `code` | conductor |
| LLM Chain Router | `chainLlm` | tool |
| Ollama Chat Model | `lmChatOllama` | tool |
| Call SEC? | `if` | conductor |
| Call Patent? | `if` | conductor |
| Call SEC Workflow | `httpRequest` | ingest |
| Call Patent Workflow | `httpRequest` | ingest |
| Log: SEC Called | `code` | conductor |
| Log: Patent Called | `code` | conductor |
| Aggregate Results | `code` | conductor |
| Log: Results Aggregated | `code` | conductor |
| LLM Chain Analyst | `chainLlm` | tool |
| Ollama Analyst Model | `lmChatOllama` | tool |
| Log: Analysis Complete | `code` | tool |
| Format Chat Response | `code` | conductor |
| Log: Complete | `code` | conductor |
| No Tools Needed | `code` | conductor |
| Structured Output Parser | `outputParserStructured` | gigo |
| Read/Write Files from Disk | `readWriteFile` | tool |
| Extract from File | `extractFromFile` | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (6 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (12 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-financial-intelligence-hub.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-financial-intelligence-hub --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-financial-intelligence-hub data/verified/mycroft-financial-intelligence-hub -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-financial-intelligence-hub.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: LLM Chain Router. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-router.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Ollama Chat Model. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-intelligence-hub__ollama-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Call SEC Workflow. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroft-financial-intelligence-hub__call-sec-workflow.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroft-financial-intelligence-hub/.
5. Step name: Call Patent Workflow. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroft-financial-intelligence-hub__call-patent-workflow.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroft-financial-intelligence-hub/.
6. Step name: LLM Chain Analyst. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-analyst.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Ollama Analyst Model. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-intelligence-hub__ollama-analyst-model.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Log: Analysis Complete. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-intelligence-hub__log-analysis-complete.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Structured Output Parser. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-financial-intelligence-hub__structured-output-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-financial-intelligence-hub/.
10. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-financial-intelligence-hub__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Extract from File. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-financial-intelligence-hub__extract-from-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-financial-intelligence-hub/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-intelligence-hub__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-financial-intelligence-hub-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-financial-intelligence-hub-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Financial Intelligence Hub` run.
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
`snickerdoodle run mycroft-financial-intelligence-hub --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-financial-intelligence-hub --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| LLM Chain Router | `snickerdoodle run mycroft-financial-intelligence-hub --step llm-chain-router` | `--no-write` |
| Ollama Chat Model | `snickerdoodle run mycroft-financial-intelligence-hub --step ollama-chat-model` | `--no-write` |
| Call SEC Workflow | `snickerdoodle run mycroft-financial-intelligence-hub --step call-sec-workflow` | `--sample` |
| Call Patent Workflow | `snickerdoodle run mycroft-financial-intelligence-hub --step call-patent-workflow` | `--sample` |
| LLM Chain Analyst | `snickerdoodle run mycroft-financial-intelligence-hub --step llm-chain-analyst` | `--no-write` |
| Ollama Analyst Model | `snickerdoodle run mycroft-financial-intelligence-hub --step ollama-analyst-model` | `--no-write` |
| Log: Analysis Complete | `snickerdoodle run mycroft-financial-intelligence-hub --step log-analysis-complete` | `--no-write` |
| Structured Output Parser | `snickerdoodle run mycroft-financial-intelligence-hub --step structured-output-parser` |  |
| Read/Write Files from Disk | `snickerdoodle run mycroft-financial-intelligence-hub --step read-write-files-from-disk` | `--no-write` |
| Extract from File | `snickerdoodle run mycroft-financial-intelligence-hub --step extract-from-file` |  |
| Produce human report | `snickerdoodle run mycroft-financial-intelligence-hub --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-financial-intelligence-hub --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-financial-intelligence-hub --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-financial-intelligence-hub --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| LLM Chain Router | `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-router.py` | tool |
| Ollama Chat Model | `scripts/tools/mycroft-financial-intelligence-hub__ollama-chat-model.py` | tool |
| Call SEC Workflow | `scripts/ingest/mycroft-financial-intelligence-hub__call-sec-workflow.py` | ingest |
| Call Patent Workflow | `scripts/ingest/mycroft-financial-intelligence-hub__call-patent-workflow.py` | ingest |
| LLM Chain Analyst | `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-analyst.py` | tool |
| Ollama Analyst Model | `scripts/tools/mycroft-financial-intelligence-hub__ollama-analyst-model.py` | tool |
| Log: Analysis Complete | `scripts/tools/mycroft-financial-intelligence-hub__log-analysis-complete.py` | tool |
| Structured Output Parser | `scripts/gigo/mycroft-financial-intelligence-hub__structured-output-parser.py` | gigo |
| Read/Write Files from Disk | `scripts/tools/mycroft-financial-intelligence-hub__read-write-files-from-disk.py` | tool |
| Extract from File | `scripts/gigo/mycroft-financial-intelligence-hub__extract-from-file.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-financial-intelligence-hub__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-financial-intelligence-hub/` | JSON |
| Verified data | `data/verified/mycroft-financial-intelligence-hub/` | JSON |
| Agent log | `logs/mycroft-financial-intelligence-hub-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-financial-intelligence-hub-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json`

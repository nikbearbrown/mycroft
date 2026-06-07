# Mycroft - Financial Intelligence Hub

## Purpose

Mycroft - Financial Intelligence Hub defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - financial intelligence hub. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Call SEC Workflow | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Call Patent Workflow | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| When chat message received | chatTrigger | conductor |
| Initialize Hub | set | gigo |
| Initialize Logging | code | gigo |
| LLM Chain Router | chainLlm | gigo |
| Ollama Chat Model | lmChatOllama | gigo |
| Call SEC? | if | conductor |
| Call Patent? | if | conductor |
| Call SEC Workflow | httpRequest | ingest |
| Call Patent Workflow | httpRequest | ingest |
| Log: SEC Called | code | gigo |
| Log: Patent Called | code | gigo |
| Aggregate Results | code | gigo |
| Log: Results Aggregated | code | gigo |
| LLM Chain Analyst | chainLlm | gigo |
| Ollama Analyst Model | lmChatOllama | gigo |
| Log: Analysis Complete | code | gigo |
| Format Chat Response | code | gigo |
| Log: Complete | code | gigo |
| No Tools Needed | code | gigo |
| Structured Output Parser | outputParserStructured | gigo |
| Read/Write Files from Disk | readWriteFile | tool |
| Extract from File | extractFromFile | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-financial-intelligence-hub.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-financial-intelligence-hub --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-financial-intelligence-hub data/verified/n8n-mycroft-financial-intelligence-hub -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-financial-intelligence-hub.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Initialize Hub. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__initialize-hub.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
3. Step name: Initialize Logging. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__initialize-logging.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
4. Step name: LLM Chain Router. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__llm-chain-router.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
5. Step name: Ollama Chat Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__ollama-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
6. Step name: Call SEC Workflow. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-intelligence-hub__call-sec-workflow.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-intelligence-hub/.
7. Step name: Call Patent Workflow. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-intelligence-hub__call-patent-workflow.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-financial-intelligence-hub/.
8. Step name: Log: SEC Called. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-sec-called.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
9. Step name: Log: Patent Called. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-patent-called.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
10. Step name: Aggregate Results. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__aggregate-results.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
11. Step name: Log: Results Aggregated. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-results-aggregated.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
12. Step name: LLM Chain Analyst. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__llm-chain-analyst.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
13. Step name: Ollama Analyst Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__ollama-analyst-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
14. Step name: Log: Analysis Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-analysis-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
15. Step name: Format Chat Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__format-chat-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
16. Step name: Log: Complete. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-complete.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
17. Step name: No Tools Needed. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__no-tools-needed.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
18. Step name: Structured Output Parser. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__structured-output-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
19. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-intelligence-hub__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
20. Step name: Extract from File. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__extract-from-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-financial-intelligence-hub/.
21. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-intelligence-hub__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroft-financial-intelligence-hub-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroft-financial-intelligence-hub-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Financial Intelligence Hub` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-financial-intelligence-hub --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-financial-intelligence-hub --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Initialize Hub | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step initialize-hub` |  |
| Initialize Logging | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step initialize-logging` |  |
| LLM Chain Router | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step llm-chain-router` |  |
| Ollama Chat Model | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step ollama-chat-model` |  |
| Call SEC Workflow | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step call-sec-workflow` | `--sample` |
| Call Patent Workflow | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step call-patent-workflow` | `--sample` |
| Log: SEC Called | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step log-sec-called` |  |
| Log: Patent Called | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step log-patent-called` |  |
| Aggregate Results | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step aggregate-results` |  |
| Log: Results Aggregated | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step log-results-aggregated` |  |
| LLM Chain Analyst | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step llm-chain-analyst` |  |
| Ollama Analyst Model | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step ollama-analyst-model` |  |
| Log: Analysis Complete | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step log-analysis-complete` |  |
| Format Chat Response | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step format-chat-response` |  |
| Log: Complete | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step log-complete` |  |
| No Tools Needed | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step no-tools-needed` |  |
| Structured Output Parser | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step structured-output-parser` |  |
| Read/Write Files from Disk | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step read-write-files-from-disk` | `--no-write` |
| Extract from File | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step extract-from-file` |  |
| Produce human report | `snickerdoodle run n8n-mycroft-financial-intelligence-hub --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroft-financial-intelligence-hub --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroft-financial-intelligence-hub --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroft-financial-intelligence-hub --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Initialize Hub | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__initialize-hub.py` | gigo |
| Initialize Logging | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__initialize-logging.py` | gigo |
| LLM Chain Router | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__llm-chain-router.py` | gigo |
| Ollama Chat Model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__ollama-chat-model.py` | gigo |
| Call SEC Workflow | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-intelligence-hub__call-sec-workflow.py` | ingest |
| Call Patent Workflow | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-financial-intelligence-hub__call-patent-workflow.py` | ingest |
| Log: SEC Called | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-sec-called.py` | gigo |
| Log: Patent Called | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-patent-called.py` | gigo |
| Aggregate Results | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__aggregate-results.py` | gigo |
| Log: Results Aggregated | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-results-aggregated.py` | gigo |
| LLM Chain Analyst | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__llm-chain-analyst.py` | gigo |
| Ollama Analyst Model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__ollama-analyst-model.py` | gigo |
| Log: Analysis Complete | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-analysis-complete.py` | gigo |
| Format Chat Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__format-chat-response.py` | gigo |
| Log: Complete | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__log-complete.py` | gigo |
| No Tools Needed | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__no-tools-needed.py` | gigo |
| Structured Output Parser | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__structured-output-parser.py` | gigo |
| Read/Write Files from Disk | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-intelligence-hub__read-write-files-from-disk.py` | tool |
| Extract from File | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-financial-intelligence-hub__extract-from-file.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-financial-intelligence-hub__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-financial-intelligence-hub/` | JSON |
| Verified data | `data/verified/n8n-mycroft-financial-intelligence-hub/` | JSON |
| Agent log | `logs/n8n-mycroft-financial-intelligence-hub-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-financial-intelligence-hub-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json`

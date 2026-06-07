# Portfolio Intelligence Agent - Complete with RAG

## Purpose

Portfolio Intelligence Agent - Complete with RAG defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to portfolio intelligence agent - complete with rag. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Schedule Trigger | `scheduleTrigger` | conductor |
| Read Holdings File | `readBinaryFile` | tool |
| Parse JSON Holdings | `code` | gigo |
| Calculate Portfolio Metrics | `code` | tool |
| Read Previous Summaries | `readBinaryFile` | tool |
| Fetch & Extract Stock Prices | `code` | conductor |
| Parse Summaries CSV | `code` | gigo |
| Calculate Daily Return | `code` | report |
| Read Knowledge Base1 | `readWriteFile` | tool |
| Parse Knowledge Base CSV | `code` | gigo |
| Read Portfolio History CSV | `readWriteFile` | tool |
| Parse Portfolio History Data | `code` | gigo |
| Build Portfolio Analysis | `code` | tool |
| RAG-Retrieve Context | `code` | conductor |
| Extract AI Summary | `code` | conductor |
| Split Out | `splitOut` | gigo |
| Generate AI Summary (Groq) | `httpRequest` | tool |
| Send a message | `gmail` | tool |
| Append Portfolio History1 | `readWriteFile` | tool |
| Convert Holdings to CSV | `convertToFile` | gigo |
| Convert Summary to CSV | `convertToFile` | gigo |
| Append Daily Summary | `readWriteFile` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (7 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (10 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (5 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/portfolio-intelligence-agent-complete-with-rag.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/portfolio-intelligence-agent-complete-with-rag data/verified/portfolio-intelligence-agent-complete-with-rag -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/portfolio-intelligence-agent-complete-with-rag.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Read Holdings File. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-holdings-file.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Parse JSON Holdings. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-json-holdings.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
4. Step name: Calculate Portfolio Metrics. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__calculate-portfolio-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Read Previous Summaries. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-previous-summaries.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Parse Summaries CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-summaries-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
7. Step name: Calculate Daily Return. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/portfolio-intelligence-agent-complete-with-rag__calculate-daily-return.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
8. Step name: Read Knowledge Base1. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-knowledge-base1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Parse Knowledge Base CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-knowledge-base-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
10. Step name: Read Portfolio History CSV. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-portfolio-history-csv.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Parse Portfolio History Data. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-portfolio-history-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
12. Step name: Build Portfolio Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__build-portfolio-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Split Out. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__split-out.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
14. Step name: Generate AI Summary (Groq). Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__generate-ai-summary-groq.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Send a message. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__send-a-message.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Append Portfolio History1. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__append-portfolio-history1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Convert Holdings to CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__convert-holdings-to-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
18. Step name: Convert Summary to CSV. Labor: AI with Human gate.
   Script called: `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__convert-summary-to-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/portfolio-intelligence-agent-complete-with-rag/.
19. Step name: Append Daily Summary. Labor: AI with Human gate.
   Script called: `scripts/tools/portfolio-intelligence-agent-complete-with-rag__append-daily-summary.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
20. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/portfolio-intelligence-agent-complete-with-rag__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/portfolio-intelligence-agent-complete-with-rag-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/portfolio-intelligence-agent-complete-with-rag-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Portfolio Intelligence Agent - Complete with RAG` run.
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
`snickerdoodle run portfolio-intelligence-agent-complete-with-rag --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run portfolio-intelligence-agent-complete-with-rag --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Read Holdings File | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step read-holdings-file` | `--no-write` |
| Parse JSON Holdings | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step parse-json-holdings` |  |
| Calculate Portfolio Metrics | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step calculate-portfolio-metrics` | `--no-write` |
| Read Previous Summaries | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step read-previous-summaries` | `--no-write` |
| Parse Summaries CSV | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step parse-summaries-csv` |  |
| Calculate Daily Return | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step calculate-daily-return` | `--no-write` |
| Read Knowledge Base1 | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step read-knowledge-base1` | `--no-write` |
| Parse Knowledge Base CSV | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step parse-knowledge-base-csv` |  |
| Read Portfolio History CSV | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step read-portfolio-history-csv` | `--no-write` |
| Parse Portfolio History Data | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step parse-portfolio-history-data` |  |
| Build Portfolio Analysis | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step build-portfolio-analysis` | `--no-write` |
| Split Out | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step split-out` |  |
| Generate AI Summary (Groq) | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step generate-ai-summary-groq` | `--no-write` |
| Send a message | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step send-a-message` | `--no-write` |
| Append Portfolio History1 | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step append-portfolio-history1` | `--no-write` |
| Convert Holdings to CSV | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step convert-holdings-to-csv` |  |
| Convert Summary to CSV | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step convert-summary-to-csv` |  |
| Append Daily Summary | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step append-daily-summary` | `--no-write` |
| Produce human report | `snickerdoodle run portfolio-intelligence-agent-complete-with-rag --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate portfolio-intelligence-agent-complete-with-rag --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Read Holdings File | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-holdings-file.py` | tool |
| Parse JSON Holdings | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-json-holdings.py` | gigo |
| Calculate Portfolio Metrics | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__calculate-portfolio-metrics.py` | tool |
| Read Previous Summaries | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-previous-summaries.py` | tool |
| Parse Summaries CSV | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-summaries-csv.py` | gigo |
| Calculate Daily Return | `[TODO: DEV] Create or map script path: scripts/tools/portfolio-intelligence-agent-complete-with-rag__calculate-daily-return.py` | tool |
| Read Knowledge Base1 | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-knowledge-base1.py` | tool |
| Parse Knowledge Base CSV | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-knowledge-base-csv.py` | gigo |
| Read Portfolio History CSV | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__read-portfolio-history-csv.py` | tool |
| Parse Portfolio History Data | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__parse-portfolio-history-data.py` | gigo |
| Build Portfolio Analysis | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__build-portfolio-analysis.py` | tool |
| Split Out | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__split-out.py` | gigo |
| Generate AI Summary (Groq) | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__generate-ai-summary-groq.py` | tool |
| Send a message | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__send-a-message.py` | tool |
| Append Portfolio History1 | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__append-portfolio-history1.py` | tool |
| Convert Holdings to CSV | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__convert-holdings-to-csv.py` | gigo |
| Convert Summary to CSV | `scripts/gigo/portfolio-intelligence-agent-complete-with-rag__convert-summary-to-csv.py` | gigo |
| Append Daily Summary | `scripts/tools/portfolio-intelligence-agent-complete-with-rag__append-daily-summary.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/portfolio-intelligence-agent-complete-with-rag__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/portfolio-intelligence-agent-complete-with-rag/` | JSON |
| Verified data | `data/verified/portfolio-intelligence-agent-complete-with-rag/` | JSON |
| Agent log | `logs/portfolio-intelligence-agent-complete-with-rag-[DATE].json` | JSON |
| Human report | `reports/generated/portfolio-intelligence-agent-complete-with-rag-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json`

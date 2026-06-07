# Portfolio Intelligence Agent - Complete with RAG

## Purpose

Portfolio Intelligence Agent - Complete with RAG defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to portfolio intelligence agent - complete with rag. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Read Holdings File | readBinaryFile | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Read Previous Summaries | readBinaryFile | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch & Extract Stock Prices | code | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Generate AI Summary (Groq) | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | manualTrigger | conductor |
| Schedule Trigger | scheduleTrigger | conductor |
| Read Holdings File | readBinaryFile | ingest |
| Parse JSON Holdings | code | gigo |
| Calculate Portfolio Metrics | code | gigo |
| Read Previous Summaries | readBinaryFile | ingest |
| Fetch & Extract Stock Prices | code | ingest |
| Parse Summaries CSV | code | gigo |
| Calculate Daily Return | code | gigo |
| Read Knowledge Base1 | readWriteFile | tool |
| Parse Knowledge Base CSV | code | gigo |
| Read Portfolio History CSV | readWriteFile | tool |
| Parse Portfolio History Data | code | gigo |
| Build Portfolio Analysis | code | gigo |
| RAG-Retrieve Context | code | gigo |
| Extract AI Summary | code | gigo |
| Split Out | splitOut | conductor |
| Generate AI Summary (Groq) | httpRequest | ingest |
| Send a message | gmail | tool |
| Append Portfolio History1 | readWriteFile | tool |
| Convert Holdings to CSV | convertToFile | gigo |
| Convert Summary to CSV | convertToFile | gigo |
| Append Daily Summary | readWriteFile | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-portfolio-intelligence-agent-complete-with-rag.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-portfolio-intelligence-agent-complete-with-rag data/verified/n8n-portfolio-intelligence-agent-complete-with-rag -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-portfolio-intelligence-agent-complete-with-rag.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Read Holdings File. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__read-holdings-file.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-portfolio-intelligence-agent-complete-with-rag/.
3. Step name: Parse JSON Holdings. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-json-holdings.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
4. Step name: Calculate Portfolio Metrics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__calculate-portfolio-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
5. Step name: Read Previous Summaries. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__read-previous-summaries.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-portfolio-intelligence-agent-complete-with-rag/.
6. Step name: Fetch & Extract Stock Prices. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__fetch-and-extract-stock-prices.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-portfolio-intelligence-agent-complete-with-rag/.
7. Step name: Parse Summaries CSV. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-summaries-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
8. Step name: Calculate Daily Return. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__calculate-daily-return.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
9. Step name: Read Knowledge Base1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__read-knowledge-base1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Parse Knowledge Base CSV. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-knowledge-base-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
11. Step name: Read Portfolio History CSV. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__read-portfolio-history-csv.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Parse Portfolio History Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-portfolio-history-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
13. Step name: Build Portfolio Analysis. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__build-portfolio-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
14. Step name: RAG-Retrieve Context. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__rag-retrieve-context.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
15. Step name: Extract AI Summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__extract-ai-summary.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
16. Step name: Generate AI Summary (Groq). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__generate-ai-summary-groq.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-portfolio-intelligence-agent-complete-with-rag/.
17. Step name: Send a message. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__send-a-message.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
18. Step name: Append Portfolio History1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__append-portfolio-history1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
19. Step name: Convert Holdings to CSV. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__convert-holdings-to-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
20. Step name: Convert Summary to CSV. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__convert-summary-to-csv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/.
21. Step name: Append Daily Summary. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__append-daily-summary.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
22. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-portfolio-intelligence-agent-complete-with-rag-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-portfolio-intelligence-agent-complete-with-rag-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Portfolio Intelligence Agent - Complete with RAG` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Read Holdings File | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step read-holdings-file` | `--sample` |
| Parse JSON Holdings | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step parse-json-holdings` |  |
| Calculate Portfolio Metrics | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step calculate-portfolio-metrics` |  |
| Read Previous Summaries | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step read-previous-summaries` | `--sample` |
| Fetch & Extract Stock Prices | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step fetch-and-extract-stock-prices` | `--sample` |
| Parse Summaries CSV | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step parse-summaries-csv` |  |
| Calculate Daily Return | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step calculate-daily-return` |  |
| Read Knowledge Base1 | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step read-knowledge-base1` | `--no-write` |
| Parse Knowledge Base CSV | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step parse-knowledge-base-csv` |  |
| Read Portfolio History CSV | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step read-portfolio-history-csv` | `--no-write` |
| Parse Portfolio History Data | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step parse-portfolio-history-data` |  |
| Build Portfolio Analysis | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step build-portfolio-analysis` |  |
| RAG-Retrieve Context | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step rag-retrieve-context` |  |
| Extract AI Summary | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step extract-ai-summary` |  |
| Generate AI Summary (Groq) | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step generate-ai-summary-groq` | `--sample` |
| Send a message | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step send-a-message` | `--no-write` |
| Append Portfolio History1 | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step append-portfolio-history1` | `--no-write` |
| Convert Holdings to CSV | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step convert-holdings-to-csv` |  |
| Convert Summary to CSV | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step convert-summary-to-csv` |  |
| Append Daily Summary | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step append-daily-summary` | `--no-write` |
| Produce human report | `snickerdoodle run n8n-portfolio-intelligence-agent-complete-with-rag --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-portfolio-intelligence-agent-complete-with-rag --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-portfolio-intelligence-agent-complete-with-rag --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-portfolio-intelligence-agent-complete-with-rag --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Read Holdings File | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__read-holdings-file.py` | ingest |
| Parse JSON Holdings | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-json-holdings.py` | gigo |
| Calculate Portfolio Metrics | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__calculate-portfolio-metrics.py` | gigo |
| Read Previous Summaries | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__read-previous-summaries.py` | ingest |
| Fetch & Extract Stock Prices | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__fetch-and-extract-stock-prices.py` | ingest |
| Parse Summaries CSV | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-summaries-csv.py` | gigo |
| Calculate Daily Return | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__calculate-daily-return.py` | gigo |
| Read Knowledge Base1 | `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__read-knowledge-base1.py` | tool |
| Parse Knowledge Base CSV | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-knowledge-base-csv.py` | gigo |
| Read Portfolio History CSV | `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__read-portfolio-history-csv.py` | tool |
| Parse Portfolio History Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__parse-portfolio-history-data.py` | gigo |
| Build Portfolio Analysis | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__build-portfolio-analysis.py` | gigo |
| RAG-Retrieve Context | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__rag-retrieve-context.py` | gigo |
| Extract AI Summary | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__extract-ai-summary.py` | gigo |
| Generate AI Summary (Groq) | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-portfolio-intelligence-agent-complete-with-rag__generate-ai-summary-groq.py` | ingest |
| Send a message | `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__send-a-message.py` | tool |
| Append Portfolio History1 | `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__append-portfolio-history1.py` | tool |
| Convert Holdings to CSV | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__convert-holdings-to-csv.py` | gigo |
| Convert Summary to CSV | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-portfolio-intelligence-agent-complete-with-rag__convert-summary-to-csv.py` | gigo |
| Append Daily Summary | `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__append-daily-summary.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-portfolio-intelligence-agent-complete-with-rag__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-portfolio-intelligence-agent-complete-with-rag/` | JSON |
| Verified data | `data/verified/n8n-portfolio-intelligence-agent-complete-with-rag/` | JSON |
| Agent log | `logs/n8n-portfolio-intelligence-agent-complete-with-rag-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-portfolio-intelligence-agent-complete-with-rag-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Portfolio_Intelligence_Agent/Portfolio Intelligence Agent - Complete with RAG.json`

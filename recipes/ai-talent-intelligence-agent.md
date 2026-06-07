# AI Talent Intelligence Agent

## Purpose

The AI Talent Intelligence Agent tracks research papers, hiring or appointment news, and known researcher records to surface AI talent movement signals that may matter for competitive intelligence, while clearly separating real source data from prototype/mock records.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| ArXiv AI/ML/NLP papers | XML/API response | ArXiv API or `data/raw/ai-talent-intelligence-agent/` | Confirm source is allowed, current, and rate-safe before live fetch. |
| AI researcher news | JSON | Serper News API or local export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Researcher database rows | JSON/table | Local mock rows or approved database export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Significance threshold | Integer | Recipe default, `5` | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json` | Yes |
| ArXiv AI/ML/NLP papers | XML/API response | ArXiv API or `data/raw/ai-talent-intelligence-agent/` | Yes |
| AI researcher news | JSON | Serper News API or local export | Yes |
| Researcher database rows | JSON/table | Local mock rows or approved database export | No |
| Significance threshold | Integer | Recipe default, `5` | Yes |
| Groq credential | Environment variable | `GROQ_API_KEY` for future live LLM adapter | No |
| Serper credential | Environment variable | `SERPER_API_KEY` for live news search | No |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/ai-talent-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run ai-talent-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/ai-talent-intelligence-agent data/verified/ai-talent-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/ai-talent-intelligence-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: fetch_ai_talent_arxiv. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_ai_talent_arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-talent-intelligence-agent/.
3. Step name: fetch_ai_talent_news. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_ai_talent_news.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-talent-intelligence-agent/.
4. Step name: load_mock_researchers. Labor: AI with Human gate.
   Script called: `scripts/ingest/load_mock_researchers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-talent-intelligence-agent/.
5. Step name: parse_ai_talent_arxiv. Labor: AI with Human gate.
   Script called: `scripts/gigo/parse_ai_talent_arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-talent-intelligence-agent/.
6. Step name: analyze_ai_talent_signal. Labor: AI with Human gate.
   Script called: `scripts/tools/analyze_ai_talent_signal.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: filter_high_significance. Labor: AI with Human gate.
   Script called: `scripts/gigo/filter_high_significance.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-talent-intelligence-agent/.
8. Step name: aggregate_ai_talent_statistics. Labor: AI with Human gate.
   Script called: `scripts/tools/aggregate_ai_talent_statistics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: generate_ai_talent_report. Labor: AI with Human gate.
   Script called: `scripts/tools/generate_ai_talent_report.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: prepare_ai_talent_database_payload. Labor: AI with Human gate.
   Script called: `scripts/gigo/prepare_ai_talent_database_payload.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-talent-intelligence-agent/.
11. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/ai-talent-intelligence-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/ai-talent-intelligence-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/ai-talent-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `AI Talent Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if both ArXiv and news inputs are missing.
- Stop if live Serper, Groq, database, or SMTP access is needed but credentials and human approval are absent.
- Stop if mock researcher records are mixed with real signals without an explicit caveat.
- Stop if no records pass the high-significance gate.
- Stop before saving to a live database or sending email.
- Stop if the report implies investment advice without human interpretation and source review.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run ai-talent-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run ai-talent-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| fetch_ai_talent_arxiv | `snickerdoodle run ai-talent-intelligence-agent --step fetch-ai-talent-arxiv` | `--sample` |
| fetch_ai_talent_news | `snickerdoodle run ai-talent-intelligence-agent --step fetch-ai-talent-news` | `--sample` |
| load_mock_researchers | `snickerdoodle run ai-talent-intelligence-agent --step load-mock-researchers` | `--sample` |
| parse_ai_talent_arxiv | `snickerdoodle run ai-talent-intelligence-agent --step parse-ai-talent-arxiv` |  |
| analyze_ai_talent_signal | `snickerdoodle run ai-talent-intelligence-agent --step analyze-ai-talent-signal` | `--no-write` |
| filter_high_significance | `snickerdoodle run ai-talent-intelligence-agent --step filter-high-significance` |  |
| aggregate_ai_talent_statistics | `snickerdoodle run ai-talent-intelligence-agent --step aggregate-ai-talent-statistics` | `--no-write` |
| generate_ai_talent_report | `snickerdoodle run ai-talent-intelligence-agent --step generate-ai-talent-report` | `--no-write` |
| prepare_ai_talent_database_payload | `snickerdoodle run ai-talent-intelligence-agent --step prepare-ai-talent-database-payload` |  |
| Produce human report | `snickerdoodle run ai-talent-intelligence-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate ai-talent-intelligence-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate ai-talent-intelligence-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate ai-talent-intelligence-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| fetch_ai_talent_arxiv | `scripts/ingest/fetch_ai_talent_arxiv.py` | ingest |
| fetch_ai_talent_news | `scripts/ingest/fetch_ai_talent_news.py` | ingest |
| load_mock_researchers | `scripts/ingest/load_mock_researchers.py` | ingest |
| parse_ai_talent_arxiv | `scripts/gigo/parse_ai_talent_arxiv.py` | gigo |
| analyze_ai_talent_signal | `scripts/tools/analyze_ai_talent_signal.py` | tool |
| filter_high_significance | `scripts/gigo/filter_high_significance.py` | gigo |
| aggregate_ai_talent_statistics | `scripts/tools/aggregate_ai_talent_statistics.py` | tool |
| generate_ai_talent_report | `scripts/tools/generate_ai_talent_report.py` | tool |
| prepare_ai_talent_database_payload | `scripts/gigo/prepare_ai_talent_database_payload.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/ai-talent-intelligence-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/ai-talent-intelligence-agent/` | JSON |
| Verified data | `data/verified/ai-talent-intelligence-agent/` | JSON |
| Agent log | `logs/ai-talent-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/ai-talent-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json`

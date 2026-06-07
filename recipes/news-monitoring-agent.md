# News Monitoring Agent

## Purpose

The News Monitoring Agent answers whether recent AI and technology news contains decision-relevant signals for financial research by collecting feed articles, cleaning and deduplicating them, attaching sentiment and retrieval metadata, indexing them into auditable local stores, and answering analyst questions only from the resulting source-grounded corpus.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Feed source list | Table/JSON | n8n sources data table or `data/verified/news-monitoring-agent/sources.json` | Confirm source is allowed, current, and rate-safe before live fetch. |
| Feed URL | URL string | Each source row | Confirm source is allowed, current, and rate-safe before live fetch. |
| Previous feed timestamp | ISO datetime/string | Source-state table or verified source metadata | Confirm source is allowed, current, and rate-safe before live fetch. |
| Article payload | JSON | `data/raw/news-monitoring-agent/` | Confirm source is allowed, current, and rate-safe before live fetch. |
| Analyst question | String | Chat/manual trigger | Confirm source is allowed, current, and rate-safe before live fetch. |
| RAG evaluation questions | CSV | `data/verified/news-monitoring-agent/questions.csv` | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json` | Yes |
| Feed source list | Table/JSON | n8n sources data table or `data/verified/news-monitoring-agent/sources.json` | Yes |
| Feed URL | URL string | Each source row | Yes |
| Previous feed timestamp | ISO datetime/string | Source-state table or verified source metadata | No |
| Article payload | JSON | `data/raw/news-monitoring-agent/` | Yes |
| Analyst question | String | Chat/manual trigger | Yes |
| RAG evaluation questions | CSV | `data/verified/news-monitoring-agent/questions.csv` | No |
| Model credentials | Environment variables | `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `HUGGINGFACE_API_KEY`, `QDRANT_API_KEY` for future live adapters | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/news-monitoring-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run news-monitoring-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/news-monitoring-agent data/verified/news-monitoring-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/news-monitoring-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: feedparser_fetch. Labor: AI with Human gate.
   Script called: `scripts/ingest/feedparser_fetch.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/news-monitoring-agent/.
3. Step name: split_articles. Labor: AI with Human gate.
   Script called: `scripts/gigo/split_articles.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
4. Step name: filter_not_null. Labor: AI with Human gate.
   Script called: `scripts/gigo/filter_not_null.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
5. Step name: upsert_source_state. Labor: AI with Human gate.
   Script called: `scripts/gigo/upsert_source_state.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
6. Step name: finbert_sentiment. Labor: AI with Human gate.
   Script called: `scripts/tools/finbert_sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: load_documents_a. Labor: AI with Human gate.
   Script called: `scripts/gigo/load_documents_a.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
8. Step name: qdrant_insert_collection. Labor: AI with Human gate.
   Script called: `scripts/tools/qdrant_insert_collection.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: query_refinement_agent. Labor: AI with Human gate.
   Script called: `scripts/tools/query_refinement_agent.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: qdrant_retrieve. Labor: AI with Human gate.
   Script called: `scripts/tools/qdrant_retrieve.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: extract_questions_from_file. Labor: AI with Human gate.
   Script called: `scripts/gigo/extract_questions_from_file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/news-monitoring-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/news-monitoring-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/news-monitoring-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `News Monitoring Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if source rows are missing feed URLs or contain credentials.
- Stop if a feed fetch fails for all sources.
- Stop if parsed article count is zero after the GIGO gate.
- Stop if deduplication removes more records than expected and no explanation is logged.
- Stop if sentiment labels are treated as investment advice rather than weak evidence tags.
- Stop if retrieval answers omit source URLs or publication dates.
- Stop if live Gemini, OpenRouter, Hugging Face, Postgres, or Qdrant calls are required but credentials and human approval are absent.
- Stop before publishing, emailing, trading, or alerting based on the output.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run news-monitoring-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run news-monitoring-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| feedparser_fetch | `snickerdoodle run news-monitoring-agent --step feedparser-fetch` | `--sample` |
| split_articles | `snickerdoodle run news-monitoring-agent --step split-articles` |  |
| filter_not_null | `snickerdoodle run news-monitoring-agent --step filter-not-null` |  |
| upsert_source_state | `snickerdoodle run news-monitoring-agent --step upsert-source-state` |  |
| finbert_sentiment | `snickerdoodle run news-monitoring-agent --step finbert-sentiment` | `--no-write` |
| load_documents_a | `snickerdoodle run news-monitoring-agent --step load-documents-a` |  |
| qdrant_insert_collection | `snickerdoodle run news-monitoring-agent --step qdrant-insert-collection` | `--no-write` |
| query_refinement_agent | `snickerdoodle run news-monitoring-agent --step query-refinement-agent` | `--no-write` |
| qdrant_retrieve | `snickerdoodle run news-monitoring-agent --step qdrant-retrieve` | `--no-write` |
| extract_questions_from_file | `snickerdoodle run news-monitoring-agent --step extract-questions-from-file` |  |
| Produce human report | `snickerdoodle run news-monitoring-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate news-monitoring-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate news-monitoring-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate news-monitoring-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| feedparser_fetch | `scripts/ingest/feedparser_fetch.py` | ingest |
| split_articles | `scripts/gigo/split_articles.py` | gigo |
| filter_not_null | `scripts/gigo/filter_not_null.py` | gigo |
| upsert_source_state | `scripts/gigo/upsert_source_state.py` | gigo |
| finbert_sentiment | `scripts/tools/finbert_sentiment.py` | tool |
| load_documents_a | `scripts/gigo/load_documents_a.py` | gigo |
| qdrant_insert_collection | `scripts/tools/qdrant_insert_collection.py` | tool |
| query_refinement_agent | `scripts/tools/query_refinement_agent.py` | tool |
| qdrant_retrieve | `scripts/tools/qdrant_retrieve.py` | tool |
| extract_questions_from_file | `scripts/gigo/extract_questions_from_file.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/news-monitoring-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/news-monitoring-agent/` | JSON |
| Verified data | `data/verified/news-monitoring-agent/` | JSON |
| Agent log | `logs/news-monitoring-agent-[DATE].json` | JSON |
| Human report | `reports/generated/news-monitoring-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json`

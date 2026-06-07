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

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/news-monitoring-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/news-monitoring-agent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/news-monitoring-agent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/news-monitoring-agent data/verified/news-monitoring-agent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/news-monitoring-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/news-monitoring-agent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/news-monitoring-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/news-monitoring-agent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/news-monitoring-agent-[DATE].json && test -f reports/generated/news-monitoring-agent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/news-monitoring-agent-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `news-monitoring-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/news-monitoring-agent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `news-monitoring-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/news-monitoring-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/news-monitoring-agent-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `news-monitoring-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/news-monitoring-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/news-monitoring-agent-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `news-monitoring-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/news-monitoring-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/news-monitoring-agent-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `news-monitoring-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/news-monitoring-agent-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `news-monitoring-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/news-monitoring-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/news-monitoring-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `News Monitoring Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

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
| Verify provenance | `snickerdoodle run news-monitoring-agent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run news-monitoring-agent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run news-monitoring-agent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run news-monitoring-agent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run news-monitoring-agent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run news-monitoring-agent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate news-monitoring-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate news-monitoring-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate news-monitoring-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate news-monitoring-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate news-monitoring-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate news-monitoring-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/news-monitoring-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/news-monitoring-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/news-monitoring-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/news-monitoring-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/news-monitoring-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/news-monitoring-agent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/news-monitoring-agent/` | JSON |
| Verified data | `data/verified/news-monitoring-agent/` | JSON |
| Agent log | `logs/news-monitoring-agent-[DATE].json` | JSON |
| Human report | `reports/generated/news-monitoring-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json"` | Referenced source/evidence path from prior recipe text. |
| `data/verified/news-monitoring-agent/questions.csv` | `test -f "data/verified/news-monitoring-agent/questions.csv"` | Referenced source/evidence path from prior recipe text. |
| `data/verified/news-monitoring-agent/sources.json` | `test -f "data/verified/news-monitoring-agent/sources.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

The News Monitoring Agent answers whether recent AI and technology news contains decision-relevant signals for financial research by collecting feed articles, cleaning and deduplicating them, attaching sentiment and retrieval metadata, indexing them into auditable local stores, and answering analyst questions only from the resulting source-grounded corpus.

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

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: feedparser_fetch. Labor: AI with Human gate.
   Script called: `scripts/ingest/feedparser-fetch.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/news-monitoring-agent/.
3. Step name: split_articles. Labor: AI with Human gate.
   Script called: `scripts/gigo/split-articles.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
4. Step name: filter_not_null. Labor: AI with Human gate.
   Script called: `scripts/gigo/filter-not-null.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
5. Step name: upsert_source_state. Labor: AI with Human gate.
   Script called: `scripts/gigo/upsert-source-state.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
6. Step name: finbert_sentiment. Labor: AI with Human gate.
   Script called: `scripts/tools/finbert-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: load_documents_a. Labor: AI with Human gate.
   Script called: `scripts/gigo/load-documents-a.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
8. Step name: qdrant_insert_collection. Labor: AI with Human gate.
   Script called: `scripts/tools/qdrant-insert-collection.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: query_refinement_agent. Labor: AI with Human gate.
   Script called: `scripts/tools/query-refinement-agent.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: qdrant_retrieve. Labor: AI with Human gate.
   Script called: `scripts/tools/qdrant-retrieve.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: extract_questions_from_file. Labor: AI with Human gate.
   Script called: `scripts/gigo/extract-questions-from-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/news-monitoring-agent/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/news-monitoring-agent-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

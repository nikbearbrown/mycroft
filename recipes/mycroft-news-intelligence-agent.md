# Mycroft News Intelligence Agent

## Purpose

The Mycroft News Intelligence Agent monitors AI and technology companies across NewsAPI and Google News RSS, normalizes article text, estimates sentiment-driven risk, prepares financial-intelligence records, and generates alerts for human review before any database or email side effects occur.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Company list | JSON | `scripts/gigo/mycroft-company-list.py` | Confirm source is allowed, current, and rate-safe before live fetch. |
| NewsAPI query payloads | JSON | `scripts/gigo/build-mycroft-news-queries.py` | Confirm source is allowed, current, and rate-safe before live fetch. |
| NewsAPI results | JSON | NewsAPI or local export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Google News RSS | XML/text | Google News RSS or local export | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json` | Yes |
| Company list | JSON | `scripts/gigo/mycroft-company-list.py` | Yes |
| NewsAPI query payloads | JSON | `scripts/gigo/build-mycroft-news-queries.py` | Yes |
| NewsAPI results | JSON | NewsAPI or local export | Yes |
| Google News RSS | XML/text | Google News RSS or local export | No |
| NewsAPI credential | Environment variable | `NEWSAPI_KEY` | No |
| Hugging Face credential | Environment variable | `HUGGINGFACE_API_TOKEN` for future live FinBERT adapter | No |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/mycroft-news-intelligence-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/mycroft-news-intelligence-agent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/mycroft-news-intelligence-agent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/mycroft-news-intelligence-agent data/verified/mycroft-news-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/mycroft-news-intelligence-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/mycroft-news-intelligence-agent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/mycroft-news-intelligence-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/mycroft-news-intelligence-agent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/mycroft-news-intelligence-agent-[DATE].json && test -f reports/generated/mycroft-news-intelligence-agent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-news-intelligence-agent-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-news-intelligence-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/mycroft-news-intelligence-agent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-news-intelligence-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/mycroft-news-intelligence-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-news-intelligence-agent-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-news-intelligence-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/mycroft-news-intelligence-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-news-intelligence-agent-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-news-intelligence-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/mycroft-news-intelligence-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-news-intelligence-agent-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-news-intelligence-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-news-intelligence-agent-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `mycroft-news-intelligence-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/mycroft-news-intelligence-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/mycroft-news-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft News Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if placeholder secrets or placeholder emails appear in generated artifacts.
- Stop if neither NewsAPI nor local news exports are available.
- Stop if normalized articles lack title or processed text.
- Stop if risk records lack a risk score or risk level.
- Stop before live Hugging Face calls without `HUGGINGFACE_API_TOKEN` and approval.
- Stop before database inserts or email sends without explicit approval.
- Stop if risk labels are treated as investment advice without human interpretation.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run mycroft-news-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-news-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run mycroft-news-intelligence-agent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run mycroft-news-intelligence-agent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run mycroft-news-intelligence-agent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run mycroft-news-intelligence-agent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run mycroft-news-intelligence-agent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run mycroft-news-intelligence-agent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate mycroft-news-intelligence-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate mycroft-news-intelligence-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate mycroft-news-intelligence-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate mycroft-news-intelligence-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate mycroft-news-intelligence-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate mycroft-news-intelligence-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/mycroft-news-intelligence-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/mycroft-news-intelligence-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/mycroft-news-intelligence-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/mycroft-news-intelligence-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/mycroft-news-intelligence-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/mycroft-news-intelligence-agent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-news-intelligence-agent/` | JSON |
| Verified data | `data/verified/mycroft-news-intelligence-agent/` | JSON |
| Agent log | `logs/mycroft-news-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-news-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

The Mycroft News Intelligence Agent monitors AI and technology companies across NewsAPI and Google News RSS, normalizes article text, estimates sentiment-driven risk, prepares financial-intelligence records, and generates alerts for human review before any database or email side effects occur.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-news-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-news-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-news-intelligence-agent data/verified/mycroft-news-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-news-intelligence-agent.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: mycroft_company_list. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-company-list.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
3. Step name: build_mycroft_news_queries. Labor: AI with Human gate.
   Script called: `scripts/gigo/build-mycroft-news-queries.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
4. Step name: fetch_mycroft_newsapi. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-mycroft-newsapi.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroft-news-intelligence-agent/.
5. Step name: normalize_mycroft_newsapi. Labor: AI with Human gate.
   Script called: `scripts/gigo/normalize-mycroft-newsapi.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
6. Step name: mycroft_finbert_sentiment_spec. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-finbert-sentiment-spec.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: mycroft_risk_calculator. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-risk-calculator.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: prepare_mycroft_financial_intelligence_rows. Labor: AI with Human gate.
   Script called: `scripts/gigo/prepare-mycroft-financial-intelligence-rows.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
9. Step name: mycroft_alert_generator. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-alert-generator.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

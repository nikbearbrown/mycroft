# AI News & Sentiment Agent

## Purpose

The AI News & Sentiment Agent monitors a small set of AI-related news articles, labels headline sentiment, records review-ready article payloads, and flags negative items for human attention without automatically writing to Airtable or sending email.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ticker/query config | JSON | Recipe default: ticker `AI`, query `nvidia` | Confirm source is allowed, current, and rate-safe before live fetch. |
| News articles | JSON | NewsAPI live call or `data/raw/ai-news-sentiment-agent/` | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json` | Yes |
| Ticker/query config | JSON | Recipe default: ticker `AI`, query `nvidia` | Yes |
| News articles | JSON | NewsAPI live call or `data/raw/ai-news-sentiment-agent/` | Yes |
| NewsAPI credential | Environment variable | `NEWSAPI_KEY` | No |
| Airtable destination | Environment/config | Human-approved Airtable base/table | No |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/ai-news-sentiment-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/ai-news-sentiment-agent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/ai-news-sentiment-agent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/ai-news-sentiment-agent data/verified/ai-news-sentiment-agent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/ai-news-sentiment-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/ai-news-sentiment-agent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/ai-news-sentiment-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/ai-news-sentiment-agent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/ai-news-sentiment-agent-[DATE].json && test -f reports/generated/ai-news-sentiment-agent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/ai-news-sentiment-agent-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-news-sentiment-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/ai-news-sentiment-agent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-news-sentiment-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/ai-news-sentiment-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/ai-news-sentiment-agent-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-news-sentiment-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/ai-news-sentiment-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/ai-news-sentiment-agent-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-news-sentiment-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/ai-news-sentiment-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/ai-news-sentiment-agent-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-news-sentiment-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/ai-news-sentiment-agent-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-news-sentiment-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/ai-news-sentiment-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/ai-news-sentiment-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `AI News & Sentiment Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if the original hardcoded API key or personal emails appear in new generated artifacts.
- Stop if no NewsAPI key and no local article export are available.
- Stop if article records lack titles or URLs.
- Stop before writing to Airtable without explicit approval.
- Stop before sending email without explicit approval and SMTP configuration.
- Stop if sentiment labels are used as financial advice without human review.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run ai-news-sentiment-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run ai-news-sentiment-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run ai-news-sentiment-agent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run ai-news-sentiment-agent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run ai-news-sentiment-agent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run ai-news-sentiment-agent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run ai-news-sentiment-agent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run ai-news-sentiment-agent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate ai-news-sentiment-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate ai-news-sentiment-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate ai-news-sentiment-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate ai-news-sentiment-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate ai-news-sentiment-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate ai-news-sentiment-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/ai-news-sentiment-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/ai-news-sentiment-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/ai-news-sentiment-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/ai-news-sentiment-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/ai-news-sentiment-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/ai-news-sentiment-agent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/ai-news-sentiment-agent/` | JSON |
| Verified data | `data/verified/ai-news-sentiment-agent/` | JSON |
| Agent log | `logs/ai-news-sentiment-agent-[DATE].json` | JSON |
| Human report | `reports/generated/ai-news-sentiment-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

The AI News & Sentiment Agent monitors a small set of AI-related news articles, labels headline sentiment, records review-ready article payloads, and flags negative items for human attention without automatically writing to Airtable or sending email.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/ai-news-sentiment-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run ai-news-sentiment-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/ai-news-sentiment-agent data/verified/ai-news-sentiment-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/ai-news-sentiment-agent.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: set_ai_news_fields. Labor: AI with Human gate.
   Script called: `scripts/gigo/set-ai-news-fields.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
3. Step name: fetch_ai_newsapi. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-ai-newsapi.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-news-sentiment-agent/.
4. Step name: split_ai_news_articles. Labor: AI with Human gate.
   Script called: `scripts/gigo/split-ai-news-articles.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
5. Step name: score_ai_news_sentiment. Labor: AI with Human gate.
   Script called: `scripts/tools/score-ai-news-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: prepare_ai_news_airtable_record. Labor: AI with Human gate.
   Script called: `scripts/gigo/prepare-ai-news-airtable-record.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
7. Step name: filter_negative_ai_news. Labor: AI with Human gate.
   Script called: `scripts/gigo/filter-negative-ai-news.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
8. Step name: send_negative_ai_news_email_handoff. Labor: AI with Human gate.
   Script called: `scripts/tools/send-negative-ai-news-email-handoff.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/ai-news-sentiment-agent-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

# Mycroft News Intelligence Agent

## Purpose

The Mycroft News Intelligence Agent monitors AI and technology companies across NewsAPI and Google News RSS, normalizes article text, estimates sentiment-driven risk, prepares financial-intelligence records, and generates alerts for human review before any database or email side effects occur.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Company list | JSON | `scripts/gigo/mycroft_company_list.py` | Confirm source is allowed, current, and rate-safe before live fetch. |
| NewsAPI query payloads | JSON | `scripts/gigo/build_mycroft_news_queries.py` | Confirm source is allowed, current, and rate-safe before live fetch. |
| NewsAPI results | JSON | NewsAPI or local export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Google News RSS | XML/text | Google News RSS or local export | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json` | Yes |
| Company list | JSON | `scripts/gigo/mycroft_company_list.py` | Yes |
| NewsAPI query payloads | JSON | `scripts/gigo/build_mycroft_news_queries.py` | Yes |
| NewsAPI results | JSON | NewsAPI or local export | Yes |
| Google News RSS | XML/text | Google News RSS or local export | No |
| NewsAPI credential | Environment variable | `NEWSAPI_KEY` | No |
| Hugging Face credential | Environment variable | `HUGGINGFACE_API_TOKEN` for future live FinBERT adapter | No |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No |

## Phase Gates

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: mycroft_company_list. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft_company_list.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
3. Step name: build_mycroft_news_queries. Labor: AI with Human gate.
   Script called: `scripts/gigo/build_mycroft_news_queries.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
4. Step name: fetch_mycroft_newsapi. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_mycroft_newsapi.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/mycroft-news-intelligence-agent/.
5. Step name: normalize_mycroft_newsapi. Labor: AI with Human gate.
   Script called: `scripts/gigo/normalize_mycroft_newsapi.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
6. Step name: mycroft_finbert_sentiment_spec. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft_finbert_sentiment_spec.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: mycroft_risk_calculator. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft_risk_calculator.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: prepare_mycroft_financial_intelligence_rows. Labor: AI with Human gate.
   Script called: `scripts/gigo/prepare_mycroft_financial_intelligence_rows.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-news-intelligence-agent/.
9. Step name: mycroft_alert_generator. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft_alert_generator.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-news-intelligence-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-news-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft News Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| mycroft_company_list | `snickerdoodle run mycroft-news-intelligence-agent --step mycroft-company-list` |  |
| build_mycroft_news_queries | `snickerdoodle run mycroft-news-intelligence-agent --step build-mycroft-news-queries` |  |
| fetch_mycroft_newsapi | `snickerdoodle run mycroft-news-intelligence-agent --step fetch-mycroft-newsapi` | `--sample` |
| normalize_mycroft_newsapi | `snickerdoodle run mycroft-news-intelligence-agent --step normalize-mycroft-newsapi` |  |
| mycroft_finbert_sentiment_spec | `snickerdoodle run mycroft-news-intelligence-agent --step mycroft-finbert-sentiment-spec` | `--no-write` |
| mycroft_risk_calculator | `snickerdoodle run mycroft-news-intelligence-agent --step mycroft-risk-calculator` | `--no-write` |
| prepare_mycroft_financial_intelligence_rows | `snickerdoodle run mycroft-news-intelligence-agent --step prepare-mycroft-financial-intelligence-rows` |  |
| mycroft_alert_generator | `snickerdoodle run mycroft-news-intelligence-agent --step mycroft-alert-generator` | `--no-write` |
| Produce human report | `snickerdoodle run mycroft-news-intelligence-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-news-intelligence-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-news-intelligence-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-news-intelligence-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| mycroft_company_list | `scripts/gigo/mycroft_company_list.py` | gigo |
| build_mycroft_news_queries | `scripts/gigo/build_mycroft_news_queries.py` | gigo |
| fetch_mycroft_newsapi | `scripts/ingest/fetch_mycroft_newsapi.py` | ingest |
| normalize_mycroft_newsapi | `scripts/gigo/normalize_mycroft_newsapi.py` | gigo |
| mycroft_finbert_sentiment_spec | `scripts/tools/mycroft_finbert_sentiment_spec.py` | tool |
| mycroft_risk_calculator | `scripts/tools/mycroft_risk_calculator.py` | tool |
| prepare_mycroft_financial_intelligence_rows | `scripts/gigo/prepare_mycroft_financial_intelligence_rows.py` | gigo |
| mycroft_alert_generator | `scripts/tools/mycroft_alert_generator.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-news-intelligence-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-news-intelligence-agent/` | JSON |
| Verified data | `data/verified/mycroft-news-intelligence-agent/` | JSON |
| Agent log | `logs/mycroft-news-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-news-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json`

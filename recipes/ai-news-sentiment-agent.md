# AI News & Sentiment Agent

## Purpose

The AI News & Sentiment Agent monitors a small set of AI-related news articles, labels headline sentiment, records review-ready article payloads, and flags negative items for human attention without automatically writing to Airtable or sending email.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ticker/query config | JSON | Recipe default: ticker `AI`, query `nvidia` | Confirm source is allowed, current, and rate-safe before live fetch. |
| News articles | JSON | NewsAPI live call or `data/raw/ai-news-sentiment-agent/` | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: set_ai_news_fields. Labor: AI with Human gate.
   Script called: `scripts/gigo/set_ai_news_fields.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
3. Step name: fetch_ai_newsapi. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_ai_newsapi.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-news-sentiment-agent/.
4. Step name: split_ai_news_articles. Labor: AI with Human gate.
   Script called: `scripts/gigo/split_ai_news_articles.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
5. Step name: score_ai_news_sentiment. Labor: AI with Human gate.
   Script called: `scripts/tools/score_ai_news_sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: prepare_ai_news_airtable_record. Labor: AI with Human gate.
   Script called: `scripts/gigo/prepare_ai_news_airtable_record.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
7. Step name: filter_negative_ai_news. Labor: AI with Human gate.
   Script called: `scripts/gigo/filter_negative_ai_news.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-news-sentiment-agent/.
8. Step name: send_negative_ai_news_email_handoff. Labor: AI with Human gate.
   Script called: `scripts/tools/send_negative_ai_news_email_handoff.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/ai-news-sentiment-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/ai-news-sentiment-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/ai-news-sentiment-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `AI News & Sentiment Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| set_ai_news_fields | `snickerdoodle run ai-news-sentiment-agent --step set-ai-news-fields` |  |
| fetch_ai_newsapi | `snickerdoodle run ai-news-sentiment-agent --step fetch-ai-newsapi` | `--sample` |
| split_ai_news_articles | `snickerdoodle run ai-news-sentiment-agent --step split-ai-news-articles` |  |
| score_ai_news_sentiment | `snickerdoodle run ai-news-sentiment-agent --step score-ai-news-sentiment` | `--no-write` |
| prepare_ai_news_airtable_record | `snickerdoodle run ai-news-sentiment-agent --step prepare-ai-news-airtable-record` |  |
| filter_negative_ai_news | `snickerdoodle run ai-news-sentiment-agent --step filter-negative-ai-news` |  |
| send_negative_ai_news_email_handoff | `snickerdoodle run ai-news-sentiment-agent --step send-negative-ai-news-email-handoff` | `--no-write` |
| Produce human report | `snickerdoodle run ai-news-sentiment-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate ai-news-sentiment-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate ai-news-sentiment-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate ai-news-sentiment-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| set_ai_news_fields | `scripts/gigo/set_ai_news_fields.py` | gigo |
| fetch_ai_newsapi | `scripts/ingest/fetch_ai_newsapi.py` | ingest |
| split_ai_news_articles | `scripts/gigo/split_ai_news_articles.py` | gigo |
| score_ai_news_sentiment | `scripts/tools/score_ai_news_sentiment.py` | tool |
| prepare_ai_news_airtable_record | `scripts/gigo/prepare_ai_news_airtable_record.py` | gigo |
| filter_negative_ai_news | `scripts/gigo/filter_negative_ai_news.py` | gigo |
| send_negative_ai_news_email_handoff | `scripts/tools/send_negative_ai_news_email_handoff.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/ai-news-sentiment-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/ai-news-sentiment-agent/` | JSON |
| Verified data | `data/verified/ai-news-sentiment-agent/` | JSON |
| Agent log | `logs/ai-news-sentiment-agent-[DATE].json` | JSON |
| Human report | `reports/generated/ai-news-sentiment-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json`

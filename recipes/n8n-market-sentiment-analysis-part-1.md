# Market Sentiment Analysis - Part 1

## Purpose

Market Sentiment Analysis - Part 1 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to market sentiment analysis - part 1. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch Price Data | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch News Headlines | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch Reddit Mentions | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook Trigger | webhook | conductor |
| Parse Question & Extract Tickers | code | gigo |
| Fetch Price Data | httpRequest | ingest |
| Fetch News Headlines | httpRequest | ingest |
| Fetch Reddit Mentions | httpRequest | ingest |
| Aggregate & Calculate Sentiment | code | gigo |
| AI Analysis & Synthesis | lmChatAnthropic | gigo |
| Format Response | code | gigo |
| Send to Slack | slack | tool |
| Send Email | emailSend | tool |
| Webhook Response | respondToWebhook | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-market-sentiment-analysis-part-1.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-market-sentiment-analysis-part-1 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-market-sentiment-analysis-part-1 data/verified/n8n-market-sentiment-analysis-part-1 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-market-sentiment-analysis-part-1.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Parse Question & Extract Tickers. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__parse-question-and-extract-tickers.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-market-sentiment-analysis-part-1/.
3. Step name: Fetch Price Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-market-sentiment-analysis-part-1__fetch-price-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-market-sentiment-analysis-part-1/.
4. Step name: Fetch News Headlines. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-market-sentiment-analysis-part-1__fetch-news-headlines.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-market-sentiment-analysis-part-1/.
5. Step name: Fetch Reddit Mentions. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-market-sentiment-analysis-part-1__fetch-reddit-mentions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-market-sentiment-analysis-part-1/.
6. Step name: Aggregate & Calculate Sentiment. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__aggregate-and-calculate-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-market-sentiment-analysis-part-1/.
7. Step name: AI Analysis & Synthesis. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__ai-analysis-and-synthesis.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-market-sentiment-analysis-part-1/.
8. Step name: Format Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__format-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-market-sentiment-analysis-part-1/.
9. Step name: Send to Slack. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-market-sentiment-analysis-part-1__send-to-slack.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Send Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-market-sentiment-analysis-part-1__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-market-sentiment-analysis-part-1__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-market-sentiment-analysis-part-1-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-market-sentiment-analysis-part-1-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Market Sentiment Analysis - Part 1` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-market-sentiment-analysis-part-1 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-market-sentiment-analysis-part-1 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Parse Question & Extract Tickers | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step parse-question-and-extract-tickers` |  |
| Fetch Price Data | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step fetch-price-data` | `--sample` |
| Fetch News Headlines | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step fetch-news-headlines` | `--sample` |
| Fetch Reddit Mentions | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step fetch-reddit-mentions` | `--sample` |
| Aggregate & Calculate Sentiment | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step aggregate-and-calculate-sentiment` |  |
| AI Analysis & Synthesis | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step ai-analysis-and-synthesis` |  |
| Format Response | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step format-response` |  |
| Send to Slack | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step send-to-slack` | `--no-write` |
| Send Email | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step send-email` | `--no-write` |
| Produce human report | `snickerdoodle run n8n-market-sentiment-analysis-part-1 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-market-sentiment-analysis-part-1 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-market-sentiment-analysis-part-1 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-market-sentiment-analysis-part-1 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Parse Question & Extract Tickers | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__parse-question-and-extract-tickers.py` | gigo |
| Fetch Price Data | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-market-sentiment-analysis-part-1__fetch-price-data.py` | ingest |
| Fetch News Headlines | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-market-sentiment-analysis-part-1__fetch-news-headlines.py` | ingest |
| Fetch Reddit Mentions | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-market-sentiment-analysis-part-1__fetch-reddit-mentions.py` | ingest |
| Aggregate & Calculate Sentiment | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__aggregate-and-calculate-sentiment.py` | gigo |
| AI Analysis & Synthesis | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__ai-analysis-and-synthesis.py` | gigo |
| Format Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-market-sentiment-analysis-part-1__format-response.py` | gigo |
| Send to Slack | `[TODO: DEV] Create or map script path: scripts/tools/n8n-market-sentiment-analysis-part-1__send-to-slack.py` | tool |
| Send Email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-market-sentiment-analysis-part-1__send-email.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-market-sentiment-analysis-part-1__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-market-sentiment-analysis-part-1/` | JSON |
| Verified data | `data/verified/n8n-market-sentiment-analysis-part-1/` | JSON |
| Agent log | `logs/n8n-market-sentiment-analysis-part-1-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-market-sentiment-analysis-part-1-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json`

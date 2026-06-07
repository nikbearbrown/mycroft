# Market Sentiment Analysis - Part 1

## Purpose

Market Sentiment Analysis - Part 1 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to market sentiment analysis - part 1. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook Trigger | `webhook` | tool |
| Parse Question & Extract Tickers | `code` | gigo |
| Fetch Price Data | `httpRequest` | ingest |
| Fetch News Headlines | `httpRequest` | ingest |
| Fetch Reddit Mentions | `httpRequest` | ingest |
| Aggregate & Calculate Sentiment | `code` | tool |
| AI Analysis & Synthesis | `lmChatAnthropic` | tool |
| Format Response | `code` | conductor |
| Send to Slack | `slack` | tool |
| Send Email | `emailSend` | report |
| Webhook Response | `respondToWebhook` | report |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (4 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (1 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/market-sentiment-analysis-part-1.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run market-sentiment-analysis-part-1 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/market-sentiment-analysis-part-1 data/verified/market-sentiment-analysis-part-1 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/market-sentiment-analysis-part-1.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Webhook Trigger. Labor: AI with Human gate.
   Script called: `scripts/tools/market-sentiment-analysis-part-1__webhook-trigger.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Parse Question & Extract Tickers. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/market-sentiment-analysis-part-1__parse-question-and-extract-tickers.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/market-sentiment-analysis-part-1/.
4. Step name: Fetch Price Data. Labor: AI with Human gate.
   Script called: `scripts/ingest/market-sentiment-analysis-part-1__fetch-price-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/market-sentiment-analysis-part-1/.
5. Step name: Fetch News Headlines. Labor: AI with Human gate.
   Script called: `scripts/ingest/market-sentiment-analysis-part-1__fetch-news-headlines.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/market-sentiment-analysis-part-1/.
6. Step name: Fetch Reddit Mentions. Labor: AI with Human gate.
   Script called: `scripts/ingest/market-sentiment-analysis-part-1__fetch-reddit-mentions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/market-sentiment-analysis-part-1/.
7. Step name: Aggregate & Calculate Sentiment. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__aggregate-and-calculate-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: AI Analysis & Synthesis. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__ai-analysis-and-synthesis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Send to Slack. Labor: AI with Human gate.
   Script called: `scripts/tools/market-sentiment-analysis-part-1__send-to-slack.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Send Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__send-email.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
11. Step name: Webhook Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__webhook-response.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/market-sentiment-analysis-part-1-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/market-sentiment-analysis-part-1-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Market Sentiment Analysis - Part 1` run.
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
`snickerdoodle run market-sentiment-analysis-part-1 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run market-sentiment-analysis-part-1 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Webhook Trigger | `snickerdoodle run market-sentiment-analysis-part-1 --step webhook-trigger` | `--no-write` |
| Parse Question & Extract Tickers | `snickerdoodle run market-sentiment-analysis-part-1 --step parse-question-and-extract-tickers` |  |
| Fetch Price Data | `snickerdoodle run market-sentiment-analysis-part-1 --step fetch-price-data` | `--sample` |
| Fetch News Headlines | `snickerdoodle run market-sentiment-analysis-part-1 --step fetch-news-headlines` | `--sample` |
| Fetch Reddit Mentions | `snickerdoodle run market-sentiment-analysis-part-1 --step fetch-reddit-mentions` | `--sample` |
| Aggregate & Calculate Sentiment | `snickerdoodle run market-sentiment-analysis-part-1 --step aggregate-and-calculate-sentiment` | `--no-write` |
| AI Analysis & Synthesis | `snickerdoodle run market-sentiment-analysis-part-1 --step ai-analysis-and-synthesis` | `--no-write` |
| Send to Slack | `snickerdoodle run market-sentiment-analysis-part-1 --step send-to-slack` | `--no-write` |
| Send Email | `snickerdoodle run market-sentiment-analysis-part-1 --step send-email` | `--no-write` |
| Webhook Response | `snickerdoodle run market-sentiment-analysis-part-1 --step webhook-response` | `--no-write` |
| Produce human report | `snickerdoodle run market-sentiment-analysis-part-1 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Webhook Trigger | `scripts/tools/market-sentiment-analysis-part-1__webhook-trigger.py` | tool |
| Parse Question & Extract Tickers | `[TODO: DEV] Create or map script path: scripts/gigo/market-sentiment-analysis-part-1__parse-question-and-extract-tickers.py` | gigo |
| Fetch Price Data | `scripts/ingest/market-sentiment-analysis-part-1__fetch-price-data.py` | ingest |
| Fetch News Headlines | `scripts/ingest/market-sentiment-analysis-part-1__fetch-news-headlines.py` | ingest |
| Fetch Reddit Mentions | `scripts/ingest/market-sentiment-analysis-part-1__fetch-reddit-mentions.py` | ingest |
| Aggregate & Calculate Sentiment | `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__aggregate-and-calculate-sentiment.py` | tool |
| AI Analysis & Synthesis | `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__ai-analysis-and-synthesis.py` | tool |
| Send to Slack | `scripts/tools/market-sentiment-analysis-part-1__send-to-slack.py` | tool |
| Send Email | `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__send-email.py` | tool |
| Webhook Response | `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__webhook-response.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/market-sentiment-analysis-part-1__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/market-sentiment-analysis-part-1/` | JSON |
| Verified data | `data/verified/market-sentiment-analysis-part-1/` | JSON |
| Agent log | `logs/market-sentiment-analysis-part-1-[DATE].json` | JSON |
| Human report | `reports/generated/market-sentiment-analysis-part-1-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json`

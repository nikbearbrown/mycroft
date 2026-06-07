# Social Sentiment Agent

## Purpose

Social Sentiment Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to social sentiment agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Get StackOverflow | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Get Reddit ML | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Get GitHub | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Groq LLM Sentiment | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Process StackOverflow | function | gigo |
| Get StackOverflow | httpRequest | ingest |
| Manual Trigger | manualTrigger | conductor |
| Combine All Data | function | gigo |
| Process Reddit ML | function | gigo |
| Get Reddit ML | httpRequest | ingest |
| Process GitHub | function | gigo |
| Get GitHub | httpRequest | ingest |
| Groq LLM Sentiment | httpRequest | ingest |
| Process Groq Sentiment | function | gigo |
| Groq Topic Classification | httpRequest | conductor |
| Topic Clustering Engine | function | gigo |
| Signal-to-Noise Filter | function | conductor |
| Social Sentiment Output | function | gigo |
| Enhanced Data Export | function | gigo |
| Prepare for Google Sheets | function | tool |
| Store in Google Sheets | googleSheets | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-social-sentiment-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-social-sentiment-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-social-sentiment-agent data/verified/n8n-social-sentiment-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-social-sentiment-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Process StackOverflow. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-stackoverflow.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
3. Step name: Get StackOverflow. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__get-stackoverflow.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-social-sentiment-agent/.
4. Step name: Combine All Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__combine-all-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
5. Step name: Process Reddit ML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-reddit-ml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
6. Step name: Get Reddit ML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__get-reddit-ml.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-social-sentiment-agent/.
7. Step name: Process GitHub. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-github.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
8. Step name: Get GitHub. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__get-github.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-social-sentiment-agent/.
9. Step name: Groq LLM Sentiment. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__groq-llm-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-social-sentiment-agent/.
10. Step name: Process Groq Sentiment. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-groq-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
11. Step name: Topic Clustering Engine. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__topic-clustering-engine.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
12. Step name: Social Sentiment Output. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__social-sentiment-output.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
13. Step name: Enhanced Data Export. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__enhanced-data-export.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-social-sentiment-agent/.
14. Step name: Prepare for Google Sheets. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-social-sentiment-agent__prepare-for-google-sheets.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Store in Google Sheets. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-social-sentiment-agent__store-in-google-sheets.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-social-sentiment-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-social-sentiment-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-social-sentiment-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Social Sentiment Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-social-sentiment-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-social-sentiment-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Process StackOverflow | `snickerdoodle run n8n-social-sentiment-agent --step process-stackoverflow` |  |
| Get StackOverflow | `snickerdoodle run n8n-social-sentiment-agent --step get-stackoverflow` | `--sample` |
| Combine All Data | `snickerdoodle run n8n-social-sentiment-agent --step combine-all-data` |  |
| Process Reddit ML | `snickerdoodle run n8n-social-sentiment-agent --step process-reddit-ml` |  |
| Get Reddit ML | `snickerdoodle run n8n-social-sentiment-agent --step get-reddit-ml` | `--sample` |
| Process GitHub | `snickerdoodle run n8n-social-sentiment-agent --step process-github` |  |
| Get GitHub | `snickerdoodle run n8n-social-sentiment-agent --step get-github` | `--sample` |
| Groq LLM Sentiment | `snickerdoodle run n8n-social-sentiment-agent --step groq-llm-sentiment` | `--sample` |
| Process Groq Sentiment | `snickerdoodle run n8n-social-sentiment-agent --step process-groq-sentiment` |  |
| Topic Clustering Engine | `snickerdoodle run n8n-social-sentiment-agent --step topic-clustering-engine` |  |
| Social Sentiment Output | `snickerdoodle run n8n-social-sentiment-agent --step social-sentiment-output` |  |
| Enhanced Data Export | `snickerdoodle run n8n-social-sentiment-agent --step enhanced-data-export` |  |
| Prepare for Google Sheets | `snickerdoodle run n8n-social-sentiment-agent --step prepare-for-google-sheets` | `--no-write` |
| Store in Google Sheets | `snickerdoodle run n8n-social-sentiment-agent --step store-in-google-sheets` | `--no-write` |
| Produce human report | `snickerdoodle run n8n-social-sentiment-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-social-sentiment-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-social-sentiment-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-social-sentiment-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Process StackOverflow | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-stackoverflow.py` | gigo |
| Get StackOverflow | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__get-stackoverflow.py` | ingest |
| Combine All Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__combine-all-data.py` | gigo |
| Process Reddit ML | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-reddit-ml.py` | gigo |
| Get Reddit ML | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__get-reddit-ml.py` | ingest |
| Process GitHub | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-github.py` | gigo |
| Get GitHub | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__get-github.py` | ingest |
| Groq LLM Sentiment | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-social-sentiment-agent__groq-llm-sentiment.py` | ingest |
| Process Groq Sentiment | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__process-groq-sentiment.py` | gigo |
| Topic Clustering Engine | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__topic-clustering-engine.py` | gigo |
| Social Sentiment Output | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__social-sentiment-output.py` | gigo |
| Enhanced Data Export | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-social-sentiment-agent__enhanced-data-export.py` | gigo |
| Prepare for Google Sheets | `[TODO: DEV] Create or map script path: scripts/tools/n8n-social-sentiment-agent__prepare-for-google-sheets.py` | tool |
| Store in Google Sheets | `[TODO: DEV] Create or map script path: scripts/tools/n8n-social-sentiment-agent__store-in-google-sheets.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-social-sentiment-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-social-sentiment-agent/` | JSON |
| Verified data | `data/verified/n8n-social-sentiment-agent/` | JSON |
| Agent log | `logs/n8n-social-sentiment-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-social-sentiment-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json`

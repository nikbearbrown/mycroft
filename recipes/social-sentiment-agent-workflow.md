# workflow

## Purpose

workflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to workflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Process StackOverflow | `function` | gigo |
| Get StackOverflow | `httpRequest` | ingest |
| Manual Trigger | `manualTrigger` | conductor |
| Combine All Data | `function` | conductor |
| Process Reddit ML | `function` | gigo |
| Get Reddit ML | `httpRequest` | ingest |
| Process GitHub | `function` | gigo |
| Get GitHub | `httpRequest` | ingest |
| Groq LLM Sentiment | `httpRequest` | tool |
| Process Groq Sentiment | `function` | gigo |
| Groq Topic Classification | `httpRequest` | tool |
| Topic Clustering Engine | `function` | conductor |
| Signal-to-Noise Filter | `function` | gigo |
| Social Sentiment Output | `function` | conductor |
| Enhanced Data Export | `function` | conductor |
| Prepare for Google Sheets | `function` | conductor |
| Store in Google Sheets | `googleSheets` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (5 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (3 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (6 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/social-sentiment-agent-workflow.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run social-sentiment-agent-workflow --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/social-sentiment-agent-workflow data/verified/social-sentiment-agent-workflow -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/social-sentiment-agent-workflow.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Process StackOverflow. Labor: AI with Human gate.
   Script called: `scripts/gigo/social-sentiment-agent-workflow__process-stackoverflow.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/social-sentiment-agent-workflow/.
3. Step name: Get StackOverflow. Labor: AI with Human gate.
   Script called: `scripts/ingest/social-sentiment-agent-workflow__get-stackoverflow.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/social-sentiment-agent-workflow/.
4. Step name: Process Reddit ML. Labor: AI with Human gate.
   Script called: `scripts/gigo/social-sentiment-agent-workflow__process-reddit-ml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/social-sentiment-agent-workflow/.
5. Step name: Get Reddit ML. Labor: AI with Human gate.
   Script called: `scripts/ingest/social-sentiment-agent-workflow__get-reddit-ml.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/social-sentiment-agent-workflow/.
6. Step name: Process GitHub. Labor: AI with Human gate.
   Script called: `scripts/gigo/social-sentiment-agent-workflow__process-github.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/social-sentiment-agent-workflow/.
7. Step name: Get GitHub. Labor: AI with Human gate.
   Script called: `scripts/ingest/social-sentiment-agent-workflow__get-github.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/social-sentiment-agent-workflow/.
8. Step name: Groq LLM Sentiment. Labor: AI with Human gate.
   Script called: `scripts/tools/social-sentiment-agent-workflow__groq-llm-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Process Groq Sentiment. Labor: AI with Human gate.
   Script called: `scripts/gigo/social-sentiment-agent-workflow__process-groq-sentiment.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/social-sentiment-agent-workflow/.
10. Step name: Groq Topic Classification. Labor: AI with Human gate.
   Script called: `scripts/tools/social-sentiment-agent-workflow__groq-topic-classification.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Signal-to-Noise Filter. Labor: AI with Human gate.
   Script called: `scripts/gigo/social-sentiment-agent-workflow__signal-to-noise-filter.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/social-sentiment-agent-workflow/.
12. Step name: Store in Google Sheets. Labor: AI with Human gate.
   Script called: `scripts/tools/social-sentiment-agent-workflow__store-in-google-sheets.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/social-sentiment-agent-workflow__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/social-sentiment-agent-workflow-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/social-sentiment-agent-workflow-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `workflow` run.
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
`snickerdoodle run social-sentiment-agent-workflow --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run social-sentiment-agent-workflow --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Process StackOverflow | `snickerdoodle run social-sentiment-agent-workflow --step process-stackoverflow` |  |
| Get StackOverflow | `snickerdoodle run social-sentiment-agent-workflow --step get-stackoverflow` | `--sample` |
| Process Reddit ML | `snickerdoodle run social-sentiment-agent-workflow --step process-reddit-ml` |  |
| Get Reddit ML | `snickerdoodle run social-sentiment-agent-workflow --step get-reddit-ml` | `--sample` |
| Process GitHub | `snickerdoodle run social-sentiment-agent-workflow --step process-github` |  |
| Get GitHub | `snickerdoodle run social-sentiment-agent-workflow --step get-github` | `--sample` |
| Groq LLM Sentiment | `snickerdoodle run social-sentiment-agent-workflow --step groq-llm-sentiment` | `--no-write` |
| Process Groq Sentiment | `snickerdoodle run social-sentiment-agent-workflow --step process-groq-sentiment` |  |
| Groq Topic Classification | `snickerdoodle run social-sentiment-agent-workflow --step groq-topic-classification` | `--no-write` |
| Signal-to-Noise Filter | `snickerdoodle run social-sentiment-agent-workflow --step signal-to-noise-filter` |  |
| Store in Google Sheets | `snickerdoodle run social-sentiment-agent-workflow --step store-in-google-sheets` | `--no-write` |
| Produce human report | `snickerdoodle run social-sentiment-agent-workflow --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate social-sentiment-agent-workflow --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate social-sentiment-agent-workflow --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate social-sentiment-agent-workflow --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Process StackOverflow | `scripts/gigo/social-sentiment-agent-workflow__process-stackoverflow.py` | gigo |
| Get StackOverflow | `scripts/ingest/social-sentiment-agent-workflow__get-stackoverflow.py` | ingest |
| Process Reddit ML | `scripts/gigo/social-sentiment-agent-workflow__process-reddit-ml.py` | gigo |
| Get Reddit ML | `scripts/ingest/social-sentiment-agent-workflow__get-reddit-ml.py` | ingest |
| Process GitHub | `scripts/gigo/social-sentiment-agent-workflow__process-github.py` | gigo |
| Get GitHub | `scripts/ingest/social-sentiment-agent-workflow__get-github.py` | ingest |
| Groq LLM Sentiment | `scripts/tools/social-sentiment-agent-workflow__groq-llm-sentiment.py` | tool |
| Process Groq Sentiment | `scripts/gigo/social-sentiment-agent-workflow__process-groq-sentiment.py` | gigo |
| Groq Topic Classification | `scripts/tools/social-sentiment-agent-workflow__groq-topic-classification.py` | tool |
| Signal-to-Noise Filter | `scripts/gigo/social-sentiment-agent-workflow__signal-to-noise-filter.py` | gigo |
| Store in Google Sheets | `scripts/tools/social-sentiment-agent-workflow__store-in-google-sheets.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/social-sentiment-agent-workflow__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/social-sentiment-agent-workflow/` | JSON |
| Verified data | `data/verified/social-sentiment-agent-workflow/` | JSON |
| Agent log | `logs/social-sentiment-agent-workflow-[DATE].json` | JSON |
| Human report | `reports/generated/social-sentiment-agent-workflow-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json`

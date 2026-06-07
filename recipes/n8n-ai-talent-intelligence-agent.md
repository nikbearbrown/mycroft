# AI Talent Intelligence Agent

## Purpose

AI Talent Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to ai talent intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| 📚 SOURCE 1: ArXiv Papers | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| 📰 SOURCE 2: News Search | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| ▶️ START - Run Complete Analysis | manualTrigger | conductor |
| 📚 SOURCE 1: ArXiv Papers | httpRequest | ingest |
| 📰 SOURCE 2: News Search | httpRequest | ingest |
| 🔄 Parse ArXiv Data | code | gigo |
| 🔄 Parse News Data | code | gigo |
| 🔍 FILTER: High Significance Only | if | conductor |
| 📊 AGGREGATE Statistics | aggregate | gigo |
| 📋 Generate Intelligence Report | code | gigo |
| 💾 Save to Database | postgres | tool |
| 📧 Format Email Report | code | tool |
| 📬 Send Email Report | emailSend | tool |
| Code | code | gigo |
| Merge | merge | conductor |
| When chat message received | chatTrigger | conductor |
| Basic LLM Chain | chainLlm | gigo |
| Groq Chat Model | lmChatGroq | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-ai-talent-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-ai-talent-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-ai-talent-intelligence-agent data/verified/n8n-ai-talent-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-ai-talent-intelligence-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: 📚 SOURCE 1: ArXiv Papers. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-ai-talent-intelligence-agent__source-1-arxiv-papers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-ai-talent-intelligence-agent/.
3. Step name: 📰 SOURCE 2: News Search. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-ai-talent-intelligence-agent__source-2-news-search.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-ai-talent-intelligence-agent/.
4. Step name: 🔄 Parse ArXiv Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__parse-arxiv-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-ai-talent-intelligence-agent/.
5. Step name: 🔄 Parse News Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__parse-news-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-ai-talent-intelligence-agent/.
6. Step name: 📊 AGGREGATE Statistics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__aggregate-statistics.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-ai-talent-intelligence-agent/.
7. Step name: 📋 Generate Intelligence Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__generate-intelligence-report.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-ai-talent-intelligence-agent/.
8. Step name: 💾 Save to Database. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__save-to-database.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: 📧 Format Email Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__format-email-report.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: 📬 Send Email Report. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__send-email-report.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Code. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__code.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-ai-talent-intelligence-agent/.
12. Step name: Basic LLM Chain. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__basic-llm-chain.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-ai-talent-intelligence-agent/.
13. Step name: Groq Chat Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__groq-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-ai-talent-intelligence-agent/.
14. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-ai-talent-intelligence-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-ai-talent-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `AI Talent Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-ai-talent-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-ai-talent-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| 📚 SOURCE 1: ArXiv Papers | `snickerdoodle run n8n-ai-talent-intelligence-agent --step source-1-arxiv-papers` | `--sample` |
| 📰 SOURCE 2: News Search | `snickerdoodle run n8n-ai-talent-intelligence-agent --step source-2-news-search` | `--sample` |
| 🔄 Parse ArXiv Data | `snickerdoodle run n8n-ai-talent-intelligence-agent --step parse-arxiv-data` |  |
| 🔄 Parse News Data | `snickerdoodle run n8n-ai-talent-intelligence-agent --step parse-news-data` |  |
| 📊 AGGREGATE Statistics | `snickerdoodle run n8n-ai-talent-intelligence-agent --step aggregate-statistics` |  |
| 📋 Generate Intelligence Report | `snickerdoodle run n8n-ai-talent-intelligence-agent --step generate-intelligence-report` |  |
| 💾 Save to Database | `snickerdoodle run n8n-ai-talent-intelligence-agent --step save-to-database` | `--no-write` |
| 📧 Format Email Report | `snickerdoodle run n8n-ai-talent-intelligence-agent --step format-email-report` | `--no-write` |
| 📬 Send Email Report | `snickerdoodle run n8n-ai-talent-intelligence-agent --step send-email-report` | `--no-write` |
| Code | `snickerdoodle run n8n-ai-talent-intelligence-agent --step code` |  |
| Basic LLM Chain | `snickerdoodle run n8n-ai-talent-intelligence-agent --step basic-llm-chain` |  |
| Groq Chat Model | `snickerdoodle run n8n-ai-talent-intelligence-agent --step groq-chat-model` |  |
| Produce human report | `snickerdoodle run n8n-ai-talent-intelligence-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-ai-talent-intelligence-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-ai-talent-intelligence-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-ai-talent-intelligence-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| 📚 SOURCE 1: ArXiv Papers | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-ai-talent-intelligence-agent__source-1-arxiv-papers.py` | ingest |
| 📰 SOURCE 2: News Search | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-ai-talent-intelligence-agent__source-2-news-search.py` | ingest |
| 🔄 Parse ArXiv Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__parse-arxiv-data.py` | gigo |
| 🔄 Parse News Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__parse-news-data.py` | gigo |
| 📊 AGGREGATE Statistics | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__aggregate-statistics.py` | gigo |
| 📋 Generate Intelligence Report | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__generate-intelligence-report.py` | gigo |
| 💾 Save to Database | `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__save-to-database.py` | tool |
| 📧 Format Email Report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__format-email-report.py` | tool |
| 📬 Send Email Report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__send-email-report.py` | tool |
| Code | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__code.py` | gigo |
| Basic LLM Chain | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__basic-llm-chain.py` | gigo |
| Groq Chat Model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-ai-talent-intelligence-agent__groq-chat-model.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-ai-talent-intelligence-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-ai-talent-intelligence-agent/` | JSON |
| Verified data | `data/verified/n8n-ai-talent-intelligence-agent/` | JSON |
| Agent log | `logs/n8n-ai-talent-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-ai-talent-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json`

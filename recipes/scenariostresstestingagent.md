# ScenarioStressTestingAgent

## Purpose

ScenarioStressTestingAgent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to scenariostresstestingagent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook Trigger | `webhook` | tool |
| Parse Input | `set` | gigo |
| Edit Fields | `set` | conductor |
| Validate Portfolio | `code` | conductor |
| Custom Scenario? | `if` | conductor |
| Load_Template_Scenario | `code` | conductor |
| When chat message received | `chatTrigger` | conductor |
| Basic LLM Chain | `chainLlm` | tool |
| Groq Chat Model | `lmChatGroq` | tool |
| Parse_LLM_Response | `code` | tool |
| Stress_Test_Engine | `code` | tool |
| Respond to Webhook | `respondToWebhook` | report |
| Fetch_Data | `httpRequest` | ingest |
| Merge | `merge` | conductor |
| Merge1 | `merge` | conductor |
| Save_Portfolio_Before_LLM | `code` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (6 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (7 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/scenariostresstestingagent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run scenariostresstestingagent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/scenariostresstestingagent data/verified/scenariostresstestingagent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/scenariostresstestingagent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Webhook Trigger. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent__webhook-trigger.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Parse Input. Labor: AI with Human gate.
   Script called: `scripts/gigo/scenariostresstestingagent__parse-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/scenariostresstestingagent/.
4. Step name: Basic LLM Chain. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent__basic-llm-chain.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Groq Chat Model. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent__groq-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Parse_LLM_Response. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent__parse-llm-response.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Stress_Test_Engine. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent__stress-test-engine.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/scenariostresstestingagent__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
9. Step name: Fetch_Data. Labor: AI with Human gate.
   Script called: `scripts/ingest/scenariostresstestingagent__fetch-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/scenariostresstestingagent/.
10. Step name: Save_Portfolio_Before_LLM. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent__save-portfolio-before-llm.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/scenariostresstestingagent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/scenariostresstestingagent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/scenariostresstestingagent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `ScenarioStressTestingAgent` run.
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
`snickerdoodle run scenariostresstestingagent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run scenariostresstestingagent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Webhook Trigger | `snickerdoodle run scenariostresstestingagent --step webhook-trigger` | `--no-write` |
| Parse Input | `snickerdoodle run scenariostresstestingagent --step parse-input` |  |
| Basic LLM Chain | `snickerdoodle run scenariostresstestingagent --step basic-llm-chain` | `--no-write` |
| Groq Chat Model | `snickerdoodle run scenariostresstestingagent --step groq-chat-model` | `--no-write` |
| Parse_LLM_Response | `snickerdoodle run scenariostresstestingagent --step parse-llm-response` | `--no-write` |
| Stress_Test_Engine | `snickerdoodle run scenariostresstestingagent --step stress-test-engine` | `--no-write` |
| Respond to Webhook | `snickerdoodle run scenariostresstestingagent --step respond-to-webhook` | `--no-write` |
| Fetch_Data | `snickerdoodle run scenariostresstestingagent --step fetch-data` | `--sample` |
| Save_Portfolio_Before_LLM | `snickerdoodle run scenariostresstestingagent --step save-portfolio-before-llm` | `--no-write` |
| Produce human report | `snickerdoodle run scenariostresstestingagent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate scenariostresstestingagent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate scenariostresstestingagent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate scenariostresstestingagent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Webhook Trigger | `scripts/tools/scenariostresstestingagent__webhook-trigger.py` | tool |
| Parse Input | `scripts/gigo/scenariostresstestingagent__parse-input.py` | gigo |
| Basic LLM Chain | `scripts/tools/scenariostresstestingagent__basic-llm-chain.py` | tool |
| Groq Chat Model | `scripts/tools/scenariostresstestingagent__groq-chat-model.py` | tool |
| Parse_LLM_Response | `scripts/tools/scenariostresstestingagent__parse-llm-response.py` | tool |
| Stress_Test_Engine | `scripts/tools/scenariostresstestingagent__stress-test-engine.py` | tool |
| Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/scenariostresstestingagent__respond-to-webhook.py` | tool |
| Fetch_Data | `scripts/ingest/scenariostresstestingagent__fetch-data.py` | ingest |
| Save_Portfolio_Before_LLM | `scripts/tools/scenariostresstestingagent__save-portfolio-before-llm.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/scenariostresstestingagent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/scenariostresstestingagent/` | JSON |
| Verified data | `data/verified/scenariostresstestingagent/` | JSON |
| Agent log | `logs/scenariostresstestingagent-[DATE].json` | JSON |
| Human report | `reports/generated/scenariostresstestingagent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json`

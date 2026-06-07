# ScenarioStressTestingAgent

## Purpose

ScenarioStressTestingAgent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to scenariostresstestingagent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Fetch_Data | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook Trigger | webhook | conductor |
| Parse Input | set | gigo |
| Edit Fields | set | gigo |
| Validate Portfolio | code | gigo |
| Custom Scenario? | if | conductor |
| Load_Template_Scenario | code | gigo |
| When chat message received | chatTrigger | conductor |
| Basic LLM Chain | chainLlm | gigo |
| Groq Chat Model | lmChatGroq | gigo |
| Parse_LLM_Response | code | gigo |
| Stress_Test_Engine | code | gigo |
| Respond to Webhook | respondToWebhook | conductor |
| Fetch_Data | httpRequest | ingest |
| Merge | merge | conductor |
| Merge1 | merge | conductor |
| Save_Portfolio_Before_LLM | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-scenariostresstestingagent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-scenariostresstestingagent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-scenariostresstestingagent data/verified/n8n-scenariostresstestingagent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-scenariostresstestingagent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Parse Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__parse-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
3. Step name: Edit Fields. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__edit-fields.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
4. Step name: Validate Portfolio. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__validate-portfolio.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
5. Step name: Load_Template_Scenario. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__load-template-scenario.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
6. Step name: Basic LLM Chain. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__basic-llm-chain.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
7. Step name: Groq Chat Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__groq-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
8. Step name: Parse_LLM_Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__parse-llm-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
9. Step name: Stress_Test_Engine. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__stress-test-engine.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
10. Step name: Fetch_Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-scenariostresstestingagent__fetch-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-scenariostresstestingagent/.
11. Step name: Save_Portfolio_Before_LLM. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__save-portfolio-before-llm.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-scenariostresstestingagent/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-scenariostresstestingagent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-scenariostresstestingagent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-scenariostresstestingagent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `ScenarioStressTestingAgent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-scenariostresstestingagent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-scenariostresstestingagent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Parse Input | `snickerdoodle run n8n-scenariostresstestingagent --step parse-input` |  |
| Edit Fields | `snickerdoodle run n8n-scenariostresstestingagent --step edit-fields` |  |
| Validate Portfolio | `snickerdoodle run n8n-scenariostresstestingagent --step validate-portfolio` |  |
| Load_Template_Scenario | `snickerdoodle run n8n-scenariostresstestingagent --step load-template-scenario` |  |
| Basic LLM Chain | `snickerdoodle run n8n-scenariostresstestingagent --step basic-llm-chain` |  |
| Groq Chat Model | `snickerdoodle run n8n-scenariostresstestingagent --step groq-chat-model` |  |
| Parse_LLM_Response | `snickerdoodle run n8n-scenariostresstestingagent --step parse-llm-response` |  |
| Stress_Test_Engine | `snickerdoodle run n8n-scenariostresstestingagent --step stress-test-engine` |  |
| Fetch_Data | `snickerdoodle run n8n-scenariostresstestingagent --step fetch-data` | `--sample` |
| Save_Portfolio_Before_LLM | `snickerdoodle run n8n-scenariostresstestingagent --step save-portfolio-before-llm` |  |
| Produce human report | `snickerdoodle run n8n-scenariostresstestingagent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-scenariostresstestingagent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-scenariostresstestingagent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-scenariostresstestingagent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Parse Input | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__parse-input.py` | gigo |
| Edit Fields | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__edit-fields.py` | gigo |
| Validate Portfolio | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__validate-portfolio.py` | gigo |
| Load_Template_Scenario | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__load-template-scenario.py` | gigo |
| Basic LLM Chain | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__basic-llm-chain.py` | gigo |
| Groq Chat Model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__groq-chat-model.py` | gigo |
| Parse_LLM_Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__parse-llm-response.py` | gigo |
| Stress_Test_Engine | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__stress-test-engine.py` | gigo |
| Fetch_Data | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-scenariostresstestingagent__fetch-data.py` | ingest |
| Save_Portfolio_Before_LLM | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-scenariostresstestingagent__save-portfolio-before-llm.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-scenariostresstestingagent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-scenariostresstestingagent/` | JSON |
| Verified data | `data/verified/n8n-scenariostresstestingagent/` | JSON |
| Agent log | `logs/n8n-scenariostresstestingagent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-scenariostresstestingagent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json`

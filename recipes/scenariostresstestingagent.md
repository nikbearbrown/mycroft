# ScenarioStressTestingAgent

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (6 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (7 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/scenariostresstestingagent.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `scenariostresstestingagent__fetch-data`. Labor: AI. Script called: `scripts/ingest/scenariostresstestingagent__fetch-data.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `scenariostresstestingagent__parse-input`. Labor: AI. Script called: `scripts/gigo/scenariostresstestingagent__parse-input.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `scenariostresstestingagent__webhook-trigger`. Labor: AI. Script called: `scripts/tools/scenariostresstestingagent__webhook-trigger.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `scenariostresstestingagent__basic-llm-chain`. Labor: AI. Script called: `scripts/tools/scenariostresstestingagent__basic-llm-chain.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `scenariostresstestingagent__groq-chat-model`. Labor: AI. Script called: `scripts/tools/scenariostresstestingagent__groq-chat-model.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `scenariostresstestingagent__parse-llm-response`. Labor: AI. Script called: `scripts/tools/scenariostresstestingagent__parse-llm-response.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `scenariostresstestingagent__stress-test-engine`. Labor: AI. Script called: `scripts/tools/scenariostresstestingagent__stress-test-engine.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `scenariostresstestingagent__save-portfolio-before-llm`. Labor: AI. Script called: `scripts/tools/scenariostresstestingagent__save-portfolio-before-llm.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/scenariostresstestingagent/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/scenariostresstestingagent-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Webhook Trigger | `webhook` | tool |
| 2 | Parse Input | `set` | gigo |
| 3 | Edit Fields | `set` | conductor |
| 4 | Validate Portfolio | `code` | conductor |
| 5 | Custom Scenario? | `if` | conductor |
| 6 | Load_Template_Scenario | `code` | conductor |
| 7 | When chat message received | `chatTrigger` | conductor |
| 8 | Basic LLM Chain | `chainLlm` | tool |
| 9 | Groq Chat Model | `lmChatGroq` | tool |
| 10 | Parse_LLM_Response | `code` | tool |
| 11 | Stress_Test_Engine | `code` | tool |
| 12 | Respond to Webhook | `respondToWebhook` | report |
| 13 | Fetch_Data | `httpRequest` | ingest |
| 14 | Merge | `merge` | conductor |
| 15 | Merge1 | `merge` | conductor |
| 16 | Save_Portfolio_Before_LLM | `code` | tool |

## Script Index

- `scripts/ingest/scenariostresstestingagent__fetch-data.py`
- `scripts/gigo/scenariostresstestingagent__parse-input.py`
- `scripts/tools/scenariostresstestingagent__webhook-trigger.py`
- `scripts/tools/scenariostresstestingagent__basic-llm-chain.py`
- `scripts/tools/scenariostresstestingagent__groq-chat-model.py`
- `scripts/tools/scenariostresstestingagent__parse-llm-response.py`
- `scripts/tools/scenariostresstestingagent__stress-test-engine.py`
- `scripts/tools/scenariostresstestingagent__save-portfolio-before-llm.py`

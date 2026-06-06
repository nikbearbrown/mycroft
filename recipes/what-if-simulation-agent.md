# What-If Simulation Agent

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (3 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (5 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/what-if-simulation-agent.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `what-if-simulation-agent__parse-validate-input`. Labor: AI. Script called: `scripts/gigo/what-if-simulation-agent__parse-validate-input.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `what-if-simulation-agent__parse-groq-response`. Labor: AI. Script called: `scripts/gigo/what-if-simulation-agent__parse-groq-response.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `what-if-simulation-agent__save-to-postgresql`. Labor: AI. Script called: `scripts/gigo/what-if-simulation-agent__save-to-postgresql.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `what-if-simulation-agent__webhook-receive-simulation-request`. Labor: AI. Script called: `scripts/tools/what-if-simulation-agent__webhook-receive-simulation-request.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `what-if-simulation-agent__sim-2-risk-appetite-simulator`. Labor: AI. Script called: `scripts/tools/what-if-simulation-agent__sim-2-risk-appetite-simulator.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `what-if-simulation-agent__aggregate-score-all-simulations`. Labor: AI. Script called: `scripts/tools/what-if-simulation-agent__aggregate-score-all-simulations.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `what-if-simulation-agent__groq-generate-investment-insights`. Labor: AI. Script called: `scripts/tools/what-if-simulation-agent__groq-generate-investment-insights.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `what-if-simulation-agent__build-ai-prompt`. Labor: AI. Script called: `scripts/tools/what-if-simulation-agent__build-ai-prompt.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/what-if-simulation-agent/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/what-if-simulation-agent-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | 🎯 Webhook — Receive Simulation Request | `webhook` | tool |
| 2 | 🔍 Parse & Validate Input | `code` | gigo |
| 3 | 📈 Sim 1 — Growth vs Sentiment Tradeoff | `code` | conductor |
| 4 | ⚖️ Sim 2 — Risk Appetite Simulator | `code` | tool |
| 5 | 🎯 Sim 3 — Threshold Break Simulator | `code` | conductor |
| 6 | 🧠 Aggregate & Score All Simulations | `code` | tool |
| 7 | 🤖 Groq — Generate Investment Insights | `httpRequest` | tool |
| 8 | 🔄 Parse Groq Response | `code` | gigo |
| 9 | 🗄️ Prepare DB Record | `code` | conductor |
| 10 | 💾 Save to PostgreSQL | `postgres` | gigo |
| 11 | 📊 Build Final Response | `code` | conductor |
| 12 | ✅ Respond to Webhook | `respondToWebhook` | report |
| 13 | 📝 Build AI Prompt | `code` | tool |

## Script Index

- `scripts/gigo/what-if-simulation-agent__parse-validate-input.py`
- `scripts/gigo/what-if-simulation-agent__parse-groq-response.py`
- `scripts/gigo/what-if-simulation-agent__save-to-postgresql.py`
- `scripts/tools/what-if-simulation-agent__webhook-receive-simulation-request.py`
- `scripts/tools/what-if-simulation-agent__sim-2-risk-appetite-simulator.py`
- `scripts/tools/what-if-simulation-agent__aggregate-score-all-simulations.py`
- `scripts/tools/what-if-simulation-agent__groq-generate-investment-insights.py`
- `scripts/tools/what-if-simulation-agent__build-ai-prompt.py`

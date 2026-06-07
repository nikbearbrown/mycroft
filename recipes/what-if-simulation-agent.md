# What-If Simulation Agent

## Purpose

What-If Simulation Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to what-if simulation agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| 🎯 Webhook — Receive Simulation Request | `webhook` | tool |
| 🔍 Parse & Validate Input | `code` | gigo |
| 📈 Sim 1 — Growth vs Sentiment Tradeoff | `code` | conductor |
| ⚖️ Sim 2 — Risk Appetite Simulator | `code` | tool |
| 🎯 Sim 3 — Threshold Break Simulator | `code` | conductor |
| 🧠 Aggregate & Score All Simulations | `code` | tool |
| 🤖 Groq — Generate Investment Insights | `httpRequest` | tool |
| 🔄 Parse Groq Response | `code` | gigo |
| 🗄️ Prepare DB Record | `code` | conductor |
| 💾 Save to PostgreSQL | `postgres` | gigo |
| 📊 Build Final Response | `code` | conductor |
| ✅ Respond to Webhook | `respondToWebhook` | report |
| 📝 Build AI Prompt | `code` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (3 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (5 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/what-if-simulation-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run what-if-simulation-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/what-if-simulation-agent data/verified/what-if-simulation-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/what-if-simulation-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: 🎯 Webhook — Receive Simulation Request. Labor: AI with Human gate.
   Script called: `scripts/tools/what-if-simulation-agent__webhook-receive-simulation-request.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: 🔍 Parse & Validate Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/what-if-simulation-agent__parse-and-validate-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/what-if-simulation-agent/.
4. Step name: ⚖️ Sim 2 — Risk Appetite Simulator. Labor: AI with Human gate.
   Script called: `scripts/tools/what-if-simulation-agent__sim-2-risk-appetite-simulator.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: 🧠 Aggregate & Score All Simulations. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/what-if-simulation-agent__aggregate-and-score-all-simulations.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: 🤖 Groq — Generate Investment Insights. Labor: AI with Human gate.
   Script called: `scripts/tools/what-if-simulation-agent__groq-generate-investment-insights.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: 🔄 Parse Groq Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/what-if-simulation-agent__parse-groq-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/what-if-simulation-agent/.
8. Step name: 💾 Save to PostgreSQL. Labor: AI with Human gate.
   Script called: `scripts/gigo/what-if-simulation-agent__save-to-postgresql.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/what-if-simulation-agent/.
9. Step name: ✅ Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/what-if-simulation-agent__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
10. Step name: 📝 Build AI Prompt. Labor: AI with Human gate.
   Script called: `scripts/tools/what-if-simulation-agent__build-ai-prompt.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/what-if-simulation-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/what-if-simulation-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/what-if-simulation-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `What-If Simulation Agent` run.
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
`snickerdoodle run what-if-simulation-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run what-if-simulation-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| 🎯 Webhook — Receive Simulation Request | `snickerdoodle run what-if-simulation-agent --step webhook-receive-simulation-request` | `--no-write` |
| 🔍 Parse & Validate Input | `snickerdoodle run what-if-simulation-agent --step parse-and-validate-input` |  |
| ⚖️ Sim 2 — Risk Appetite Simulator | `snickerdoodle run what-if-simulation-agent --step sim-2-risk-appetite-simulator` | `--no-write` |
| 🧠 Aggregate & Score All Simulations | `snickerdoodle run what-if-simulation-agent --step aggregate-and-score-all-simulations` | `--no-write` |
| 🤖 Groq — Generate Investment Insights | `snickerdoodle run what-if-simulation-agent --step groq-generate-investment-insights` | `--no-write` |
| 🔄 Parse Groq Response | `snickerdoodle run what-if-simulation-agent --step parse-groq-response` |  |
| 💾 Save to PostgreSQL | `snickerdoodle run what-if-simulation-agent --step save-to-postgresql` |  |
| ✅ Respond to Webhook | `snickerdoodle run what-if-simulation-agent --step respond-to-webhook` | `--no-write` |
| 📝 Build AI Prompt | `snickerdoodle run what-if-simulation-agent --step build-ai-prompt` | `--no-write` |
| Produce human report | `snickerdoodle run what-if-simulation-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate what-if-simulation-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate what-if-simulation-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate what-if-simulation-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| 🎯 Webhook — Receive Simulation Request | `scripts/tools/what-if-simulation-agent__webhook-receive-simulation-request.py` | tool |
| 🔍 Parse & Validate Input | `[TODO: DEV] Create or map script path: scripts/gigo/what-if-simulation-agent__parse-and-validate-input.py` | gigo |
| ⚖️ Sim 2 — Risk Appetite Simulator | `scripts/tools/what-if-simulation-agent__sim-2-risk-appetite-simulator.py` | tool |
| 🧠 Aggregate & Score All Simulations | `[TODO: DEV] Create or map script path: scripts/tools/what-if-simulation-agent__aggregate-and-score-all-simulations.py` | tool |
| 🤖 Groq — Generate Investment Insights | `scripts/tools/what-if-simulation-agent__groq-generate-investment-insights.py` | tool |
| 🔄 Parse Groq Response | `scripts/gigo/what-if-simulation-agent__parse-groq-response.py` | gigo |
| 💾 Save to PostgreSQL | `scripts/gigo/what-if-simulation-agent__save-to-postgresql.py` | gigo |
| ✅ Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/what-if-simulation-agent__respond-to-webhook.py` | tool |
| 📝 Build AI Prompt | `scripts/tools/what-if-simulation-agent__build-ai-prompt.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/what-if-simulation-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/what-if-simulation-agent/` | JSON |
| Verified data | `data/verified/what-if-simulation-agent/` | JSON |
| Agent log | `logs/what-if-simulation-agent-[DATE].json` | JSON |
| Human report | `reports/generated/what-if-simulation-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json`

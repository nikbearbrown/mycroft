# What-If Simulation Agent

## Purpose

What-If Simulation Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to what-if simulation agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| 🤖 Groq — Generate Investment Insights | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| 🎯 Webhook — Receive Simulation Request | webhook | conductor |
| 🔍 Parse & Validate Input | code | gigo |
| 📈 Sim 1 — Growth vs Sentiment Tradeoff | code | gigo |
| ⚖️ Sim 2 — Risk Appetite Simulator | code | gigo |
| 🎯 Sim 3 — Threshold Break Simulator | code | gigo |
| 🧠 Aggregate & Score All Simulations | code | gigo |
| 🤖 Groq — Generate Investment Insights | httpRequest | ingest |
| 🔄 Parse Groq Response | code | gigo |
| 🗄️ Prepare DB Record | code | tool |
| 💾 Save to PostgreSQL | postgres | gigo |
| 📊 Build Final Response | code | gigo |
| ✅ Respond to Webhook | respondToWebhook | conductor |
| 📝 Build AI Prompt | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-what-if-simulation-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-what-if-simulation-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-what-if-simulation-agent data/verified/n8n-what-if-simulation-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-what-if-simulation-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: 🔍 Parse & Validate Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__parse-and-validate-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
3. Step name: 📈 Sim 1 — Growth vs Sentiment Tradeoff. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__sim-1-growth-vs-sentiment-tradeoff.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
4. Step name: ⚖️ Sim 2 — Risk Appetite Simulator. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__sim-2-risk-appetite-simulator.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
5. Step name: 🎯 Sim 3 — Threshold Break Simulator. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__sim-3-threshold-break-simulator.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
6. Step name: 🧠 Aggregate & Score All Simulations. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__aggregate-and-score-all-simulations.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
7. Step name: 🤖 Groq — Generate Investment Insights. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-what-if-simulation-agent__groq-generate-investment-insights.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-what-if-simulation-agent/.
8. Step name: 🔄 Parse Groq Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__parse-groq-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
9. Step name: 🗄️ Prepare DB Record. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-what-if-simulation-agent__prepare-db-record.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: 💾 Save to PostgreSQL. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__save-to-postgresql.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
11. Step name: 📊 Build Final Response. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__build-final-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
12. Step name: 📝 Build AI Prompt. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__build-ai-prompt.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-what-if-simulation-agent/.
13. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-what-if-simulation-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-what-if-simulation-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-what-if-simulation-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `What-If Simulation Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-what-if-simulation-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-what-if-simulation-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| 🔍 Parse & Validate Input | `snickerdoodle run n8n-what-if-simulation-agent --step parse-and-validate-input` |  |
| 📈 Sim 1 — Growth vs Sentiment Tradeoff | `snickerdoodle run n8n-what-if-simulation-agent --step sim-1-growth-vs-sentiment-tradeoff` |  |
| ⚖️ Sim 2 — Risk Appetite Simulator | `snickerdoodle run n8n-what-if-simulation-agent --step sim-2-risk-appetite-simulator` |  |
| 🎯 Sim 3 — Threshold Break Simulator | `snickerdoodle run n8n-what-if-simulation-agent --step sim-3-threshold-break-simulator` |  |
| 🧠 Aggregate & Score All Simulations | `snickerdoodle run n8n-what-if-simulation-agent --step aggregate-and-score-all-simulations` |  |
| 🤖 Groq — Generate Investment Insights | `snickerdoodle run n8n-what-if-simulation-agent --step groq-generate-investment-insights` | `--sample` |
| 🔄 Parse Groq Response | `snickerdoodle run n8n-what-if-simulation-agent --step parse-groq-response` |  |
| 🗄️ Prepare DB Record | `snickerdoodle run n8n-what-if-simulation-agent --step prepare-db-record` | `--no-write` |
| 💾 Save to PostgreSQL | `snickerdoodle run n8n-what-if-simulation-agent --step save-to-postgresql` |  |
| 📊 Build Final Response | `snickerdoodle run n8n-what-if-simulation-agent --step build-final-response` |  |
| 📝 Build AI Prompt | `snickerdoodle run n8n-what-if-simulation-agent --step build-ai-prompt` |  |
| Produce human report | `snickerdoodle run n8n-what-if-simulation-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-what-if-simulation-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-what-if-simulation-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-what-if-simulation-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| 🔍 Parse & Validate Input | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__parse-and-validate-input.py` | gigo |
| 📈 Sim 1 — Growth vs Sentiment Tradeoff | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__sim-1-growth-vs-sentiment-tradeoff.py` | gigo |
| ⚖️ Sim 2 — Risk Appetite Simulator | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__sim-2-risk-appetite-simulator.py` | gigo |
| 🎯 Sim 3 — Threshold Break Simulator | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__sim-3-threshold-break-simulator.py` | gigo |
| 🧠 Aggregate & Score All Simulations | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__aggregate-and-score-all-simulations.py` | gigo |
| 🤖 Groq — Generate Investment Insights | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-what-if-simulation-agent__groq-generate-investment-insights.py` | ingest |
| 🔄 Parse Groq Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__parse-groq-response.py` | gigo |
| 🗄️ Prepare DB Record | `[TODO: DEV] Create or map script path: scripts/tools/n8n-what-if-simulation-agent__prepare-db-record.py` | tool |
| 💾 Save to PostgreSQL | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__save-to-postgresql.py` | gigo |
| 📊 Build Final Response | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__build-final-response.py` | gigo |
| 📝 Build AI Prompt | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-what-if-simulation-agent__build-ai-prompt.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-what-if-simulation-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-what-if-simulation-agent/` | JSON |
| Verified data | `data/verified/n8n-what-if-simulation-agent/` | JSON |
| Agent log | `logs/n8n-what-if-simulation-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-what-if-simulation-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json`

# Part1 -Investor_ Agent

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (3 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (2 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Part1 -Investor_ Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/part1-investor-agent.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `part1-investor-agent__db-get-recent-deals`. Labor: AI. Script called: `scripts/ingest/part1-investor-agent__db-get-recent-deals.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `part1-investor-agent__get-top-investor`. Labor: AI. Script called: `scripts/ingest/part1-investor-agent__get-top-investor.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `part1-investor-agent__parse-user-question`. Labor: AI. Script called: `scripts/gigo/part1-investor-agent__parse-user-question.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `part1-investor-agent__investor-profile-sql-node`. Labor: AI. Script called: `scripts/gigo/part1-investor-agent__investor-profile-sql-node.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `part1-investor-agent__startup-investors-sql-node`. Labor: AI. Script called: `scripts/gigo/part1-investor-agent__startup-investors-sql-node.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `part1-investor-agent__webhook-chat-interface`. Labor: AI. Script called: `scripts/tools/part1-investor-agent__webhook-chat-interface.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/part1-investor-agent/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/part1-investor-agent-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Investor_Intelligence/Part1 -Investor_ Agent.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Webhook - Chat Interface | `webhook` | tool |
| 2 | Parse User Question | `code` | gigo |
| 3 | DB - Get Recent Deals | `postgres` | ingest |
| 4 | Format Chatbot Response | `code` | conductor |
| 5 | Send Response | `respondToWebhook` | report |
| 6 | Get top investor | `postgres` | ingest |
| 7 | Route by Query Type  | `switch` | conductor |
| 8 | Investor Profile SQL node | `postgres` | gigo |
| 9 | Startup Investors SQL node | `postgres` | gigo |

## Script Index

- `scripts/ingest/part1-investor-agent__db-get-recent-deals.py`
- `scripts/ingest/part1-investor-agent__get-top-investor.py`
- `scripts/gigo/part1-investor-agent__parse-user-question.py`
- `scripts/gigo/part1-investor-agent__investor-profile-sql-node.py`
- `scripts/gigo/part1-investor-agent__startup-investors-sql-node.py`
- `scripts/tools/part1-investor-agent__webhook-chat-interface.py`

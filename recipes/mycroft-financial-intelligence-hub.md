# Mycroft - Financial Intelligence Hub

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (2 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (6 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (12 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroft-financial-intelligence-hub.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroft-financial-intelligence-hub__call-sec-workflow`. Labor: AI. Script called: `scripts/ingest/mycroft-financial-intelligence-hub__call-sec-workflow.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroft-financial-intelligence-hub__call-patent-workflow`. Labor: AI. Script called: `scripts/ingest/mycroft-financial-intelligence-hub__call-patent-workflow.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroft-financial-intelligence-hub__structured-output-parser`. Labor: AI. Script called: `scripts/gigo/mycroft-financial-intelligence-hub__structured-output-parser.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroft-financial-intelligence-hub__extract-from-file`. Labor: AI. Script called: `scripts/gigo/mycroft-financial-intelligence-hub__extract-from-file.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroft-financial-intelligence-hub__llm-chain-router`. Labor: AI. Script called: `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-router.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroft-financial-intelligence-hub__ollama-chat-model`. Labor: AI. Script called: `scripts/tools/mycroft-financial-intelligence-hub__ollama-chat-model.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroft-financial-intelligence-hub__llm-chain-analyst`. Labor: AI. Script called: `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-analyst.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroft-financial-intelligence-hub__ollama-analyst-model`. Labor: AI. Script called: `scripts/tools/mycroft-financial-intelligence-hub__ollama-analyst-model.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `mycroft-financial-intelligence-hub__log-analysis-complete`. Labor: AI. Script called: `scripts/tools/mycroft-financial-intelligence-hub__log-analysis-complete.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `mycroft-financial-intelligence-hub__read-write-files-from-disk`. Labor: AI. Script called: `scripts/tools/mycroft-financial-intelligence-hub__read-write-files-from-disk.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-financial-intelligence-hub/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroft-financial-intelligence-hub-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Financial_Intelligence_Hub/Mycroft - Financial Intelligence Hub.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | When chat message received | `chatTrigger` | conductor |
| 2 | Initialize Hub | `set` | conductor |
| 3 | Initialize Logging | `code` | conductor |
| 4 | LLM Chain Router | `chainLlm` | tool |
| 5 | Ollama Chat Model | `lmChatOllama` | tool |
| 6 | Call SEC? | `if` | conductor |
| 7 | Call Patent? | `if` | conductor |
| 8 | Call SEC Workflow | `httpRequest` | ingest |
| 9 | Call Patent Workflow | `httpRequest` | ingest |
| 10 | Log: SEC Called | `code` | conductor |
| 11 | Log: Patent Called | `code` | conductor |
| 12 | Aggregate Results | `code` | conductor |
| 13 | Log: Results Aggregated | `code` | conductor |
| 14 | LLM Chain Analyst | `chainLlm` | tool |
| 15 | Ollama Analyst Model | `lmChatOllama` | tool |
| 16 | Log: Analysis Complete | `code` | tool |
| 17 | Format Chat Response | `code` | conductor |
| 18 | Log: Complete | `code` | conductor |
| 19 | No Tools Needed | `code` | conductor |
| 20 | Structured Output Parser | `outputParserStructured` | gigo |
| 21 | Read/Write Files from Disk | `readWriteFile` | tool |
| 22 | Extract from File | `extractFromFile` | gigo |

## Script Index

- `scripts/ingest/mycroft-financial-intelligence-hub__call-sec-workflow.py`
- `scripts/ingest/mycroft-financial-intelligence-hub__call-patent-workflow.py`
- `scripts/gigo/mycroft-financial-intelligence-hub__structured-output-parser.py`
- `scripts/gigo/mycroft-financial-intelligence-hub__extract-from-file.py`
- `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-router.py`
- `scripts/tools/mycroft-financial-intelligence-hub__ollama-chat-model.py`
- `scripts/tools/mycroft-financial-intelligence-hub__llm-chain-analyst.py`
- `scripts/tools/mycroft-financial-intelligence-hub__ollama-analyst-model.py`
- `scripts/tools/mycroft-financial-intelligence-hub__log-analysis-complete.py`
- `scripts/tools/mycroft-financial-intelligence-hub__read-write-files-from-disk.py`

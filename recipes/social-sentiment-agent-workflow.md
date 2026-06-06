# workflow

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (5 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (3 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (6 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/social-sentiment-agent-workflow.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `social-sentiment-agent-workflow__get-stackoverflow`. Labor: AI. Script called: `scripts/ingest/social-sentiment-agent-workflow__get-stackoverflow.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `social-sentiment-agent-workflow__get-reddit-ml`. Labor: AI. Script called: `scripts/ingest/social-sentiment-agent-workflow__get-reddit-ml.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `social-sentiment-agent-workflow__get-github`. Labor: AI. Script called: `scripts/ingest/social-sentiment-agent-workflow__get-github.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `social-sentiment-agent-workflow__process-stackoverflow`. Labor: AI. Script called: `scripts/gigo/social-sentiment-agent-workflow__process-stackoverflow.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `social-sentiment-agent-workflow__process-reddit-ml`. Labor: AI. Script called: `scripts/gigo/social-sentiment-agent-workflow__process-reddit-ml.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `social-sentiment-agent-workflow__process-github`. Labor: AI. Script called: `scripts/gigo/social-sentiment-agent-workflow__process-github.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `social-sentiment-agent-workflow__process-groq-sentiment`. Labor: AI. Script called: `scripts/gigo/social-sentiment-agent-workflow__process-groq-sentiment.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `social-sentiment-agent-workflow__signal-to-noise-filter`. Labor: AI. Script called: `scripts/gigo/social-sentiment-agent-workflow__signal-to-noise-filter.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `social-sentiment-agent-workflow__groq-llm-sentiment`. Labor: AI. Script called: `scripts/tools/social-sentiment-agent-workflow__groq-llm-sentiment.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `social-sentiment-agent-workflow__groq-topic-classification`. Labor: AI. Script called: `scripts/tools/social-sentiment-agent-workflow__groq-topic-classification.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `social-sentiment-agent-workflow__store-in-google-sheets`. Labor: AI. Script called: `scripts/tools/social-sentiment-agent-workflow__store-in-google-sheets.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/social-sentiment-agent-workflow/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/social-sentiment-agent-workflow-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Social_Sentiment_Agent/workflow.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Process StackOverflow | `function` | gigo |
| 2 | Get StackOverflow | `httpRequest` | ingest |
| 3 | Manual Trigger | `manualTrigger` | conductor |
| 4 | Combine All Data | `function` | conductor |
| 5 | Process Reddit ML | `function` | gigo |
| 6 | Get Reddit ML | `httpRequest` | ingest |
| 7 | Process GitHub | `function` | gigo |
| 8 | Get GitHub | `httpRequest` | ingest |
| 9 | Groq LLM Sentiment | `httpRequest` | tool |
| 10 | Process Groq Sentiment | `function` | gigo |
| 11 | Groq Topic Classification | `httpRequest` | tool |
| 12 | Topic Clustering Engine | `function` | conductor |
| 13 | Signal-to-Noise Filter | `function` | gigo |
| 14 | Social Sentiment Output | `function` | conductor |
| 15 | Enhanced Data Export | `function` | conductor |
| 16 | Prepare for Google Sheets | `function` | conductor |
| 17 | Store in Google Sheets | `googleSheets` | tool |

## Script Index

- `scripts/ingest/social-sentiment-agent-workflow__get-stackoverflow.py`
- `scripts/ingest/social-sentiment-agent-workflow__get-reddit-ml.py`
- `scripts/ingest/social-sentiment-agent-workflow__get-github.py`
- `scripts/gigo/social-sentiment-agent-workflow__process-stackoverflow.py`
- `scripts/gigo/social-sentiment-agent-workflow__process-reddit-ml.py`
- `scripts/gigo/social-sentiment-agent-workflow__process-github.py`
- `scripts/gigo/social-sentiment-agent-workflow__process-groq-sentiment.py`
- `scripts/gigo/social-sentiment-agent-workflow__signal-to-noise-filter.py`
- `scripts/tools/social-sentiment-agent-workflow__groq-llm-sentiment.py`
- `scripts/tools/social-sentiment-agent-workflow__groq-topic-classification.py`
- `scripts/tools/social-sentiment-agent-workflow__store-in-google-sheets.py`

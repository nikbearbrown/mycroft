# My workflow 4

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (13 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/my-workflow-4-2.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `my-workflow-4-2__github-get-repos`. Labor: AI. Script called: `scripts/ingest/my-workflow-4-2__github-get-repos.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `my-workflow-4-2__github-get-languages`. Labor: AI. Script called: `scripts/ingest/my-workflow-4-2__github-get-languages.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `my-workflow-4-2__arxiv-search-papers`. Labor: AI. Script called: `scripts/ingest/my-workflow-4-2__arxiv-search-papers.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `my-workflow-4-2__parse-arxiv-xml`. Labor: AI. Script called: `scripts/gigo/my-workflow-4-2__parse-arxiv-xml.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/my-workflow-4-2/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/my-workflow-4-2-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Prepare Variables | `set` | conductor |
| 2 | GitHub: Get Repos | `httpRequest` | ingest |
| 3 | Batch Repos | `splitInBatches` | conductor |
| 4 | GitHub: Get Languages | `httpRequest` | ingest |
| 5 | Aggregate Repo Data | `set` | conductor |
| 6 | arXiv: Search Papers | `httpRequest` | ingest |
| 7 | Parse arXiv XML | `code` | gigo |
| 8 | Manual Trigger | `manualTrigger` | conductor |
| 9 | Input: Companies | `set` | conductor |
| 10 | Format Language Data | `set` | conductor |
| 11 | Format Research Data | `set` | conductor |
| 12 | Code | `code` | conductor |
| 13 | Code1 | `code` | conductor |
| 14 | Code2 | `code` | conductor |
| 15 | Code3 | `code` | conductor |
| 16 | Code4 | `code` | conductor |
| 17 | Code5 | `code` | conductor |

## Script Index

- `scripts/ingest/my-workflow-4-2__github-get-repos.py`
- `scripts/ingest/my-workflow-4-2__github-get-languages.py`
- `scripts/ingest/my-workflow-4-2__arxiv-search-papers.py`
- `scripts/gigo/my-workflow-4-2__parse-arxiv-xml.py`

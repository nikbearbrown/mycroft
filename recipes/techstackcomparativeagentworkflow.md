# TechStackComparativeAgentWorkflow

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (3 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (12 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/techstackcomparativeagentworkflow.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `techstackcomparativeagentworkflow__github-get-repos`. Labor: AI. Script called: `scripts/ingest/techstackcomparativeagentworkflow__github-get-repos.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `techstackcomparativeagentworkflow__github-get-languages`. Labor: AI. Script called: `scripts/ingest/techstackcomparativeagentworkflow__github-get-languages.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `techstackcomparativeagentworkflow__arxiv-search-papers`. Labor: AI. Script called: `scripts/ingest/techstackcomparativeagentworkflow__arxiv-search-papers.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `techstackcomparativeagentworkflow__parse-arxiv-xml`. Labor: AI. Script called: `scripts/gigo/techstackcomparativeagentworkflow__parse-arxiv-xml.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `techstackcomparativeagentworkflow__split-out`. Labor: AI. Script called: `scripts/gigo/techstackcomparativeagentworkflow__split-out.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `techstackcomparativeagentworkflow__convert-to-file`. Labor: AI. Script called: `scripts/gigo/techstackcomparativeagentworkflow__convert-to-file.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/techstackcomparativeagentworkflow/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/techstackcomparativeagentworkflow-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/TechStackComparativeAgentWorkflow.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Validate Input | `if` | conductor |
| 2 | Prepare Variables | `set` | conductor |
| 3 | GitHub: Get Repos | `httpRequest` | ingest |
| 4 | Batch Repos (Top 5) | `splitInBatches` | conductor |
| 5 | GitHub: Get Languages | `httpRequest` | ingest |
| 6 | Aggregate Repo Data | `set` | conductor |
| 7 | arXiv: Search Papers | `httpRequest` | ingest |
| 8 | Error: Invalid Input | `set` | conductor |
| 9 | Parse arXiv XML | `code` | gigo |
| 10 | When clicking ‘Execute workflow’ | `manualTrigger` | conductor |
| 11 | Split Out | `splitOut` | gigo |
| 12 | set | `set` | conductor |
| 13 | set1 | `set` | conductor |
| 14 | Convert to File | `convertToFile` | gigo |
| 15 | Edit Fields | `set` | conductor |
| 16 | Edit Fields1 | `set` | conductor |
| 17 | Code | `code` | conductor |
| 18 | Edit Fields2 | `set` | conductor |

## Script Index

- `scripts/ingest/techstackcomparativeagentworkflow__github-get-repos.py`
- `scripts/ingest/techstackcomparativeagentworkflow__github-get-languages.py`
- `scripts/ingest/techstackcomparativeagentworkflow__arxiv-search-papers.py`
- `scripts/gigo/techstackcomparativeagentworkflow__parse-arxiv-xml.py`
- `scripts/gigo/techstackcomparativeagentworkflow__split-out.py`
- `scripts/gigo/techstackcomparativeagentworkflow__convert-to-file.py`

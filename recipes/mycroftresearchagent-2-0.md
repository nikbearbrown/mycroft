# MycroftResearchAgent_2.0

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (4 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (4 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (3 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (3 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/mycroftresearchagent-2-0.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `mycroftresearchagent-2-0__get-financial-overview1`. Labor: AI. Script called: `scripts/ingest/mycroftresearchagent-2-0__get-financial-overview1.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `mycroftresearchagent-2-0__get-income-statement1`. Labor: AI. Script called: `scripts/ingest/mycroftresearchagent-2-0__get-income-statement1.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `mycroftresearchagent-2-0__google-search-patent`. Labor: AI. Script called: `scripts/ingest/mycroftresearchagent-2-0__google-search-patent.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `mycroftresearchagent-2-0__get-earnings-data`. Labor: AI. Script called: `scripts/ingest/mycroftresearchagent-2-0__get-earnings-data.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `mycroftresearchagent-2-0__process-company-data1`. Labor: AI. Script called: `scripts/gigo/mycroftresearchagent-2-0__process-company-data1.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `mycroftresearchagent-2-0__process-patent-data1`. Labor: AI. Script called: `scripts/gigo/mycroftresearchagent-2-0__process-patent-data1.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `mycroftresearchagent-2-0__process-financial-data1`. Labor: AI. Script called: `scripts/gigo/mycroftresearchagent-2-0__process-financial-data1.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `mycroftresearchagent-2-0__process-earnings-data`. Labor: AI. Script called: `scripts/gigo/mycroftresearchagent-2-0__process-earnings-data.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `mycroftresearchagent-2-0__generate-analysis1`. Labor: AI. Script called: `scripts/tools/mycroftresearchagent-2-0__generate-analysis1.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `mycroftresearchagent-2-0__get-competitive-analysis`. Labor: AI. Script called: `scripts/tools/mycroftresearchagent-2-0__get-competitive-analysis.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `mycroftresearchagent-2-0__merge-competitive-analysis`. Labor: AI. Script called: `scripts/tools/mycroftresearchagent-2-0__merge-competitive-analysis.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroftresearchagent-2-0/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/mycroftresearchagent-2-0-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Research_Analytics_Agent/ResearchAgent_2.0.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | When clicking ‘Execute workflow’ | `manualTrigger` | conductor |
| 2 | Company Input | `set` | conductor |
| 3 | Get Financial Overview1 | `httpRequest` | ingest |
| 4 | Get Income Statement1 | `httpRequest` | ingest |
| 5 | Process Company Data1 | `code` | gigo |
| 6 | Google Search Patent | `httpRequest` | ingest |
| 7 | Process Patent Data1 | `code` | gigo |
| 8 | Process Financial Data1 | `code` | gigo |
| 9 | Generate Analysis1 | `code` | tool |
| 10 | Generate Final Report1 | `code` | report |
| 11 | Merge | `merge` | conductor |
| 12 | Get Earnings Data | `httpRequest` | ingest |
| 13 | Process Earnings Data | `code` | gigo |
| 14 | Get Competitive Analysis | `code` | tool |
| 15 | Merge Competitive Analysis | `code` | tool |
| 16 | Investment Report | `code` | report |

## Script Index

- `scripts/ingest/mycroftresearchagent-2-0__get-financial-overview1.py`
- `scripts/ingest/mycroftresearchagent-2-0__get-income-statement1.py`
- `scripts/ingest/mycroftresearchagent-2-0__google-search-patent.py`
- `scripts/ingest/mycroftresearchagent-2-0__get-earnings-data.py`
- `scripts/gigo/mycroftresearchagent-2-0__process-company-data1.py`
- `scripts/gigo/mycroftresearchagent-2-0__process-patent-data1.py`
- `scripts/gigo/mycroftresearchagent-2-0__process-financial-data1.py`
- `scripts/gigo/mycroftresearchagent-2-0__process-earnings-data.py`
- `scripts/tools/mycroftresearchagent-2-0__generate-analysis1.py`
- `scripts/tools/mycroftresearchagent-2-0__get-competitive-analysis.py`
- `scripts/tools/mycroftresearchagent-2-0__merge-competitive-analysis.py`

# My workflow

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/my-workflow.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `my-workflow__http-request-repo-metadata`. Labor: AI. Script called: `scripts/ingest/my-workflow__http-request-repo-metadata.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `my-workflow__code-split-into-items`. Labor: AI. Script called: `scripts/gigo/my-workflow__code-split-into-items.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `my-workflow__code-parse-owner-repo`. Labor: AI. Script called: `scripts/gigo/my-workflow__code-parse-owner-repo.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `my-workflow__read-write-files-from-disk`. Labor: AI. Script called: `scripts/tools/my-workflow__read-write-files-from-disk.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/my-workflow/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/my-workflow-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Manual Trigger | `manualTrigger` | conductor |
| 2 | Set (Targets) | `set` | conductor |
| 3 | Code (Split into items) | `code` | gigo |
| 4 | Code (Parse owner/repo) | `code` | gigo |
| 5 | HTTP Request (Repo Metadata) | `httpRequest` | ingest |
| 6 | Code (Build profile JSON) | `code` | conductor |
| 7 | Code (JSON → Binary) | `code` | conductor |
| 8 | Read/Write Files from Disk | `readWriteFile` | tool |

## Script Index

- `scripts/ingest/my-workflow__http-request-repo-metadata.py`
- `scripts/gigo/my-workflow__code-split-into-items.py`
- `scripts/gigo/my-workflow__code-parse-owner-repo.py`
- `scripts/tools/my-workflow__read-write-files-from-disk.py`

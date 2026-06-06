# Retail Investor Anxiety Index

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (4 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (13 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (9 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/retail-investor-anxiety-index.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `retail-investor-anxiety-index__fetch-wsb`. Labor: AI. Script called: `scripts/ingest/retail-investor-anxiety-index__fetch-wsb.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `retail-investor-anxiety-index__fetch-investing`. Labor: AI. Script called: `scripts/ingest/retail-investor-anxiety-index__fetch-investing.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `retail-investor-anxiety-index__fetch-stocks`. Labor: AI. Script called: `scripts/ingest/retail-investor-anxiety-index__fetch-stocks.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `retail-investor-anxiety-index__insert-to-supabase`. Labor: AI. Script called: `scripts/ingest/retail-investor-anxiety-index__insert-to-supabase.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `retail-investor-anxiety-index__1a-raw-merge-structural-clean`. Labor: AI. Script called: `scripts/gigo/retail-investor-anxiety-index__1a-raw-merge-structural-clean.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `retail-investor-anxiety-index__1b-linguistic-relevance-filter`. Labor: AI. Script called: `scripts/gigo/retail-investor-anxiety-index__1b-linguistic-relevance-filter.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `retail-investor-anxiety-index__manual-run-trigger`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__manual-run-trigger.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `retail-investor-anxiety-index__keyword-pre-scorer`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__keyword-pre-scorer.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `retail-investor-anxiety-index__claude-1-anxiety-score`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__claude-1-anxiety-score.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `retail-investor-anxiety-index__claude-2-narrative-velocity`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__claude-2-narrative-velocity.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `retail-investor-anxiety-index__claude-3-herd-detection`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__claude-3-herd-detection.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: `retail-investor-anxiety-index__claude-4-conviction-vs-uncertainty`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__claude-4-conviction-vs-uncertainty.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
13. Step name: `retail-investor-anxiety-index__claude-5-crowd-cycle-stage`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__claude-5-crowd-cycle-stage.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
14. Step name: `retail-investor-anxiety-index__anthropic-model-1`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-1.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
15. Step name: `retail-investor-anxiety-index__anthropic-model-2`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-2.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
16. Step name: `retail-investor-anxiety-index__anthropic-model-3`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-3.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
17. Step name: `retail-investor-anxiety-index__anthropic-model-4`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-4.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
18. Step name: `retail-investor-anxiety-index__anthropic-model-5`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__anthropic-model-5.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
19. Step name: `retail-investor-anxiety-index__dashboard-webhook`. Labor: AI. Script called: `scripts/tools/retail-investor-anxiety-index__dashboard-webhook.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
20. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/retail-investor-anxiety-index/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/retail-investor-anxiety-index-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Retail_Investor_Anxiety_Index/workflow.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Schedule Trigger | `scheduleTrigger` | conductor |
| 2 | Manual Run Trigger | `webhook` | tool |
| 3 | Fetch WSB | `httpRequest` | ingest |
| 4 | Fetch Investing | `httpRequest` | ingest |
| 5 | Fetch Stocks | `httpRequest` | ingest |
| 6 | Merge Reddit Feeds | `merge` | conductor |
| 7 | 1A: Raw Merge & Structural Clean | `code` | gigo |
| 8 | 1B: Linguistic & Relevance Filter | `code` | gigo |
| 9 | Keyword Pre-Scorer | `code` | tool |
| 10 | Aggregate for Claude | `code` | conductor |
| 11 | Claude 1: Anxiety Score | `chainLlm` | tool |
| 12 | Claude 2: Narrative Velocity | `chainLlm` | tool |
| 13 | Claude 3: Herd Detection | `chainLlm` | tool |
| 14 | Claude 4: Conviction vs Uncertainty | `chainLlm` | tool |
| 15 | Claude 5: Crowd Cycle Stage | `chainLlm` | tool |
| 16 | Anthropic Model 1 | `lmChatAnthropic` | tool |
| 17 | Anthropic Model 2 | `lmChatAnthropic` | tool |
| 18 | Anthropic Model 3 | `lmChatAnthropic` | tool |
| 19 | Anthropic Model 4 | `lmChatAnthropic` | tool |
| 20 | Anthropic Model 5 | `lmChatAnthropic` | tool |
| 21 | Merge Claude Outputs | `merge` | conductor |
| 22 | Signal Aggregator | `code` | conductor |
| 23 | Persist to File | `code` | conductor |
| 24 | Generate Quickchart URLs | `code` | conductor |
| 25 | Write output.json | `code` | conductor |
| 26 | Insert to Supabase | `httpRequest` | ingest |
| 27 | Pipeline Response | `respondToWebhook` | report |
| 28 | Dashboard Webhook | `webhook` | tool |
| 29 | Build Dashboard Response | `code` | conductor |
| 30 | Serve Dashboard HTML | `respondToWebhook` | report |

## Script Index

- `scripts/ingest/retail-investor-anxiety-index__fetch-wsb.py`
- `scripts/ingest/retail-investor-anxiety-index__fetch-investing.py`
- `scripts/ingest/retail-investor-anxiety-index__fetch-stocks.py`
- `scripts/ingest/retail-investor-anxiety-index__insert-to-supabase.py`
- `scripts/gigo/retail-investor-anxiety-index__1a-raw-merge-structural-clean.py`
- `scripts/gigo/retail-investor-anxiety-index__1b-linguistic-relevance-filter.py`
- `scripts/tools/retail-investor-anxiety-index__manual-run-trigger.py`
- `scripts/tools/retail-investor-anxiety-index__keyword-pre-scorer.py`
- `scripts/tools/retail-investor-anxiety-index__claude-1-anxiety-score.py`
- `scripts/tools/retail-investor-anxiety-index__claude-2-narrative-velocity.py`
- `scripts/tools/retail-investor-anxiety-index__claude-3-herd-detection.py`
- `scripts/tools/retail-investor-anxiety-index__claude-4-conviction-vs-uncertainty.py`
- `scripts/tools/retail-investor-anxiety-index__claude-5-crowd-cycle-stage.py`
- `scripts/tools/retail-investor-anxiety-index__anthropic-model-1.py`
- `scripts/tools/retail-investor-anxiety-index__anthropic-model-2.py`
- `scripts/tools/retail-investor-anxiety-index__anthropic-model-3.py`
- `scripts/tools/retail-investor-anxiety-index__anthropic-model-4.py`
- `scripts/tools/retail-investor-anxiety-index__anthropic-model-5.py`
- `scripts/tools/retail-investor-anxiety-index__dashboard-webhook.py`

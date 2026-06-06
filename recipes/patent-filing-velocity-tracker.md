# Patent Filing Velocity Tracker

## Purpose

This recipe converts the original n8n workflow into a repeatable Mycroft workflow that can be run in dialogic mode with local data first, credential-gated live calls second, and human review before any external side effect or analytical conclusion is trusted.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (13 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (7 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No for local mode |

## Phase Gates

1. Source gate: all required local exports or live-call handoff specs must be present. Verification: run the generated ingest scripts for this workflow and confirm each returns JSON with a status field. Human capacity required: [PA], [TO].
2. GIGO gate: normalized records must preserve missing fields rather than inventing values. Verification: run generated GIGO scripts and inspect `record_count` and `records`. Human capacity required: [PA].
3. Tool gate: model/API/tool nodes must return local deterministic outputs or approval-required handoff specs. Verification: run generated tool scripts and confirm `live_call_performed` is false unless explicitly approved. Human capacity required: [TO], [IJ].
4. Report gate: final report must separate source facts, transformations, and interpretation. Verification: fill `reports/templates/patent-filing-velocity-tracker.md` and link the run log. Human capacity required: [EI].

## Steps

1. Step name: `patent-filing-velocity-tracker__insert-to-supabase`. Labor: AI. Script called: `scripts/ingest/patent-filing-velocity-tracker__insert-to-supabase.py`. Input: prior verified payloads or local export. Output: ingest result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
2. Step name: `patent-filing-velocity-tracker__1a-structural-clean`. Labor: AI. Script called: `scripts/gigo/patent-filing-velocity-tracker__1a-structural-clean.py`. Input: prior verified payloads or local export. Output: gigo result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
3. Step name: `patent-filing-velocity-tracker__manual-run-trigger`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__manual-run-trigger.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
4. Step name: `patent-filing-velocity-tracker__dashboard-webhook`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__dashboard-webhook.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
5. Step name: `patent-filing-velocity-tracker__1b-category-classifier-velocity-pre-scorer`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__1b-category-classifier-velocity-pre-scorer.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
6. Step name: `patent-filing-velocity-tracker__claude-1-velocity-score`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__claude-1-velocity-score.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
7. Step name: `patent-filing-velocity-tracker__claude-2-concept-novelty`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__claude-2-concept-novelty.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
8. Step name: `patent-filing-velocity-tracker__claude-3-inventor-network`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__claude-3-inventor-network.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
9. Step name: `patent-filing-velocity-tracker__claude-4-cross-company-convergence`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__claude-4-cross-company-convergence.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
10. Step name: `patent-filing-velocity-tracker__claude-5-strategic-intent`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__claude-5-strategic-intent.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
11. Step name: `patent-filing-velocity-tracker__anthropic-model-1`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-1.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
12. Step name: `patent-filing-velocity-tracker__anthropic-model-2`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-2.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
13. Step name: `patent-filing-velocity-tracker__anthropic-model-3`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-3.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
14. Step name: `patent-filing-velocity-tracker__anthropic-model-4`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-4.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
15. Step name: `patent-filing-velocity-tracker__anthropic-model-5`. Labor: AI. Script called: `scripts/tools/patent-filing-velocity-tracker__anthropic-model-5.py`. Input: prior verified payloads or local export. Output: tool result payload. Where output goes: `data/raw/`, `data/verified/`, or `logs/` as appropriate.
16. Step name: Human review. Labor: Human. Human action required: review source coverage, missing credentials, model/database/email handoffs, and interpretation limits. Input: generated logs and reports. Output: accept, reject, or rerun decision. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/patent-filing-velocity-tracker/<run-id>.json`. It must include source workflow path, scripts used, node classifications, credential status, live-call status, validation results, output paths, stop conditions, and human decisions.

### Human report

The human report goes to `reports/generated/patent-filing-velocity-tracker-<date>.md`. It surfaces the workflow result, source coverage, missing data, anomalies, and decisions required before downstream use.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Patent_Filing_Velocity_Tracker/workflow.json`

## Node Classification

| Order | Node Name | Node Type | Classification |
|---|---|---|---|
| 1 | Manual Run Trigger | `webhook` | tool |
| 2 | Dashboard Webhook | `webhook` | tool |
| 3 | Fetch Patent Data | `code` | conductor |
| 4 | 1A: Structural Clean | `code` | gigo |
| 5 | 1B: Category Classifier + Velocity Pre-Scorer | `code` | tool |
| 6 | Aggregate for Claude | `code` | conductor |
| 7 | Claude 1: Velocity Score | `chainLlm` | tool |
| 8 | Claude 2: Concept Novelty | `chainLlm` | tool |
| 9 | Claude 3: Inventor Network | `chainLlm` | tool |
| 10 | Claude 4: Cross-Company Convergence | `chainLlm` | tool |
| 11 | Claude 5: Strategic Intent | `chainLlm` | tool |
| 12 | Anthropic Model 1 | `lmChatAnthropic` | tool |
| 13 | Anthropic Model 2 | `lmChatAnthropic` | tool |
| 14 | Anthropic Model 3 | `lmChatAnthropic` | tool |
| 15 | Anthropic Model 4 | `lmChatAnthropic` | tool |
| 16 | Anthropic Model 5 | `lmChatAnthropic` | tool |
| 17 | Merge Claude Outputs | `merge` | conductor |
| 18 | Signal Aggregator | `code` | conductor |
| 19 | Insert to Supabase | `httpRequest` | ingest |
| 20 | Check Trigger Type | `code` | conductor |
| 21 | If Webhook | `if` | conductor |
| 22 | Pipeline Response | `respondToWebhook` | report |
| 23 | Build Dashboard HTML | `code` | conductor |
| 24 | Serve Dashboard HTML | `respondToWebhook` | report |

## Script Index

- `scripts/ingest/patent-filing-velocity-tracker__insert-to-supabase.py`
- `scripts/gigo/patent-filing-velocity-tracker__1a-structural-clean.py`
- `scripts/tools/patent-filing-velocity-tracker__manual-run-trigger.py`
- `scripts/tools/patent-filing-velocity-tracker__dashboard-webhook.py`
- `scripts/tools/patent-filing-velocity-tracker__1b-category-classifier-velocity-pre-scorer.py`
- `scripts/tools/patent-filing-velocity-tracker__claude-1-velocity-score.py`
- `scripts/tools/patent-filing-velocity-tracker__claude-2-concept-novelty.py`
- `scripts/tools/patent-filing-velocity-tracker__claude-3-inventor-network.py`
- `scripts/tools/patent-filing-velocity-tracker__claude-4-cross-company-convergence.py`
- `scripts/tools/patent-filing-velocity-tracker__claude-5-strategic-intent.py`
- `scripts/tools/patent-filing-velocity-tracker__anthropic-model-1.py`
- `scripts/tools/patent-filing-velocity-tracker__anthropic-model-2.py`
- `scripts/tools/patent-filing-velocity-tracker__anthropic-model-3.py`
- `scripts/tools/patent-filing-velocity-tracker__anthropic-model-4.py`
- `scripts/tools/patent-filing-velocity-tracker__anthropic-model-5.py`

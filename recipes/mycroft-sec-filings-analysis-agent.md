# Mycroft - SEC Filings Analysis Agent

## Purpose

Mycroft - SEC Filings Analysis Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - sec filings analysis agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| If | `if` | conductor |
| Set Variables | `set` | conductor |
| Setup Github Repo | `executeCommand` | tool |
| Set Path Variables | `code` | conductor |
| Setup Python Enviornment and Output Directories | `executeCommand` | tool |
| Edgar_Fetcher | `executeCommand` | tool |
| Validate Fetcher | `code` | conductor |
| Financial Analyzer | `executeCommand` | tool |
| Narrative Parser | `executeCommand` | tool |
| Error Handling | `code` | conductor |
| Cleanup | `executeCommand` | tool |
| Webhook | `webhook` | tool |
| Respond to Webhook | `respondToWebhook` | report |
| If1 | `if` | conductor |
| Respond to Webhook1 | `respondToWebhook` | report |
| Read/Write Files from Disk | `readWriteFile` | tool |
| Read/Write Files from Disk1 | `readWriteFile` | tool |
| Parse Results | `code` | gigo |
| Parse Both Results | `code` | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (9 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (6 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-sec-filings-analysis-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run mycroft-sec-filings-analysis-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/mycroft-sec-filings-analysis-agent data/verified/mycroft-sec-filings-analysis-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/mycroft-sec-filings-analysis-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Setup Python Enviornment and Output Directories. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__setup-python-enviornment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Edgar_Fetcher. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__edgar-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Financial Analyzer. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__financial-analyzer.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Narrative Parser. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__narrative-parser.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Cleanup. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__cleanup.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Webhook. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__webhook.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-agent__respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
10. Step name: Respond to Webhook1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-agent__respond-to-webhook1.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
11. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
12. Step name: Read/Write Files from Disk1. Labor: AI with Human gate.
   Script called: `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Parse Results. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-results.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-sec-filings-analysis-agent/.
14. Step name: Parse Both Results. Labor: AI with Human gate.
   Script called: `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-both-results.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/mycroft-sec-filings-analysis-agent/.
15. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/mycroft-sec-filings-analysis-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/mycroft-sec-filings-analysis-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - SEC Filings Analysis Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run mycroft-sec-filings-analysis-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run mycroft-sec-filings-analysis-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Setup Github Repo | `snickerdoodle run mycroft-sec-filings-analysis-agent --step setup-github-repo` | `--no-write` |
| Setup Python Enviornment and Output Directories | `snickerdoodle run mycroft-sec-filings-analysis-agent --step setup-python-enviornment-and-output-directories` | `--no-write` |
| Edgar_Fetcher | `snickerdoodle run mycroft-sec-filings-analysis-agent --step edgar-fetcher` | `--no-write` |
| Financial Analyzer | `snickerdoodle run mycroft-sec-filings-analysis-agent --step financial-analyzer` | `--no-write` |
| Narrative Parser | `snickerdoodle run mycroft-sec-filings-analysis-agent --step narrative-parser` | `--no-write` |
| Cleanup | `snickerdoodle run mycroft-sec-filings-analysis-agent --step cleanup` | `--no-write` |
| Webhook | `snickerdoodle run mycroft-sec-filings-analysis-agent --step webhook` | `--no-write` |
| Respond to Webhook | `snickerdoodle run mycroft-sec-filings-analysis-agent --step respond-to-webhook` | `--no-write` |
| Respond to Webhook1 | `snickerdoodle run mycroft-sec-filings-analysis-agent --step respond-to-webhook1` | `--no-write` |
| Read/Write Files from Disk | `snickerdoodle run mycroft-sec-filings-analysis-agent --step read-write-files-from-disk` | `--no-write` |
| Read/Write Files from Disk1 | `snickerdoodle run mycroft-sec-filings-analysis-agent --step read-write-files-from-disk1` | `--no-write` |
| Parse Results | `snickerdoodle run mycroft-sec-filings-analysis-agent --step parse-results` |  |
| Parse Both Results | `snickerdoodle run mycroft-sec-filings-analysis-agent --step parse-both-results` |  |
| Produce human report | `snickerdoodle run mycroft-sec-filings-analysis-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate mycroft-sec-filings-analysis-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate mycroft-sec-filings-analysis-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate mycroft-sec-filings-analysis-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Setup Github Repo | `scripts/tools/mycroft-sec-filings-analysis-agent__setup-github-repo.py` | tool |
| Setup Python Enviornment and Output Directories | `scripts/tools/mycroft-sec-filings-analysis-agent__setup-python-enviornment-and-output-directories.py` | tool |
| Edgar_Fetcher | `scripts/tools/mycroft-sec-filings-analysis-agent__edgar-fetcher.py` | tool |
| Financial Analyzer | `scripts/tools/mycroft-sec-filings-analysis-agent__financial-analyzer.py` | tool |
| Narrative Parser | `scripts/tools/mycroft-sec-filings-analysis-agent__narrative-parser.py` | tool |
| Cleanup | `scripts/tools/mycroft-sec-filings-analysis-agent__cleanup.py` | tool |
| Webhook | `scripts/tools/mycroft-sec-filings-analysis-agent__webhook.py` | tool |
| Respond to Webhook | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-agent__respond-to-webhook.py` | tool |
| Respond to Webhook1 | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-agent__respond-to-webhook1.py` | tool |
| Read/Write Files from Disk | `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk.py` | tool |
| Read/Write Files from Disk1 | `scripts/tools/mycroft-sec-filings-analysis-agent__read-write-files-from-disk1.py` | tool |
| Parse Results | `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-results.py` | gigo |
| Parse Both Results | `scripts/gigo/mycroft-sec-filings-analysis-agent__parse-both-results.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/mycroft-sec-filings-analysis-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/mycroft-sec-filings-analysis-agent/` | JSON |
| Verified data | `data/verified/mycroft-sec-filings-analysis-agent/` | JSON |
| Agent log | `logs/mycroft-sec-filings-analysis-agent-[DATE].json` | JSON |
| Human report | `reports/generated/mycroft-sec-filings-analysis-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json`

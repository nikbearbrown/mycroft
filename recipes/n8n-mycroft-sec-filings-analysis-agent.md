# Mycroft - SEC Filings Analysis Agent

## Purpose

Mycroft - SEC Filings Analysis Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - sec filings analysis agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Edgar_Fetcher | executeCommand | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Validate Fetcher | code | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| If | if | conductor |
| Set Variables | set | gigo |
| Setup Github Repo | executeCommand | gigo |
| Set Path Variables | code | gigo |
| Setup Python Enviornment and Output Directories | executeCommand | gigo |
| Edgar_Fetcher | executeCommand | ingest |
| Validate Fetcher | code | ingest |
| Financial Analyzer | executeCommand | gigo |
| Narrative Parser | executeCommand | gigo |
| Error Handling | code | gigo |
| Cleanup | executeCommand | gigo |
| Webhook | webhook | conductor |
| Respond to Webhook | respondToWebhook | conductor |
| If1 | if | conductor |
| Respond to Webhook1 | respondToWebhook | conductor |
| Read/Write Files from Disk | readWriteFile | tool |
| Read/Write Files from Disk1 | readWriteFile | tool |
| Parse Results | code | gigo |
| Parse Both Results | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-sec-filings-analysis-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-sec-filings-analysis-agent data/verified/n8n-mycroft-sec-filings-analysis-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-sec-filings-analysis-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Set Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__set-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
3. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
4. Step name: Set Path Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__set-path-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
5. Step name: Setup Python Enviornment and Output Directories. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__setup-python-enviornment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
6. Step name: Edgar_Fetcher. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-agent__edgar-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-sec-filings-analysis-agent/.
7. Step name: Validate Fetcher. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-agent__validate-fetcher.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-sec-filings-analysis-agent/.
8. Step name: Financial Analyzer. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__financial-analyzer.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
9. Step name: Narrative Parser. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__narrative-parser.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
10. Step name: Error Handling. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__error-handling.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
11. Step name: Cleanup. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__cleanup.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
12. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-agent__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
13. Step name: Read/Write Files from Disk1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-agent__read-write-files-from-disk1.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
14. Step name: Parse Results. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__parse-results.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
15. Step name: Parse Both Results. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__parse-both-results.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-sec-filings-analysis-agent/.
16. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroft-sec-filings-analysis-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroft-sec-filings-analysis-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - SEC Filings Analysis Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Set Variables | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step set-variables` |  |
| Setup Github Repo | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step setup-github-repo` |  |
| Set Path Variables | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step set-path-variables` |  |
| Setup Python Enviornment and Output Directories | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step setup-python-enviornment-and-output-directories` |  |
| Edgar_Fetcher | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step edgar-fetcher` | `--sample` |
| Validate Fetcher | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step validate-fetcher` | `--sample` |
| Financial Analyzer | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step financial-analyzer` |  |
| Narrative Parser | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step narrative-parser` |  |
| Error Handling | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step error-handling` |  |
| Cleanup | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step cleanup` |  |
| Read/Write Files from Disk | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step read-write-files-from-disk` | `--no-write` |
| Read/Write Files from Disk1 | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step read-write-files-from-disk1` | `--no-write` |
| Parse Results | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step parse-results` |  |
| Parse Both Results | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step parse-both-results` |  |
| Produce human report | `snickerdoodle run n8n-mycroft-sec-filings-analysis-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroft-sec-filings-analysis-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroft-sec-filings-analysis-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroft-sec-filings-analysis-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Set Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__set-variables.py` | gigo |
| Setup Github Repo | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__setup-github-repo.py` | gigo |
| Set Path Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__set-path-variables.py` | gigo |
| Setup Python Enviornment and Output Directories | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__setup-python-enviornment-and-output-directories.py` | gigo |
| Edgar_Fetcher | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-agent__edgar-fetcher.py` | ingest |
| Validate Fetcher | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-sec-filings-analysis-agent__validate-fetcher.py` | ingest |
| Financial Analyzer | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__financial-analyzer.py` | gigo |
| Narrative Parser | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__narrative-parser.py` | gigo |
| Error Handling | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__error-handling.py` | gigo |
| Cleanup | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__cleanup.py` | gigo |
| Read/Write Files from Disk | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-agent__read-write-files-from-disk.py` | tool |
| Read/Write Files from Disk1 | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-agent__read-write-files-from-disk1.py` | tool |
| Parse Results | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__parse-results.py` | gigo |
| Parse Both Results | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-sec-filings-analysis-agent__parse-both-results.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-sec-filings-analysis-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-sec-filings-analysis-agent/` | JSON |
| Verified data | `data/verified/n8n-mycroft-sec-filings-analysis-agent/` | JSON |
| Agent log | `logs/n8n-mycroft-sec-filings-analysis-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-sec-filings-analysis-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - SEC Filings Analysis Agent.json`

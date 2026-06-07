# Mycroft - Patent Intelligence Agent

## Purpose

Mycroft - Patent Intelligence Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to mycroft - patent intelligence agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Read Processed Data | readBinaryFile | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Read Metrics | readBinaryFile | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Set Variables | set | gigo |
| Setup Github Repo | executeCommand | gigo |
| Set Path Variables | code | gigo |
| Setup Environment and Output Directories | executeCommand | gigo |
| Extract Patents | executeCommand | gigo |
| Check Extraction Success | if | conductor |
| Process Patents | executeCommand | gigo |
| Read Processed Data | readBinaryFile | ingest |
| Read Metrics | readBinaryFile | ingest |
| Send Report Email | emailSend | tool |
| Error Notification | emailSend | conductor |
| Cleanup Repository | executeCommand | gigo |
| Cleanup Repository Error | executeCommand | gigo |
| Webhook | webhook | conductor |
| Respond to Webhook | respondToWebhook | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-patent-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-mycroft-patent-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-mycroft-patent-intelligence-agent data/verified/n8n-mycroft-patent-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-mycroft-patent-intelligence-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Set Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__set-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
3. Step name: Setup Github Repo. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__setup-github-repo.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
4. Step name: Set Path Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__set-path-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
5. Step name: Setup Environment and Output Directories. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__setup-environment-and-output-directories.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
6. Step name: Extract Patents. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__extract-patents.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
7. Step name: Process Patents. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__process-patents.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
8. Step name: Read Processed Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-agent__read-processed-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-patent-intelligence-agent/.
9. Step name: Read Metrics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-agent__read-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-mycroft-patent-intelligence-agent/.
10. Step name: Send Report Email. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-agent__send-report-email.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Cleanup Repository. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__cleanup-repository.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
12. Step name: Cleanup Repository Error. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__cleanup-repository-error.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-mycroft-patent-intelligence-agent/.
13. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-mycroft-patent-intelligence-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-mycroft-patent-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Mycroft - Patent Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-mycroft-patent-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-mycroft-patent-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Set Variables | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step set-variables` |  |
| Setup Github Repo | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step setup-github-repo` |  |
| Set Path Variables | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step set-path-variables` |  |
| Setup Environment and Output Directories | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step setup-environment-and-output-directories` |  |
| Extract Patents | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step extract-patents` |  |
| Process Patents | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step process-patents` |  |
| Read Processed Data | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step read-processed-data` | `--sample` |
| Read Metrics | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step read-metrics` | `--sample` |
| Send Report Email | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step send-report-email` | `--no-write` |
| Cleanup Repository | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step cleanup-repository` |  |
| Cleanup Repository Error | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step cleanup-repository-error` |  |
| Produce human report | `snickerdoodle run n8n-mycroft-patent-intelligence-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-mycroft-patent-intelligence-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-mycroft-patent-intelligence-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-mycroft-patent-intelligence-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Set Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__set-variables.py` | gigo |
| Setup Github Repo | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__setup-github-repo.py` | gigo |
| Set Path Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__set-path-variables.py` | gigo |
| Setup Environment and Output Directories | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__setup-environment-and-output-directories.py` | gigo |
| Extract Patents | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__extract-patents.py` | gigo |
| Process Patents | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__process-patents.py` | gigo |
| Read Processed Data | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-agent__read-processed-data.py` | ingest |
| Read Metrics | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-mycroft-patent-intelligence-agent__read-metrics.py` | ingest |
| Send Report Email | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-agent__send-report-email.py` | tool |
| Cleanup Repository | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__cleanup-repository.py` | gigo |
| Cleanup Repository Error | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-mycroft-patent-intelligence-agent__cleanup-repository-error.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-mycroft-patent-intelligence-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-mycroft-patent-intelligence-agent/` | JSON |
| Verified data | `data/verified/n8n-mycroft-patent-intelligence-agent/` | JSON |
| Agent log | `logs/n8n-mycroft-patent-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-mycroft-patent-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Orchestrator/v1/Mycroft - Patent Intelligence Agent.json`

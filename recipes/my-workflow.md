# My workflow

## Purpose

My workflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to my workflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Set (Targets) | `set` | conductor |
| Code (Split into items) | `code` | gigo |
| Code (Parse owner/repo) | `code` | gigo |
| HTTP Request (Repo Metadata) | `httpRequest` | ingest |
| Code (Build profile JSON) | `code` | conductor |
| Code (JSON → Binary) | `code` | conductor |
| Read/Write Files from Disk | `readWriteFile` | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (2 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (1 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (4 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run my-workflow --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/my-workflow data/verified/my-workflow -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/my-workflow.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Code (Split into items). Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow__code-split-into-items.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow/.
3. Step name: Code (Parse owner/repo). Labor: AI with Human gate.
   Script called: `scripts/gigo/my-workflow__code-parse-owner-repo.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/my-workflow/.
4. Step name: HTTP Request (Repo Metadata). Labor: AI with Human gate.
   Script called: `scripts/ingest/my-workflow__http-request-repo-metadata.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/my-workflow/.
5. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `scripts/tools/my-workflow__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/my-workflow__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/my-workflow-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/my-workflow-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `My workflow` run.
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
`snickerdoodle run my-workflow --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run my-workflow --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Code (Split into items) | `snickerdoodle run my-workflow --step code-split-into-items` |  |
| Code (Parse owner/repo) | `snickerdoodle run my-workflow --step code-parse-owner-repo` |  |
| HTTP Request (Repo Metadata) | `snickerdoodle run my-workflow --step http-request-repo-metadata` | `--sample` |
| Read/Write Files from Disk | `snickerdoodle run my-workflow --step read-write-files-from-disk` | `--no-write` |
| Produce human report | `snickerdoodle run my-workflow --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate my-workflow --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate my-workflow --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate my-workflow --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Code (Split into items) | `scripts/gigo/my-workflow__code-split-into-items.py` | gigo |
| Code (Parse owner/repo) | `scripts/gigo/my-workflow__code-parse-owner-repo.py` | gigo |
| HTTP Request (Repo Metadata) | `scripts/ingest/my-workflow__http-request-repo-metadata.py` | ingest |
| Read/Write Files from Disk | `scripts/tools/my-workflow__read-write-files-from-disk.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/my-workflow__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/my-workflow/` | JSON |
| Verified data | `data/verified/my-workflow/` | JSON |
| Agent log | `logs/my-workflow-[DATE].json` | JSON |
| Human report | `reports/generated/my-workflow-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json`

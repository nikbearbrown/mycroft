# oss signals workflow

## Purpose

oss signals workflow defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to oss signals workflow. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| HTTP Request (Repo Metadata) | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | manualTrigger | conductor |
| Set (Targets) | set | gigo |
| Code (Split into items) | code | conductor |
| Code (Parse owner/repo) | code | gigo |
| HTTP Request (Repo Metadata) | httpRequest | ingest |
| Code (Build profile JSON) | code | gigo |
| Code (JSON → Binary) | code | gigo |
| Read/Write Files from Disk | readWriteFile | tool |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-oss-signals-workflow.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-oss-signals-workflow --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-oss-signals-workflow data/verified/n8n-oss-signals-workflow -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-oss-signals-workflow.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Set (Targets). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__set-targets.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-oss-signals-workflow/.
3. Step name: Code (Parse owner/repo). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__code-parse-owner-repo.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-oss-signals-workflow/.
4. Step name: HTTP Request (Repo Metadata). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-oss-signals-workflow__http-request-repo-metadata.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-oss-signals-workflow/.
5. Step name: Code (Build profile JSON). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__code-build-profile-json.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-oss-signals-workflow/.
6. Step name: Code (JSON → Binary). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__code-json-binary.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-oss-signals-workflow/.
7. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-oss-signals-workflow__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-oss-signals-workflow__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-oss-signals-workflow-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-oss-signals-workflow-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `oss signals workflow` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-oss-signals-workflow --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-oss-signals-workflow --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Set (Targets) | `snickerdoodle run n8n-oss-signals-workflow --step set-targets` |  |
| Code (Parse owner/repo) | `snickerdoodle run n8n-oss-signals-workflow --step code-parse-owner-repo` |  |
| HTTP Request (Repo Metadata) | `snickerdoodle run n8n-oss-signals-workflow --step http-request-repo-metadata` | `--sample` |
| Code (Build profile JSON) | `snickerdoodle run n8n-oss-signals-workflow --step code-build-profile-json` |  |
| Code (JSON → Binary) | `snickerdoodle run n8n-oss-signals-workflow --step code-json-binary` |  |
| Read/Write Files from Disk | `snickerdoodle run n8n-oss-signals-workflow --step read-write-files-from-disk` | `--no-write` |
| Produce human report | `snickerdoodle run n8n-oss-signals-workflow --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-oss-signals-workflow --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-oss-signals-workflow --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-oss-signals-workflow --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Set (Targets) | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__set-targets.py` | gigo |
| Code (Parse owner/repo) | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__code-parse-owner-repo.py` | gigo |
| HTTP Request (Repo Metadata) | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-oss-signals-workflow__http-request-repo-metadata.py` | ingest |
| Code (Build profile JSON) | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__code-build-profile-json.py` | gigo |
| Code (JSON → Binary) | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-oss-signals-workflow__code-json-binary.py` | gigo |
| Read/Write Files from Disk | `[TODO: DEV] Create or map script path: scripts/tools/n8n-oss-signals-workflow__read-write-files-from-disk.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-oss-signals-workflow__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-oss-signals-workflow/` | JSON |
| Verified data | `data/verified/n8n-oss-signals-workflow/` | JSON |
| Agent log | `logs/n8n-oss-signals-workflow-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-oss-signals-workflow-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/OpenSource_Engineering_Health/n8n/oss_signals_workflow.json`

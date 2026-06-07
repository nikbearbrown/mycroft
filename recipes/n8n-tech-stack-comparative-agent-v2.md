# Tech Stack Comparative Agent V2

## Purpose

Tech Stack Comparative Agent V2 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to tech stack comparative agent v2. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| GitHub: Get Repos | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| GitHub: Get Languages | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| arXiv: Search Papers | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Prepare Variables | set | gigo |
| GitHub: Get Repos | httpRequest | ingest |
| Batch Repos | splitInBatches | conductor |
| GitHub: Get Languages | httpRequest | ingest |
| Aggregate Repo Data | set | gigo |
| arXiv: Search Papers | httpRequest | ingest |
| Parse arXiv XML | code | gigo |
| Manual Trigger | manualTrigger | conductor |
| Input: Companies | set | gigo |
| Format Language Data | set | gigo |
| Format Research Data | set | gigo |
| Code | code | gigo |
| Code1 | code | gigo |
| Code2 | code | gigo |
| Code3 | code | gigo |
| Code4 | code | gigo |
| Code5 | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-tech-stack-comparative-agent-v2.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-tech-stack-comparative-agent-v2 data/verified/n8n-tech-stack-comparative-agent-v2 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-tech-stack-comparative-agent-v2.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Prepare Variables. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__prepare-variables.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
3. Step name: GitHub: Get Repos. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-comparative-agent-v2__github-get-repos.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-tech-stack-comparative-agent-v2/.
4. Step name: GitHub: Get Languages. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-comparative-agent-v2__github-get-languages.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-tech-stack-comparative-agent-v2/.
5. Step name: Aggregate Repo Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__aggregate-repo-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
6. Step name: arXiv: Search Papers. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-comparative-agent-v2__arxiv-search-papers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-tech-stack-comparative-agent-v2/.
7. Step name: Parse arXiv XML. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__parse-arxiv-xml.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
8. Step name: Input: Companies. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__input-companies.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
9. Step name: Format Language Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__format-language-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
10. Step name: Format Research Data. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__format-research-data.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
11. Step name: Code. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
12. Step name: Code1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
13. Step name: Code2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
14. Step name: Code3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
15. Step name: Code4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
16. Step name: Code5. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code5.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-comparative-agent-v2/.
17. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-tech-stack-comparative-agent-v2__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-tech-stack-comparative-agent-v2-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-tech-stack-comparative-agent-v2-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Tech Stack Comparative Agent V2` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-tech-stack-comparative-agent-v2 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-tech-stack-comparative-agent-v2 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Prepare Variables | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step prepare-variables` |  |
| GitHub: Get Repos | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step github-get-repos` | `--sample` |
| GitHub: Get Languages | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step github-get-languages` | `--sample` |
| Aggregate Repo Data | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step aggregate-repo-data` |  |
| arXiv: Search Papers | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step arxiv-search-papers` | `--sample` |
| Parse arXiv XML | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step parse-arxiv-xml` |  |
| Input: Companies | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step input-companies` |  |
| Format Language Data | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step format-language-data` |  |
| Format Research Data | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step format-research-data` |  |
| Code | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step code` |  |
| Code1 | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step code1` |  |
| Code2 | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step code2` |  |
| Code3 | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step code3` |  |
| Code4 | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step code4` |  |
| Code5 | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step code5` |  |
| Produce human report | `snickerdoodle run n8n-tech-stack-comparative-agent-v2 --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-tech-stack-comparative-agent-v2 --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-tech-stack-comparative-agent-v2 --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-tech-stack-comparative-agent-v2 --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Prepare Variables | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__prepare-variables.py` | gigo |
| GitHub: Get Repos | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-comparative-agent-v2__github-get-repos.py` | ingest |
| GitHub: Get Languages | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-comparative-agent-v2__github-get-languages.py` | ingest |
| Aggregate Repo Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__aggregate-repo-data.py` | gigo |
| arXiv: Search Papers | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-comparative-agent-v2__arxiv-search-papers.py` | ingest |
| Parse arXiv XML | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__parse-arxiv-xml.py` | gigo |
| Input: Companies | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__input-companies.py` | gigo |
| Format Language Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__format-language-data.py` | gigo |
| Format Research Data | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__format-research-data.py` | gigo |
| Code | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code.py` | gigo |
| Code1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code1.py` | gigo |
| Code2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code2.py` | gigo |
| Code3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code3.py` | gigo |
| Code4 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code4.py` | gigo |
| Code5 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-comparative-agent-v2__code5.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-tech-stack-comparative-agent-v2__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-tech-stack-comparative-agent-v2/` | JSON |
| Verified data | `data/verified/n8n-tech-stack-comparative-agent-v2/` | JSON |
| Agent log | `logs/n8n-tech-stack-comparative-agent-v2-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-tech-stack-comparative-agent-v2-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Comparative_Agent/Tech_Stack_Comparative_Agent_V2.json`

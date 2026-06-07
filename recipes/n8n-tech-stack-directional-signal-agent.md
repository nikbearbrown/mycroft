# Tech_Stack_Directional_Signal_Agent

## Purpose

Tech_Stack_Directional_Signal_Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to tech_stack_directional_signal_agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| GitHub GraphQL | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Fetch Commit Activity | code | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Groq AI Analysis | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Form Trigger | formTrigger | conductor |
| Company Input | code | gigo |
| GitHub GraphQL | httpRequest | ingest |
| Process Repos + Language Analysis | code | gigo |
| Fetch Commit Activity | code | ingest |
| Velocity Analysis | code | gigo |
| Build Groq Prompt | code | gigo |
| Groq AI Analysis | httpRequest | ingest |
| Score + Claims Schema | code | gigo |
| Generate Dashboard | code | gigo |
| Export HTML File | code | gigo |
| Code | code | gigo |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json` | Yes |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-tech-stack-directional-signal-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-tech-stack-directional-signal-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-tech-stack-directional-signal-agent data/verified/n8n-tech-stack-directional-signal-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-tech-stack-directional-signal-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Company Input. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__company-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
3. Step name: GitHub GraphQL. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-directional-signal-agent__github-graphql.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-tech-stack-directional-signal-agent/.
4. Step name: Process Repos + Language Analysis. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__process-repos-language-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
5. Step name: Fetch Commit Activity. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-directional-signal-agent__fetch-commit-activity.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-tech-stack-directional-signal-agent/.
6. Step name: Velocity Analysis. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__velocity-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
7. Step name: Build Groq Prompt. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__build-groq-prompt.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
8. Step name: Groq AI Analysis. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-directional-signal-agent__groq-ai-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-tech-stack-directional-signal-agent/.
9. Step name: Score + Claims Schema. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__score-claims-schema.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
10. Step name: Generate Dashboard. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__generate-dashboard.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
11. Step name: Export HTML File. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__export-html-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
12. Step name: Code. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__code.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-tech-stack-directional-signal-agent/.
13. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-tech-stack-directional-signal-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-tech-stack-directional-signal-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-tech-stack-directional-signal-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Tech_Stack_Directional_Signal_Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-tech-stack-directional-signal-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-tech-stack-directional-signal-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Company Input | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step company-input` |  |
| GitHub GraphQL | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step github-graphql` | `--sample` |
| Process Repos + Language Analysis | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step process-repos-language-analysis` |  |
| Fetch Commit Activity | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step fetch-commit-activity` | `--sample` |
| Velocity Analysis | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step velocity-analysis` |  |
| Build Groq Prompt | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step build-groq-prompt` |  |
| Groq AI Analysis | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step groq-ai-analysis` | `--sample` |
| Score + Claims Schema | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step score-claims-schema` |  |
| Generate Dashboard | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step generate-dashboard` |  |
| Export HTML File | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step export-html-file` |  |
| Code | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step code` |  |
| Produce human report | `snickerdoodle run n8n-tech-stack-directional-signal-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-tech-stack-directional-signal-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-tech-stack-directional-signal-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-tech-stack-directional-signal-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Company Input | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__company-input.py` | gigo |
| GitHub GraphQL | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-directional-signal-agent__github-graphql.py` | ingest |
| Process Repos + Language Analysis | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__process-repos-language-analysis.py` | gigo |
| Fetch Commit Activity | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-directional-signal-agent__fetch-commit-activity.py` | ingest |
| Velocity Analysis | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__velocity-analysis.py` | gigo |
| Build Groq Prompt | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__build-groq-prompt.py` | gigo |
| Groq AI Analysis | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-tech-stack-directional-signal-agent__groq-ai-analysis.py` | ingest |
| Score + Claims Schema | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__score-claims-schema.py` | gigo |
| Generate Dashboard | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__generate-dashboard.py` | gigo |
| Export HTML File | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__export-html-file.py` | gigo |
| Code | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-tech-stack-directional-signal-agent__code.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-tech-stack-directional-signal-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-tech-stack-directional-signal-agent/` | JSON |
| Verified data | `data/verified/n8n-tech-stack-directional-signal-agent/` | JSON |
| Agent log | `logs/n8n-tech-stack-directional-signal-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-tech-stack-directional-signal-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json`

# Tech_Stack_Directional_Signal_Agent

## Purpose

Tech_Stack_Directional_Signal_Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to tech_stack_directional_signal_agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

## Node Classification

| Node Name | Node Type | Classification |
|---|---|---|
| Form Trigger | `formTrigger` | conductor |
| Company Input | `code` | conductor |
| GitHub GraphQL | `httpRequest` | ingest |
| Process Repos + Language Analysis | `code` | tool |
| Fetch Commit Activity | `code` | conductor |
| Velocity Analysis | `code` | tool |
| Build Groq Prompt | `code` | tool |
| Groq AI Analysis | `httpRequest` | tool |
| Score + Claims Schema | `code` | tool |
| Generate Dashboard | `code` | conductor |
| Export HTML File | `code` | conductor |
| Code | `code` | conductor |

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (5 nodes) | Yes |
| Conductor node outputs | JSON | Converted conductor steps (6 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/tech-stack-directional-signal-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run tech-stack-directional-signal-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/tech-stack-directional-signal-agent data/verified/tech-stack-directional-signal-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/tech-stack-directional-signal-agent.md`.
   Human capacity: [EI].

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: GitHub GraphQL. Labor: AI with Human gate.
   Script called: `scripts/ingest/tech-stack-directional-signal-agent__github-graphql.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/tech-stack-directional-signal-agent/.
3. Step name: Process Repos + Language Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/tech-stack-directional-signal-agent__process-repos-language-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
4. Step name: Velocity Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/tech-stack-directional-signal-agent__velocity-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Build Groq Prompt. Labor: AI with Human gate.
   Script called: `scripts/tools/tech-stack-directional-signal-agent__build-groq-prompt.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Groq AI Analysis. Labor: AI with Human gate.
   Script called: `scripts/tools/tech-stack-directional-signal-agent__groq-ai-analysis.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Score + Claims Schema. Labor: AI with Human gate.
   Script called: `scripts/tools/tech-stack-directional-signal-agent__score-claims-schema.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/tech-stack-directional-signal-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/tech-stack-directional-signal-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/tech-stack-directional-signal-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Tech_Stack_Directional_Signal_Agent` run.
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
`snickerdoodle run tech-stack-directional-signal-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run tech-stack-directional-signal-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| GitHub GraphQL | `snickerdoodle run tech-stack-directional-signal-agent --step github-graphql` | `--sample` |
| Process Repos + Language Analysis | `snickerdoodle run tech-stack-directional-signal-agent --step process-repos-language-analysis` | `--no-write` |
| Velocity Analysis | `snickerdoodle run tech-stack-directional-signal-agent --step velocity-analysis` | `--no-write` |
| Build Groq Prompt | `snickerdoodle run tech-stack-directional-signal-agent --step build-groq-prompt` | `--no-write` |
| Groq AI Analysis | `snickerdoodle run tech-stack-directional-signal-agent --step groq-ai-analysis` | `--no-write` |
| Score + Claims Schema | `snickerdoodle run tech-stack-directional-signal-agent --step score-claims-schema` | `--no-write` |
| Produce human report | `snickerdoodle run tech-stack-directional-signal-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate tech-stack-directional-signal-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate tech-stack-directional-signal-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate tech-stack-directional-signal-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| GitHub GraphQL | `scripts/ingest/tech-stack-directional-signal-agent__github-graphql.py` | ingest |
| Process Repos + Language Analysis | `scripts/tools/tech-stack-directional-signal-agent__process-repos-language-analysis.py` | tool |
| Velocity Analysis | `scripts/tools/tech-stack-directional-signal-agent__velocity-analysis.py` | tool |
| Build Groq Prompt | `scripts/tools/tech-stack-directional-signal-agent__build-groq-prompt.py` | tool |
| Groq AI Analysis | `scripts/tools/tech-stack-directional-signal-agent__groq-ai-analysis.py` | tool |
| Score + Claims Schema | `scripts/tools/tech-stack-directional-signal-agent__score-claims-schema.py` | tool |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/tech-stack-directional-signal-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/tech-stack-directional-signal-agent/` | JSON |
| Verified data | `data/verified/tech-stack-directional-signal-agent/` | JSON |
| Agent log | `logs/tech-stack-directional-signal-agent-[DATE].json` | JSON |
| Human report | `reports/generated/tech-stack-directional-signal-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Tech_Stack_Directional_Signal_Agent/Tech_Stack_Directional_Signal_Agent .json`

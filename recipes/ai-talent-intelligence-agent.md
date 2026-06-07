# AI Talent Intelligence Agent

## Purpose

The AI Talent Intelligence Agent tracks research papers, hiring or appointment news, and known researcher records to surface AI talent movement signals that may matter for competitive intelligence, while clearly separating real source data from prototype/mock records.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| ArXiv AI/ML/NLP papers | XML/API response | ArXiv API or `data/raw/ai-talent-intelligence-agent/` | Confirm source is allowed, current, and rate-safe before live fetch. |
| AI researcher news | JSON | Serper News API or local export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Researcher database rows | JSON/table | Local mock rows or approved database export | Confirm source is allowed, current, and rate-safe before live fetch. |
| Significance threshold | Integer | Recipe default, `5` | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json` | Yes |
| ArXiv AI/ML/NLP papers | XML/API response | ArXiv API or `data/raw/ai-talent-intelligence-agent/` | Yes |
| AI researcher news | JSON | Serper News API or local export | Yes |
| Researcher database rows | JSON/table | Local mock rows or approved database export | No |
| Significance threshold | Integer | Recipe default, `5` | Yes |
| Groq credential | Environment variable | `GROQ_API_KEY` for future live LLM adapter | No |
| Serper credential | Environment variable | `SERPER_API_KEY` for live news search | No |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/ai-talent-intelligence-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/ai-talent-intelligence-agent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/ai-talent-intelligence-agent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/ai-talent-intelligence-agent data/verified/ai-talent-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/ai-talent-intelligence-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/ai-talent-intelligence-agent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/ai-talent-intelligence-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/ai-talent-intelligence-agent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/ai-talent-intelligence-agent-[DATE].json && test -f reports/generated/ai-talent-intelligence-agent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/ai-talent-intelligence-agent-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-talent-intelligence-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/ai-talent-intelligence-agent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-talent-intelligence-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/ai-talent-intelligence-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/ai-talent-intelligence-agent-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-talent-intelligence-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/ai-talent-intelligence-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/ai-talent-intelligence-agent-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-talent-intelligence-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/ai-talent-intelligence-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/ai-talent-intelligence-agent-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-talent-intelligence-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/ai-talent-intelligence-agent-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `ai-talent-intelligence-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/ai-talent-intelligence-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/ai-talent-intelligence-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `AI Talent Intelligence Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if both ArXiv and news inputs are missing.
- Stop if live Serper, Groq, database, or SMTP access is needed but credentials and human approval are absent.
- Stop if mock researcher records are mixed with real signals without an explicit caveat.
- Stop if no records pass the high-significance gate.
- Stop before saving to a live database or sending email.
- Stop if the report implies investment advice without human interpretation and source review.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run ai-talent-intelligence-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run ai-talent-intelligence-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run ai-talent-intelligence-agent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run ai-talent-intelligence-agent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run ai-talent-intelligence-agent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run ai-talent-intelligence-agent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run ai-talent-intelligence-agent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run ai-talent-intelligence-agent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate ai-talent-intelligence-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate ai-talent-intelligence-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate ai-talent-intelligence-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate ai-talent-intelligence-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate ai-talent-intelligence-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate ai-talent-intelligence-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/ai-talent-intelligence-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/ai-talent-intelligence-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/ai-talent-intelligence-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/ai-talent-intelligence-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/ai-talent-intelligence-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/ai-talent-intelligence-agent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/ai-talent-intelligence-agent/` | JSON |
| Verified data | `data/verified/ai-talent-intelligence-agent/` | JSON |
| Agent log | `logs/ai-talent-intelligence-agent-[DATE].json` | JSON |
| Human report | `reports/generated/ai-talent-intelligence-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

The AI Talent Intelligence Agent tracks research papers, hiring or appointment news, and known researcher records to surface AI talent movement signals that may matter for competitive intelligence, while clearly separating real source data from prototype/mock records.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/ai-talent-intelligence-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run ai-talent-intelligence-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/ai-talent-intelligence-agent data/verified/ai-talent-intelligence-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/ai-talent-intelligence-agent.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: fetch_ai_talent_arxiv. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-ai-talent-arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-talent-intelligence-agent/.
3. Step name: fetch_ai_talent_news. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-ai-talent-news.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-talent-intelligence-agent/.
4. Step name: load_mock_researchers. Labor: AI with Human gate.
   Script called: `scripts/ingest/load-mock-researchers.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/ai-talent-intelligence-agent/.
5. Step name: parse_ai_talent_arxiv. Labor: AI with Human gate.
   Script called: `scripts/gigo/parse-ai-talent-arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-talent-intelligence-agent/.
6. Step name: analyze_ai_talent_signal. Labor: AI with Human gate.
   Script called: `scripts/tools/analyze-ai-talent-signal.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: filter_high_significance. Labor: AI with Human gate.
   Script called: `scripts/gigo/filter-high-significance.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-talent-intelligence-agent/.
8. Step name: aggregate_ai_talent_statistics. Labor: AI with Human gate.
   Script called: `scripts/tools/aggregate-ai-talent-statistics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: generate_ai_talent_report. Labor: AI with Human gate.
   Script called: `scripts/tools/generate-ai-talent-report.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: prepare_ai_talent_database_payload. Labor: AI with Human gate.
   Script called: `scripts/gigo/prepare-ai-talent-database-payload.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/ai-talent-intelligence-agent/.
11. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/ai-talent-intelligence-agent-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

# Workflow A — Extract & Store Raw Data

## Purpose

Workflow A collects raw AI-market intelligence from news, research, and community sources so later AEO FAQ workflows can synthesize emerging topics from traceable source records rather than from unsourced impressions.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| TechCrunch AI feed | RSS text | `https://techcrunch.com/category/artificial-intelligence/feed/` | Confirm source is allowed, current, and rate-safe before live fetch. |
| VentureBeat feed | RSS text | `https://venturebeat.com/feed/` | Confirm source is allowed, current, and rate-safe before live fetch. |
| Hacker News AI query | RSS text | `https://hnrss.org/frontpage?q=AI+LLM+machine+learning&count=20` | Confirm source is allowed, current, and rate-safe before live fetch. |
| ArXiv cs.AI feed | RSS/Atom text | `https://export.arxiv.org/rss/cs.AI` | Confirm source is allowed, current, and rate-safe before live fetch. |
| Reddit AI listing | JSON | `https://www.reddit.com/r/artificial+MachineLearning+OpenAI.json?limit=25&sort=hot` | Confirm source is allowed, current, and rate-safe before live fetch. |
| Existing raw_intelligence rows | Table/JSON | `data/verified/aeo-workflow-a/` or approved database export | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Original workflow node map | [TODO: DEV] Parse original workflow JSON. | [TODO: DEFINE] Classify parsed nodes as ingest, gigo, tool, conductor, or report. |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json` | Yes |
| TechCrunch AI feed | RSS text | `https://techcrunch.com/category/artificial-intelligence/feed/` | Yes |
| VentureBeat feed | RSS text | `https://venturebeat.com/feed/` | Yes |
| Hacker News AI query | RSS text | `https://hnrss.org/frontpage?q=AI+LLM+machine+learning&count=20` | Yes |
| ArXiv cs.AI feed | RSS/Atom text | `https://export.arxiv.org/rss/cs.AI` | Yes |
| Reddit AI listing | JSON | `https://www.reddit.com/r/artificial+MachineLearning+OpenAI.json?limit=25&sort=hot` | Yes |
| Existing raw_intelligence rows | Table/JSON | `data/verified/aeo-workflow-a/` or approved database export | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/workflow-a-extract-store-raw-data.md" && rg -n "\[TODO: DEFINE]" "recipes/workflow-a-extract-store-raw-data.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/workflow-a-extract-store-raw-data/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/workflow-a-extract-store-raw-data data/verified/workflow-a-extract-store-raw-data -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/workflow-a-extract-store-raw-data-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/workflow-a-extract-store-raw-data.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/workflow-a-extract-store-raw-data-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/workflow-a-extract-store-raw-data.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/workflow-a-extract-store-raw-data-[DATE].json && test -f reports/generated/workflow-a-extract-store-raw-data-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/workflow-a-extract-store-raw-data-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `workflow-a-extract-store-raw-data`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/workflow-a-extract-store-raw-data-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `workflow-a-extract-store-raw-data`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/workflow-a-extract-store-raw-data/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/workflow-a-extract-store-raw-data-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `workflow-a-extract-store-raw-data`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/workflow-a-extract-store-raw-data/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/workflow-a-extract-store-raw-data-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `workflow-a-extract-store-raw-data`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/workflow-a-extract-store-raw-data/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/workflow-a-extract-store-raw-data-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `workflow-a-extract-store-raw-data`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/workflow-a-extract-store-raw-data-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `workflow-a-extract-store-raw-data`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/workflow-a-extract-store-raw-data-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/workflow-a-extract-store-raw-data-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Workflow A — Extract & Store Raw Data` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if all five source fetches fail.
- Stop if a parser returns zero records for a source that previously produced records and no source outage is logged.
- Stop if any prepared row is missing `title`, `url`, `source_name`, or `raw_content`.
- Stop if duplicate URLs dominate the run and the source freshness question is unresolved.
- Stop before writing to a live database without explicit human approval and a verified database destination.
- Stop before triggering Workflow B if `new_items` is zero.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run workflow-a-extract-store-raw-data --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run workflow-a-extract-store-raw-data --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run workflow-a-extract-store-raw-data --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run workflow-a-extract-store-raw-data --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run workflow-a-extract-store-raw-data --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run workflow-a-extract-store-raw-data --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run workflow-a-extract-store-raw-data --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run workflow-a-extract-store-raw-data --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/workflow-a-extract-store-raw-data-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/workflow-a-extract-store-raw-data-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/workflow-a-extract-store-raw-data-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/workflow-a-extract-store-raw-data-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/workflow-a-extract-store-raw-data-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/workflow-a-extract-store-raw-data-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/workflow-a-extract-store-raw-data/` | JSON |
| Verified data | `data/verified/workflow-a-extract-store-raw-data/` | JSON |
| Agent log | `logs/workflow-a-extract-store-raw-data-[DATE].json` | JSON |
| Human report | `reports/generated/workflow-a-extract-store-raw-data-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

Workflow A collects raw AI-market intelligence from news, research, and community sources so later AEO FAQ workflows can synthesize emerging topics from traceable source records rather than from unsourced impressions.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/workflow-a-extract-store-raw-data.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run workflow-a-extract-store-raw-data --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/workflow-a-extract-store-raw-data data/verified/workflow-a-extract-store-raw-data -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/workflow-a-extract-store-raw-data.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: fetch_techcrunch. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
3. Step name: fetch_venturebeat. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-venturebeat.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
4. Step name: fetch_hackernews. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-hackernews.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
5. Step name: fetch_arxiv. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
6. Step name: fetch_reddit. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch-reddit.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
7. Step name: parse_techcrunch. Labor: AI with Human gate.
   Script called: `scripts/gigo/parse-techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-a-extract-store-raw-data/.
8. Step name: store_techcrunch. Labor: AI with Human gate.
   Script called: `scripts/gigo/store-techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-a-extract-store-raw-data/.
9. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/workflow-a-extract-store-raw-data-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

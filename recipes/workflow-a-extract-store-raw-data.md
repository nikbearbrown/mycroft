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

## Node Classification

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: fetch_techcrunch. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
3. Step name: fetch_venturebeat. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_venturebeat.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
4. Step name: fetch_hackernews. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_hackernews.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
5. Step name: fetch_arxiv. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_arxiv.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
6. Step name: fetch_reddit. Labor: AI with Human gate.
   Script called: `scripts/ingest/fetch_reddit.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/workflow-a-extract-store-raw-data/.
7. Step name: parse_techcrunch. Labor: AI with Human gate.
   Script called: `scripts/gigo/parse_techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-a-extract-store-raw-data/.
8. Step name: store_techcrunch. Labor: AI with Human gate.
   Script called: `scripts/gigo/store_techcrunch.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/workflow-a-extract-store-raw-data/.
9. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/workflow-a-extract-store-raw-data__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/workflow-a-extract-store-raw-data-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/workflow-a-extract-store-raw-data-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Workflow A — Extract & Store Raw Data` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| fetch_techcrunch | `snickerdoodle run workflow-a-extract-store-raw-data --step fetch-techcrunch` | `--sample` |
| fetch_venturebeat | `snickerdoodle run workflow-a-extract-store-raw-data --step fetch-venturebeat` | `--sample` |
| fetch_hackernews | `snickerdoodle run workflow-a-extract-store-raw-data --step fetch-hackernews` | `--sample` |
| fetch_arxiv | `snickerdoodle run workflow-a-extract-store-raw-data --step fetch-arxiv` | `--sample` |
| fetch_reddit | `snickerdoodle run workflow-a-extract-store-raw-data --step fetch-reddit` | `--sample` |
| parse_techcrunch | `snickerdoodle run workflow-a-extract-store-raw-data --step parse-techcrunch` |  |
| store_techcrunch | `snickerdoodle run workflow-a-extract-store-raw-data --step store-techcrunch` |  |
| Produce human report | `snickerdoodle run workflow-a-extract-store-raw-data --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate workflow-a-extract-store-raw-data --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| fetch_techcrunch | `scripts/ingest/fetch_techcrunch.py` | ingest |
| fetch_venturebeat | `scripts/ingest/fetch_venturebeat.py` | ingest |
| fetch_hackernews | `scripts/ingest/fetch_hackernews.py` | ingest |
| fetch_arxiv | `scripts/ingest/fetch_arxiv.py` | ingest |
| fetch_reddit | `scripts/ingest/fetch_reddit.py` | ingest |
| parse_techcrunch | `scripts/gigo/parse_techcrunch.py` | gigo |
| store_techcrunch | `scripts/gigo/store_techcrunch.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/workflow-a-extract-store-raw-data__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/workflow-a-extract-store-raw-data/` | JSON |
| Verified data | `data/verified/workflow-a-extract-store-raw-data/` | JSON |
| Agent log | `logs/workflow-a-extract-store-raw-data-[DATE].json` | JSON |
| Human report | `reports/generated/workflow-a-extract-store-raw-data-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json`

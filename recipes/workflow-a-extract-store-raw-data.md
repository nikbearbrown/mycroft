# Workflow A — Extract & Store Raw Data

## Purpose

Workflow A collects raw AI-market intelligence from news, research, and community sources so later AEO FAQ workflows can synthesize emerging topics from traceable source records rather than from unsourced impressions.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| TechCrunch AI feed | RSS text | `https://techcrunch.com/category/artificial-intelligence/feed/` | Yes |
| VentureBeat feed | RSS text | `https://venturebeat.com/feed/` | Yes |
| Hacker News AI query | RSS text | `https://hnrss.org/frontpage?q=AI+LLM+machine+learning&count=20` | Yes |
| ArXiv cs.AI feed | RSS/Atom text | `https://export.arxiv.org/rss/cs.AI` | Yes |
| Reddit AI listing | JSON | `https://www.reddit.com/r/artificial+MachineLearning+OpenAI.json?limit=25&sort=hot` | Yes |
| Existing raw_intelligence rows | Table/JSON | `data/verified/aeo-workflow-a/` or approved database export | No |

## Phase Gates

1. Source gate: each configured source must be public, URL-shaped, and appropriate for AI-market monitoring. Verification: inspect the five feed URLs in the recipe and run one ingest script in sample/error-safe mode, for example `python3 scripts/ingest/fetch_hackernews.py`. Human capacity: [PF], [PA].
2. Ingest gate: raw payloads must be saved or fetch failures logged per source. Verification: each fetch output must contain `source_name` plus either `raw` or `error`. Human capacity: [TO], [PA].
3. Parse gate: each parser must produce records with `title`, `source_name`, `source_type`, `url`, `raw_content`, `published_date`, `pulled_date`, `topic_tag`, and `processed`. Verification: run `python3 scripts/gigo/parse_techcrunch.py`, `python3 scripts/gigo/parse_arxiv.py`, and `python3 scripts/gigo/parse_reddit.py` on sample inputs. Human capacity: [PA].
4. Storage gate: rows must be deduplicated by URL and truncated to the raw_intelligence contract before any database write. Verification: run one `scripts/gigo/store_*.py` script and confirm `conflict_key` is `url`. Human capacity: [PA], [TO].
5. Continuation gate: Workflow B may start only if `new_items` is greater than zero. Verification: count prepared storage rows and log `new_items` and `this_cycle`. Human capacity: [EI].

## Steps

1. Trigger scheduled collection. Labor: AI. Script called: none; conductor schedule. Input: four-hour interval. Output: run ID. Where output goes: `logs/`.
2. Fetch TechCrunch. Labor: AI. Script called: `scripts/ingest/fetch_techcrunch.py`. Input: TechCrunch feed URL. Output: raw feed payload. Where output goes: `data/raw/`.
3. Fetch VentureBeat. Labor: AI. Script called: `scripts/ingest/fetch_venturebeat.py`. Input: VentureBeat feed URL. Output: raw feed payload. Where output goes: `data/raw/`.
4. Fetch Hacker News. Labor: AI. Script called: `scripts/ingest/fetch_hackernews.py`. Input: HNRSS query URL. Output: raw feed payload. Where output goes: `data/raw/`.
5. Fetch ArXiv. Labor: AI. Script called: `scripts/ingest/fetch_arxiv.py`. Input: ArXiv feed URL. Output: raw feed payload. Where output goes: `data/raw/`.
6. Fetch Reddit. Labor: AI. Script called: `scripts/ingest/fetch_reddit.py`. Input: Reddit listing URL. Output: raw JSON payload. Where output goes: `data/raw/`.
7. Parse source payloads. Labor: AI. Script called: `scripts/gigo/parse_techcrunch.py`, `scripts/gigo/parse_venturebeat.py`, `scripts/gigo/parse_hackernews.py`, `scripts/gigo/parse_arxiv.py`, and `scripts/gigo/parse_reddit.py`. Input: raw source payloads. Output: normalized raw_intelligence records. Where output goes: `data/verified/`.
8. Prepare storage rows. Labor: AI. Script called: `scripts/gigo/store_techcrunch.py`, `scripts/gigo/store_venturebeat.py`, `scripts/gigo/store_hackernews.py`, `scripts/gigo/store_arxiv.py`, and `scripts/gigo/store_reddit.py`. Input: parsed records. Output: idempotent row payloads keyed by URL. Where output goes: `data/verified/`.
9. Verify item counts. Labor: AI. Script called: shared count helper in `scripts/gigo/aeo_raw_intelligence_shared.py` or conductor count. Input: prepared rows. Output: `new_items` and `this_cycle` metrics. Where output goes: `logs/`.
10. Decide whether to trigger Workflow B. Labor: Human and AI. Human action required: approve continuation when new items exist and the parse/storage gates pass. Input: count metrics and anomaly log. Output: continue or skip decision. Where output goes: `logs/` and `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/aeo-workflow-a/<run-id>.json`. It must include source URLs, fetch status by source, raw payload locations, parsed counts by source, prepared row counts by source, deduplication counts, `new_items`, `this_cycle`, scripts used, and whether Workflow B was triggered or skipped.

### Human report

The human report goes to `reports/generated/workflow-a-extract-store-raw-data-<date>.md`. It surfaces source coverage, which feeds failed or changed structure, whether enough new source material exists for synthesis, and whether Workflow B should run.

## Stop Conditions

- Stop if all five source fetches fail.
- Stop if a parser returns zero records for a source that previously produced records and no source outage is logged.
- Stop if any prepared row is missing `title`, `url`, `source_name`, or `raw_content`.
- Stop if duplicate URLs dominate the run and the source freshness question is unresolved.
- Stop before writing to a live database without explicit human approval and a verified database destination.
- Stop before triggering Workflow B if `new_items` is zero.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AEO_FAQ_Pipeline_Phase2/data_extraction.json`

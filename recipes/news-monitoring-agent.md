# News Monitoring Agent

## Purpose

The News Monitoring Agent answers whether recent AI and technology news contains decision-relevant signals for financial research by collecting feed articles, cleaning and deduplicating them, attaching sentiment and retrieval metadata, indexing them into auditable local stores, and answering analyst questions only from the resulting source-grounded corpus.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Feed source list | Table/JSON | n8n sources data table or `data/verified/news-monitoring-agent/sources.json` | Yes |
| Feed URL | URL string | Each source row | Yes |
| Previous feed timestamp | ISO datetime/string | Source-state table or verified source metadata | No |
| Article payload | JSON | `data/raw/news-monitoring-agent/` | Yes after ingest |
| Analyst question | String | Chat/manual trigger | Yes for RAG answering |
| RAG evaluation questions | CSV | `data/verified/news-monitoring-agent/questions.csv` | No |
| Model credentials | Environment variables | `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `HUGGINGFACE_API_KEY`, `QDRANT_API_KEY` for future live adapters | No for local dialogic mode |

## Phase Gates

1. Source gate: the source list must contain URL-like feed entries and no secrets. Verification: run `python3 scripts/gigo/upsert_source_state.py --input '{"feed_url":"https://example.com/feed.xml","last_updated":"2026-06-06T00:00:00Z"}'` and confirm the URL and freshness fields are preserved. Human capacity: [PF], [PA].
2. Ingest gate: at least one feed fetch must produce raw JSON or explicitly report a fetch error. Verification: run `python3 scripts/ingest/feedparser_fetch.py --input '{"feed_url":"https://example.com/feed.xml"}'` as a dry-run pattern; for real feeds save to `data/raw/news-monitoring-agent/<run-id>.json`. Human capacity: [TO], [PA].
3. GIGO gate: parsed records must have stable IDs, URL/title/content fields, and empty-content records removed. Verification: run `python3 scripts/gigo/parse_article.py`, `python3 scripts/gigo/filter_not_null.py`, and `python3 scripts/gigo/remove_duplicates.py` on a small sample and inspect counts. Human capacity: [PA].
4. Sentiment gate: sentiment labels must be present and identified as local or model-derived. Verification: run `python3 scripts/tools/finbert_sentiment.py` and confirm `sentiment.method` is present before interpretation. Human capacity: [PA], [IJ].
5. Retrieval gate: document chunks and retrieval matches must reference source URLs and dates. Verification: run `python3 scripts/gigo/load_documents_a.py` followed by `python3 scripts/tools/rag_answer_agent.py` on a sample question and confirm sources are included. Human capacity: [PA], [IJ].
6. Report gate: the generated human report must separate findings from pipeline details and list anomalies. Verification: create a report from `reports/templates/news-monitoring-agent.md` and link the corresponding log entry. Human capacity: [EI], [IJ].

## Steps

1. Trigger workflow. Labor: AI. Script called: none; conductor action. Input: schedule, chat trigger, or manual trigger. Output: run ID and mode. Where output goes: `logs/`.
2. Load source rows. Labor: AI. Script called: existing local source table or `scripts/gigo/upsert_source_state.py` for state records. Input: source list. Output: verified source records. Where output goes: `data/verified/`.
3. Fetch feed articles. Labor: AI. Script called: `scripts/ingest/feedparser_fetch.py`. Input: source records. Output: raw feed payloads. Where output goes: `data/raw/`.
4. Split and parse articles. Labor: AI. Script called: `scripts/gigo/split_articles.py` and `scripts/gigo/parse_article.py`. Input: raw feed payloads. Output: normalized article records. Where output goes: `data/verified/`.
5. Filter and deduplicate. Labor: AI. Script called: `scripts/gigo/filter_not_null.py` and `scripts/gigo/remove_duplicates.py`. Input: normalized article records. Output: complete unique records. Where output goes: `data/verified/`.
6. Update source freshness. Labor: AI. Script called: `scripts/gigo/upsert_source_state.py`. Input: feed metadata. Output: source-state upsert records. Where output goes: `data/verified/`.
7. Score financial sentiment. Labor: AI. Script called: `scripts/tools/finbert_sentiment.py`. Input: verified unique articles. Output: sentiment-labeled articles. Where output goes: `data/verified/`.
8. Build retrieval documents. Labor: AI. Script called: `scripts/gigo/load_documents_a.py`, `scripts/gigo/load_documents_b.py`, `scripts/gigo/split_documents_a.py`, and `scripts/gigo/split_documents_b.py`. Input: sentiment-labeled articles. Output: chunked document records. Where output goes: `data/verified/`.
9. Prepare vector-store upserts. Labor: AI. Script called: `scripts/tools/qdrant_insert_collection.py`, `scripts/tools/embedding_finance.py`, and `scripts/tools/embedding_gemini.py`. Input: chunked document records. Output: local point payloads or live-run invocation specs. Where output goes: `data/verified/` and `logs/`.
10. Refine analyst question. Labor: AI. Script called: `scripts/tools/query_refinement_agent.py`, `scripts/tools/metadata_filter_agent.py`, `scripts/gigo/parse_refined_queries.py`, and `scripts/gigo/parse_metadata_filter.py`. Input: analyst question. Output: refined queries and filter JSON. Where output goes: `logs/`.
11. Retrieve and answer. Labor: AI. Script called: `scripts/tools/qdrant_retrieve.py` and `scripts/tools/rag_answer_agent.py`. Input: refined question and local documents. Output: source-grounded answer with matched documents. Where output goes: `logs/`.
12. Evaluate RAG variants. Labor: AI and Human. Script called: `scripts/gigo/extract_questions_from_file.py`, `scripts/tools/rag_grader_call.py`, and `scripts/tools/qdrant_scroll.py`. Input: evaluation questions and answer records. Output: handoff records for the dependent rag grader. Where output goes: `logs/`.
13. Review metrics and report. Labor: Human. Human action required: inspect counts, source coverage, lost-record percentage, sentiment caveats, and sourced answer quality. Output: approved findings and decisions. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent logs go to `logs/news-monitoring-agent/<run-id>.json` or an equivalent run log entry. Each log must include `run_id`, `mode`, `source_count`, `raw_article_count`, `unique_article_count`, `processed_article_count`, `scripts_used`, `validation_results`, `answer_records`, `source_urls`, `external_services_requested`, `external_services_called`, and `stop_conditions`.

### Human report

The human report goes to `reports/generated/news-monitoring-agent-<date>.md`. It surfaces the most important source-grounded news findings, anomalies that require review, source coverage, and decisions the analyst or instructor must make before using the output in a financial argument.

## Stop Conditions

- Stop if source rows are missing feed URLs or contain credentials.
- Stop if a feed fetch fails for all sources.
- Stop if parsed article count is zero after the GIGO gate.
- Stop if deduplication removes more records than expected and no explanation is logged.
- Stop if sentiment labels are treated as investment advice rather than weak evidence tags.
- Stop if retrieval answers omit source URLs or publication dates.
- Stop if live Gemini, OpenRouter, Hugging Face, Postgres, or Qdrant calls are required but credentials and human approval are absent.
- Stop before publishing, emailing, trading, or alerting based on the output.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json`

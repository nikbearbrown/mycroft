# News Monitoring Agent — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is moved to `conductor/verified/`.

## Entry Point

The flow is triggered by a scheduled news-monitoring run, a manual workflow execution, a chat question from an analyst, or a RAG evaluation request.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- Depends on: none
- AI task: Create a run ID, identify whether the run is ingest, chat, evaluation, or full dialogic mode, and record the source workflow path.
- Handoff condition: A run ID and mode are present in the log draft.
- On failure: Stop and ask the human to choose a run mode.

### Step 2 — Verify Sources

- Labor: AI
- Depends on: Step 1
- AI task: Read local source records and verify feed URLs and freshness fields without external lookup.
- Handoff condition: Every active source has a URL and no credential-like values.
- On failure: Stop and report invalid source rows.

### Step 3 — Fetch Raw Articles

- Labor: AI
- Depends on: Step 2
- AI task: Run `scripts/ingest/feedparser_fetch.py` on the approved source sample and save raw payloads under `data/raw/news-monitoring-agent/`.
- Handoff condition: At least one raw payload exists or every fetch error is logged with source URL.
- On failure: Stop at ingest gate and request human review.

### Step 4 — Normalize, Filter, and Deduplicate

- Labor: AI
- Depends on: Step 3
- AI task: Run `scripts/gigo/split_articles.py`, `scripts/gigo/parse_article.py`, `scripts/gigo/filter_not_null.py`, and `scripts/gigo/remove_duplicates.py`.
- Handoff condition: Verified output contains stable IDs, source URLs, titles, and non-empty content.
- On failure: Stop and report schema or count failures.

### Step 5 — Add Sentiment and Retrieval Documents

- Labor: AI
- Depends on: Step 4
- AI task: Run `scripts/tools/finbert_sentiment.py`, then build collection A and B documents with `scripts/gigo/load_documents_a.py` and `scripts/gigo/load_documents_b.py`.
- Handoff condition: Each processed article has sentiment metadata and at least one document chunk.
- On failure: Stop and preserve the verified pre-sentiment article file.

### Step 6 — Prepare Retrieval Store

- Labor: AI
- Depends on: Step 5
- AI task: Run `scripts/tools/qdrant_insert_collection.py` in local-spec mode for both collections.
- Handoff condition: Point records include deterministic IDs, vectors, and payload metadata.
- On failure: Stop and report the first invalid point record.

### Step 7 — Answer Analyst Question

- Labor: AI
- Depends on: Step 6
- AI task: Run `scripts/tools/query_refinement_agent.py`, `scripts/tools/metadata_filter_agent.py`, `scripts/tools/qdrant_retrieve.py`, and `scripts/tools/rag_answer_agent.py` on the analyst question.
- Handoff condition: The answer includes matched source metadata or explicitly says no local articles matched.
- On failure: Stop and ask the human whether to broaden the question or inspect source coverage.

### Step 8 — Optional RAG Evaluation

- Labor: AI
- Depends on: Step 7
- AI task: If evaluation questions are present, run `scripts/gigo/extract_questions_from_file.py` and create grader handoffs with `scripts/tools/rag_grader_call.py`.
- Handoff condition: Each evaluation row has a question, answer record, and grader handoff status.
- On failure: Continue the main run but mark RAG evaluation incomplete.

### Step 9 — Human Review

- Labor: Human
- Depends on: Step 7
- Human task: Use [PA], [IJ], and [EI] to inspect source coverage, answer grounding, sentiment caveats, and anomalies.
- Handoff condition: Human explicitly approves, rejects, or requests rerun with revised sources/question.
- On failure: Keep the run in dialogic mode and do not generate a final report.

### Step 10 — Generate Report

- Labor: AI
- Depends on: Step 9
- AI task: Fill `reports/templates/news-monitoring-agent.md` and save a dated report under `reports/generated/`.
- Handoff condition: Report links to the run log and lists decisions required.
- On failure: Stop and report missing report fields.

## Phase Gates

Hard gates: Step 2 source gate, Step 4 GIGO gate, Step 7 retrieval answer gate, and Step 9 human review gate.

## Silent Mode Requirements

- Minimum three successful dialogic runs with different feed sources or analyst questions.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for source coverage, answer grounding, and report usefulness.
- No live external services enabled without documented credential handling and retry behavior.

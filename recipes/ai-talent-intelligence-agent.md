# AI Talent Intelligence Agent

## Purpose

The AI Talent Intelligence Agent tracks research papers, hiring or appointment news, and known researcher records to surface AI talent movement signals that may matter for competitive intelligence, while clearly separating real source data from prototype/mock records.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| ArXiv AI/ML/NLP papers | XML/API response | ArXiv API or `data/raw/ai-talent-intelligence-agent/` | Yes |
| AI researcher news | JSON | Serper News API or local export | Yes |
| Researcher database rows | JSON/table | Local mock rows or approved database export | No |
| Significance threshold | Integer | Recipe default, `5` | Yes |
| Groq credential | Environment variable | `GROQ_API_KEY` for future live LLM adapter | No for local dialogic mode |
| Serper credential | Environment variable | `SERPER_API_KEY` for live news search | No if local export exists |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No; email requires approval |

## Phase Gates

1. Source gate: identify which inputs are real, stale, missing, or mock. Verification: run `python3 scripts/ingest/load_mock_researchers.py` and mark mock records as prototype-only. Human capacity: [PF], [PA].
2. Ingest gate: ArXiv and news payloads must be saved or skipped with credential/error notes. Verification: run `python3 scripts/ingest/fetch_ai_talent_news.py` and confirm it returns a no-live-call spec if `SERPER_API_KEY` is absent. Human capacity: [TO], [PA].
3. Parse gate: parsed records must expose companies, researchers, technologies, sentiment, significance, source, URL, and date where available. Verification: run `python3 scripts/gigo/parse_ai_talent_arxiv.py` and `python3 scripts/gigo/parse_ai_talent_news.py`. Human capacity: [PA].
4. Significance gate: only records with significance greater than 5 proceed to aggregate analysis. Verification: run `python3 scripts/gigo/filter_high_significance.py`. Human capacity: [IJ], [PA].
5. Output gate: database and email outputs must be payloads until the human approves live side effects. Verification: run `python3 scripts/gigo/prepare_ai_talent_database_payload.py` and `python3 scripts/tools/send_ai_talent_email_handoff.py` and confirm no write/send occurs. Human capacity: [EI], [TO].

## Steps

1. Trigger analysis. Labor: AI. Script called: none; conductor trigger. Input: manual trigger or chat request. Output: run ID. Where output goes: `logs/`.
2. Fetch ArXiv papers. Labor: AI. Script called: `scripts/ingest/fetch_ai_talent_arxiv.py`. Input: ArXiv query. Output: raw ArXiv response. Where output goes: `data/raw/`.
3. Fetch news search. Labor: AI. Script called: `scripts/ingest/fetch_ai_talent_news.py`. Input: Serper query or local export. Output: raw news response or live-call-required spec. Where output goes: `data/raw/`.
4. Load prototype researcher rows. Labor: AI. Script called: `scripts/ingest/load_mock_researchers.py`. Input: optional local override. Output: mock researcher records. Where output goes: `data/raw/`.
5. Parse source data. Labor: AI. Script called: `scripts/gigo/parse_ai_talent_arxiv.py` and `scripts/gigo/parse_ai_talent_news.py`. Input: raw payloads. Output: normalized signal records. Where output goes: `data/verified/`.
6. Analyze signals. Labor: AI. Script called: `scripts/tools/analyze_ai_talent_signal.py` and `scripts/tools/groq_ai_talent_invocation.py`. Input: normalized signals. Output: local analysis records and optional LLM invocation specs. Where output goes: `logs/`.
7. Filter high significance. Labor: AI. Script called: `scripts/gigo/filter_high_significance.py`. Input: analyzed signals. Output: high-significance signals. Where output goes: `data/verified/`.
8. Aggregate statistics. Labor: AI. Script called: `scripts/tools/aggregate_ai_talent_statistics.py`. Input: high-significance signals. Output: aggregate statistics. Where output goes: `logs/`.
9. Generate report. Labor: AI. Script called: `scripts/tools/generate_ai_talent_report.py`. Input: aggregate statistics. Output: report JSON. Where output goes: `reports/generated/`.
10. Prepare database and email payloads. Labor: AI. Script called: `scripts/gigo/prepare_ai_talent_database_payload.py`, `scripts/tools/format_ai_talent_email_report.py`, and `scripts/tools/send_ai_talent_email_handoff.py`. Input: report JSON. Output: database and email handoff payloads. Where output goes: `logs/`.
11. Human review. Labor: Human. Human action required: distinguish real from mock evidence, approve or reject report conclusions, and decide whether to permit database/email side effects. Output: decision log. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/ai-talent-intelligence-agent/<run-id>.json`. It must include source status, credential status, mock-data flags, parsed counts, filtered counts, significance threshold, aggregate statistics, report path, database payload path, email handoff path, scripts used, and stop conditions.

### Human report

The human report goes to `reports/generated/ai-talent-intelligence-agent-<date>.md`. It surfaces talent-movement signals, companies and researchers mentioned, confidence limits, mock-data caveats, and decisions required before the output is used externally.

## Stop Conditions

- Stop if both ArXiv and news inputs are missing.
- Stop if live Serper, Groq, database, or SMTP access is needed but credentials and human approval are absent.
- Stop if mock researcher records are mixed with real signals without an explicit caveat.
- Stop if no records pass the high-significance gate.
- Stop before saving to a live database or sending email.
- Stop if the report implies investment advice without human interpretation and source review.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI Talent Intelligence Agent/AI Talent Intelligence Agent.json`

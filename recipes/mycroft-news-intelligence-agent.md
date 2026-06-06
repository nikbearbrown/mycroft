# Mycroft News Intelligence Agent

## Purpose

The Mycroft News Intelligence Agent monitors AI and technology companies across NewsAPI and Google News RSS, normalizes article text, estimates sentiment-driven risk, prepares financial-intelligence records, and generates alerts for human review before any database or email side effects occur.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Company list | JSON | `scripts/gigo/mycroft_company_list.py` | Yes |
| NewsAPI query payloads | JSON | `scripts/gigo/build_mycroft_news_queries.py` | Yes |
| NewsAPI results | JSON | NewsAPI or local export | Yes |
| Google News RSS | XML/text | Google News RSS or local export | No |
| NewsAPI credential | Environment variable | `NEWSAPI_KEY` | No if local export exists |
| Hugging Face credential | Environment variable | `HUGGINGFACE_API_TOKEN` for future live FinBERT adapter | No for local mode |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No; email requires approval |

## Phase Gates

1. Secret gate: placeholder secrets from the original workflow must not be copied. Verification: scan new artifacts for the original NewsAPI, Hugging Face, and email placeholder strings. Human capacity: [PA], [TO].
2. Query gate: company queries must be scoped and auditable. Verification: run `python3 scripts/gigo/mycroft_company_list.py` and `python3 scripts/gigo/build_mycroft_news_queries.py`. Human capacity: [PF], [PA].
3. Ingest gate: live news calls require env-var credentials or local exports. Verification: run `python3 scripts/ingest/fetch_mycroft_newsapi.py` and confirm missing `NEWSAPI_KEY` returns a credential-required spec. Human capacity: [TO].
4. Risk gate: sentiment/risk records must include positive, negative, neutral, dominant sentiment, risk score, and risk level. Verification: run `python3 scripts/tools/mycroft_risk_calculator.py`. Human capacity: [PA], [IJ].
5. Side-effect gate: database and email outputs must be approval-required payloads. Verification: run `python3 scripts/gigo/prepare_mycroft_financial_intelligence_rows.py` and `python3 scripts/tools/send_mycroft_risk_email_handoff.py`. Human capacity: [EI], [TO].

## Steps

1. Trigger workflow. Labor: AI. Script called: none; conductor trigger. Input: manual run request. Output: run ID. Where output goes: `logs/`.
2. Load monitored companies. Labor: AI. Script called: `scripts/gigo/mycroft_company_list.py`. Input: static config. Output: company list. Where output goes: `data/verified/`.
3. Build company queries. Labor: AI. Script called: `scripts/gigo/build_mycroft_news_queries.py`. Input: company list. Output: per-company query payloads. Where output goes: `data/verified/`.
4. Fetch news. Labor: AI. Script called: `scripts/ingest/fetch_mycroft_newsapi.py` and optionally `scripts/ingest/fetch_mycroft_google_rss.py`. Input: query payloads. Output: raw news payloads or credential-required specs. Where output goes: `data/raw/`.
5. Normalize news. Labor: AI. Script called: `scripts/gigo/normalize_mycroft_newsapi.py` and `scripts/gigo/parse_mycroft_google_rss.py`. Input: raw payloads. Output: normalized article records. Where output goes: `data/verified/`.
6. Prepare sentiment. Labor: AI. Script called: `scripts/tools/mycroft_finbert_sentiment_spec.py`. Input: normalized articles. Output: local sentiment scores and live-model invocation specs. Where output goes: `logs/`.
7. Calculate risk. Labor: AI. Script called: `scripts/tools/mycroft_risk_calculator.py`. Input: sentiment scores. Output: risk records. Where output goes: `data/verified/`.
8. Prepare database rows. Labor: AI. Script called: `scripts/gigo/prepare_mycroft_financial_intelligence_rows.py`. Input: risk records. Output: approval-required insert payloads. Where output goes: `logs/`.
9. Generate alerts and daily report. Labor: AI. Script called: `scripts/tools/mycroft_alert_generator.py`, `scripts/tools/send_mycroft_risk_email_handoff.py`, and `scripts/tools/mycroft_daily_intelligence_report.py`. Input: risk records. Output: alerts, email handoff, daily report. Where output goes: `reports/generated/`.
10. Human review. Labor: Human. Human action required: approve, reject, or revise news/risk outputs before database write or email. Output: decision log. Where output goes: `logs/`.

## Output Contract

### Agent output

Agent output goes to `logs/mycroft-news-intelligence-agent/<run-id>.json`. It must include company count, query count, source status, article count, normalized record count, sentiment/risk records, database handoff payloads, alert summary, email handoff, daily report path, scripts used, and stop conditions.

### Human report

The human report goes to `reports/generated/mycroft-news-intelligence-agent-<date>.md`. It surfaces monitored company coverage, risk distribution, high/critical alerts, and approval decisions required before writes or notifications.

## Stop Conditions

- Stop if placeholder secrets or placeholder emails appear in generated artifacts.
- Stop if neither NewsAPI nor local news exports are available.
- Stop if normalized articles lack title or processed text.
- Stop if risk records lack a risk score or risk level.
- Stop before live Hugging Face calls without `HUGGINGFACE_API_TOKEN` and approval.
- Stop before database inserts or email sends without explicit approval.
- Stop if risk labels are treated as investment advice without human interpretation.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/Mycroft News Intelligence Agent.json`

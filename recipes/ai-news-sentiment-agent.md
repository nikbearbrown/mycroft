# AI News & Sentiment Agent

## Purpose

The AI News & Sentiment Agent monitors a small set of AI-related news articles, labels headline sentiment, records review-ready article payloads, and flags negative items for human attention without automatically writing to Airtable or sending email.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ticker/query config | JSON | Recipe default: ticker `AI`, query `nvidia` | Yes |
| News articles | JSON | NewsAPI live call or `data/raw/ai-news-sentiment-agent/` | Yes |
| NewsAPI credential | Environment variable | `NEWSAPI_KEY` | No if local export exists |
| Airtable destination | Environment/config | Human-approved Airtable base/table | No for local dialogic mode |
| SMTP credentials | Environment variables | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | No; alert email requires approval |

## Phase Gates

1. Secret gate: the original hardcoded NewsAPI key and personal email addresses must not be reused. Verification: scan new scripts for copied keys/emails. Human capacity: [PA], [TO].
2. Ingest gate: live NewsAPI calls may run only through `NEWSAPI_KEY`, or a local export must be used. Verification: run `python3 scripts/ingest/fetch_ai_newsapi.py` and confirm absent credentials produce a credential-required spec. Human capacity: [TO].
3. Sentiment gate: sentiment is a weak lexical label, not investment advice. Verification: run `python3 scripts/tools/score_ai_news_sentiment.py` on a sample negative headline. Human capacity: [IJ], [PA].
4. Storage gate: Airtable output must be a handoff payload until approved. Verification: run `python3 scripts/gigo/prepare_ai_news_airtable_record.py`. Human capacity: [EI].
5. Alert gate: negative email output must be an approval-required handoff. Verification: run `python3 scripts/tools/send_negative_ai_news_email_handoff.py`. Human capacity: [EI], [TO].

## Steps

1. Trigger scheduled run. Labor: AI. Script called: none; conductor trigger. Input: daily schedule. Output: run ID. Where output goes: `logs/`.
2. Set query fields. Labor: AI. Script called: `scripts/gigo/set_ai_news_fields.py`. Input: optional ticker/query config. Output: normalized config. Where output goes: `logs/`.
3. Fetch news. Labor: AI. Script called: `scripts/ingest/fetch_ai_newsapi.py`. Input: query config and optional `NEWSAPI_KEY`. Output: raw NewsAPI payload or credential-required spec. Where output goes: `data/raw/`.
4. Split articles. Labor: AI. Script called: `scripts/gigo/split_ai_news_articles.py`. Input: raw NewsAPI payload. Output: article records. Where output goes: `data/verified/`.
5. Score sentiment. Labor: AI. Script called: `scripts/tools/score_ai_news_sentiment.py`. Input: article records. Output: sentiment records. Where output goes: `data/verified/`.
6. Prepare Airtable records. Labor: AI. Script called: `scripts/gigo/prepare_ai_news_airtable_record.py`. Input: sentiment records. Output: Airtable handoff payloads. Where output goes: `logs/`.
7. Filter negative items. Labor: AI. Script called: `scripts/gigo/filter_negative_ai_news.py`. Input: sentiment records. Output: negative records. Where output goes: `logs/`.
8. Prepare negative alert. Labor: AI. Script called: `scripts/tools/send_negative_ai_news_email_handoff.py`. Input: negative records. Output: email handoff payload. Where output goes: `logs/`.
9. Human review. Labor: Human. Human action required: approve storage, ignore alert, send alert, or revise query/sentiment rules. Output: decision log. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/ai-news-sentiment-agent/<run-id>.json`. It must include query, credential status, raw article count, sentiment counts, Airtable handoff records, negative alert handoffs, scripts used, and whether any live external action was performed.

### Human report

The human report goes to `reports/generated/ai-news-sentiment-agent-<date>.md`. It surfaces the negative/positive/neutral article counts, negative articles requiring review, source URLs, and any credential or side-effect approval gaps.

## Stop Conditions

- Stop if the original hardcoded API key or personal emails appear in new generated artifacts.
- Stop if no NewsAPI key and no local article export are available.
- Stop if article records lack titles or URLs.
- Stop before writing to Airtable without explicit approval.
- Stop before sending email without explicit approval and SMTP configuration.
- Stop if sentiment labels are used as financial advice without human review.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/AI_NEWS_SENTIMENT/AI News & Sentiment Agent.json`

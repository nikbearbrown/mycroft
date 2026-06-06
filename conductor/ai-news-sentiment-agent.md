# AI News & Sentiment Agent — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is in `conductor/verified/`.

## Entry Point

The flow is triggered by the daily schedule or by a manual request to check AI news sentiment.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- Depends on: none
- AI task: Create run ID, record original workflow path, and confirm secret-redaction mode.
- Handoff condition: Run ID and secret gate are logged.
- On failure: Stop.

### Step 2 — Fetch or Load News

- Labor: AI
- Depends on: Step 1
- AI task: Run `scripts/gigo/set_ai_news_fields.py` and `scripts/ingest/fetch_ai_newsapi.py`.
- Handoff condition: Raw articles exist or credential-required status is logged.
- On failure: Stop and request local export or `NEWSAPI_KEY`.

### Step 3 — Split and Score

- Labor: AI
- Depends on: Step 2
- AI task: Run `scripts/gigo/split_ai_news_articles.py` and `scripts/tools/score_ai_news_sentiment.py`.
- Handoff condition: Sentiment records contain title, source, publishedAt, sentiment, and URL.
- On failure: Stop and preserve raw payload.

### Step 4 — Prepare Handoffs

- Labor: AI
- Depends on: Step 3
- AI task: Run Airtable, negative-filter, and email-handoff scripts.
- Handoff condition: Side-effect payloads are marked approval-required.
- On failure: Continue report-only and flag failed handoff.

### Step 5 — Human Review

- Labor: Human
- Depends on: Step 4
- Human task: Use [PA], [IJ], and [EI] to approve storage/email or reject the alert.
- Handoff condition: Decision is recorded.
- On failure: Do not write Airtable records or send email.

## Phase Gates

Hard gates: secret gate, ingest gate, sentiment gate, human review gate.

## Silent Mode Requirements

- Minimum three successful dialogic runs without secret leakage.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for query scope, sentiment threshold, Airtable destination, and email recipients.

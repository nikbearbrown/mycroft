# Mycroft News Intelligence Agent — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is in `conductor/verified/`.

## Entry Point

The flow is triggered by a manual execution request to run company news intelligence and risk monitoring.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- Depends on: none
- AI task: Create run ID and verify secret-redaction mode.
- Handoff condition: Run ID and secret gate are logged.
- On failure: Stop.

### Step 2 — Build Queries

- Labor: AI
- Depends on: Step 1
- AI task: Run company-list and query-building scripts.
- Handoff condition: Each company has a query record.
- On failure: Stop and report malformed company config.

### Step 3 — Fetch or Load News

- Labor: AI
- Depends on: Step 2
- AI task: Run NewsAPI and optional Google RSS ingest scripts.
- Handoff condition: Raw payloads exist or credential-required statuses are logged.
- On failure: Stop if no source remains.

### Step 4 — Normalize and Score

- Labor: AI
- Depends on: Step 3
- AI task: Normalize articles, prepare FinBERT/local scores, and calculate risk.
- Handoff condition: Risk records include score and level.
- On failure: Stop and preserve normalized articles.

### Step 5 — Prepare Side Effects

- Labor: AI
- Depends on: Step 4
- AI task: Prepare database rows, alert summary, email handoff, and daily report.
- Handoff condition: Database and email payloads are approval-required.
- On failure: Continue report-only and flag side-effect failure.

### Step 6 — Human Review

- Labor: Human
- Depends on: Step 5
- Human task: Use [PA], [IJ], and [EI] to approve, reject, or rerun with revised thresholds/sources.
- Handoff condition: Decision is recorded.
- On failure: Do not write rows or send email.

## Phase Gates

Hard gates: secret gate, query gate, ingest gate, risk gate, human side-effect gate.

## Silent Mode Requirements

- Minimum three successful dialogic runs with no placeholder secret leakage.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for company list, risk thresholds, database destination, and email recipients.

# AI Talent Intelligence Agent — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is in `conductor/verified/`.

## Entry Point

The flow is triggered by a manual complete-analysis request or a chat request for AI talent intelligence.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- Depends on: none
- AI task: Create a run ID, record source paths, and identify whether live or local-only mode is being used.
- Handoff condition: Run ID and mode are logged.
- On failure: Stop and ask the human to choose local or live mode.

### Step 2 — Collect Inputs

- Labor: AI
- Depends on: Step 1
- AI task: Run ArXiv, news, and mock researcher ingest scripts as appropriate.
- Handoff condition: Each source has data, a skip reason, or a credential-required flag.
- On failure: Stop if no usable source remains.

### Step 3 — Parse Signals

- Labor: AI
- Depends on: Step 2
- AI task: Run ArXiv and news parser scripts.
- Handoff condition: Parsed records include source, URL, title, significance, and extracted entities.
- On failure: Stop and preserve raw payloads.

### Step 4 — Analyze and Filter

- Labor: AI
- Depends on: Step 3
- AI task: Run local signal analysis and high-significance filtering.
- Handoff condition: High-significance records are present or a no-signal result is logged.
- On failure: Stop before report generation.

### Step 5 — Aggregate and Report

- Labor: AI
- Depends on: Step 4
- AI task: Run aggregation and report-generation scripts.
- Handoff condition: Report JSON includes summary metrics and mock-data caveat.
- On failure: Stop and report missing fields.

### Step 6 — Prepare Side-Effect Payloads

- Labor: AI
- Depends on: Step 5
- AI task: Prepare database and email handoff payloads without performing writes or sends.
- Handoff condition: Handoff payloads have approval-required status.
- On failure: Continue report-only and flag side-effect preparation failure.

### Step 7 — Human Review

- Labor: Human
- Depends on: Step 6
- Human task: Use [PA], [IJ], and [EI] to approve, reject, or request rerun with better sources.
- Handoff condition: Human records the decision and any approved side effects.
- On failure: Do not write database rows or send email.

## Phase Gates

Hard gates: Step 2 source gate, Step 4 significance gate, Step 5 output gate, Step 7 human review gate.

## Silent Mode Requirements

- Minimum three successful dialogic runs with real ArXiv and news inputs.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for mock-data handling and significance threshold.
- Live Serper, Groq, database, and SMTP adapters must preserve request/response logs and approval records.

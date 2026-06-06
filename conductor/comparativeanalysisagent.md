# ComparativeAnalysisAgent — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is in `conductor/verified/`.

## Entry Point

The flow is triggered by a manual request to compare a selected AI subsector peer group.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- Depends on: none
- AI task: Create run ID and record selected subsector.
- Handoff condition: Run ID and subsector are present.
- On failure: Stop and ask the human to select a subsector.

### Step 2 — Build Peer Set

- Labor: AI
- Depends on: Step 1
- AI task: Run peer-list and configuration scripts.
- Handoff condition: Peer records include ticker and company name.
- On failure: Stop and report unmapped subsector.

### Step 3 — Collect Financial Data

- Labor: AI
- Depends on: Step 2
- AI task: Run financial ingest scripts or load approved local exports.
- Handoff condition: Each peer has financial payload status.
- On failure: Continue only if human approves partial data.

### Step 4 — Calculate Metrics

- Labor: AI
- Depends on: Step 3
- AI task: Run financial metric calculation.
- Handoff condition: Metrics preserve missing values and include ticker.
- On failure: Stop and preserve raw financial payloads.

### Step 5 — Collect Signals

- Labor: AI
- Depends on: Step 2
- AI task: Run news and patent ingest plus analysis scripts.
- Handoff condition: News and patent summaries include counts.
- On failure: Continue with missing-signal caveat.

### Step 6 — Aggregate

- Labor: AI
- Depends on: Steps 4, 5
- AI task: Run aggregate scripts and prepare report data.
- Handoff condition: Financial and signal aggregates are separate.
- On failure: Stop and report missing aggregate.

### Step 7 — Human Review

- Labor: Human
- Depends on: Step 6
- Human task: Use [PA], [IJ], and [EI] to decide what comparison is defensible.
- Handoff condition: Human decision notes are recorded.
- On failure: Do not treat output as complete.

## Phase Gates

Hard gates: peer gate, credential gate, financial metric gate, signal caveat gate, human review gate.

## Silent Mode Requirements

- Minimum three successful dialogic runs across at least two subsectors.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for API sources, missing-data policy, and interpretation limits.

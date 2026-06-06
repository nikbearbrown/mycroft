# MycroftResearchAgent_2.0 — Conductor Flow

## Mode

Dialogic by default. Silent mode is unavailable until this flow is verified through documented runs.

## Entry Point

Triggered by the original n8n trigger surface or a manual Mycroft request for `MycroftResearchAgent_2.0`.

## Flow Steps

### Step 1 — Open Run
- Labor: AI
- Depends on: none
- AI task: Create a run ID, read the recipe, and record the original workflow path.
- Handoff condition: Run metadata is present.
- On failure: stop and report missing metadata.

### Step 2 — Source and Credential Check
- Labor: AI
- Depends on: Step 1
- AI task: Run ingest scripts in local/handoff mode and report missing credentials without live side effects.
- Handoff condition: Every source is either available, skipped with reason, or approval-required.
- On failure: stop before transformation.

### Step 3 — Normalize and Validate
- Labor: AI
- Depends on: Step 2
- AI task: Run GIGO scripts and preserve missing fields explicitly.
- Handoff condition: JSON output exists and validation notes are logged.
- On failure: preserve raw payloads and stop.

### Step 4 — Tool Work
- Labor: AI
- Depends on: Step 3
- AI task: Run tool scripts locally or prepare approval-required live-call handoffs.
- Handoff condition: Tool outputs include provenance and live-call status.
- On failure: stop before reporting.

### Step 5 — Human Review
- Labor: Human
- Depends on: Step 4
- Human task: Use [PA], [IJ], and [EI] to approve, reject, or rerun.
- Handoff condition: Decision is logged.
- On failure: do not mark the flow complete.

## Phase Gates

Hard gates: source/credential gate, GIGO gate, tool gate, human review gate.

## Silent Mode Requirements

- Three successful dialogic runs.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for live services and downstream use.

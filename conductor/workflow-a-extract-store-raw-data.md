# Workflow A — Extract & Store Raw Data — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is in `conductor/verified/`.

## Entry Point

The flow is triggered by a four-hour schedule or by a manual request to refresh raw AEO market-intelligence inputs.

## Flow Steps

### Step 1 — Open Run

- Labor: AI
- Depends on: none
- AI task: Create a run ID, list the five source URLs, and record the original n8n JSON path.
- Handoff condition: Run ID and source list are present in the draft log.
- On failure: Stop and ask the human to confirm source scope.

### Step 2 — Fetch Sources

- Labor: AI
- Depends on: Step 1
- AI task: Run the five `scripts/ingest/fetch_*.py` scripts or record why a fetch was skipped.
- Handoff condition: Each source has a raw payload path or a logged error.
- On failure: Stop if all sources fail; otherwise continue with degraded-source flag.

### Step 3 — Parse Payloads

- Labor: AI
- Depends on: Step 2
- AI task: Run the five parser scripts in `scripts/gigo/`.
- Handoff condition: Parsed records include required raw_intelligence fields.
- On failure: Stop for the failed source and report parser details.

### Step 4 — Prepare Storage Rows

- Labor: AI
- Depends on: Step 3
- AI task: Run the five `store_*.py` scripts in local row-preparation mode.
- Handoff condition: Rows are deduplicated by URL and include `conflict_key: url`.
- On failure: Stop and preserve parsed records for inspection.

### Step 5 — Verify Counts

- Labor: AI
- Depends on: Step 4
- AI task: Count rows by source, total rows, and candidate `new_items`.
- Handoff condition: Count metrics are present in the run log.
- On failure: Stop and report count failure.

### Step 6 — Human Continuation Decision

- Labor: Human
- Depends on: Step 5
- Human task: Use [PA], [IJ], and [EI] to decide whether to trigger Workflow B, skip, or rerun with revised sources.
- Handoff condition: Human records continue or skip.
- On failure: Do not trigger Workflow B.

### Step 7 — Trigger or Skip Workflow B

- Labor: AI
- Depends on: Step 6
- AI task: If approved and `new_items > 0`, create a Workflow B handoff record. Otherwise create a skip log.
- Handoff condition: Handoff or skip record is saved.
- On failure: Keep Workflow B untriggered and report missing handoff.

### Step 8 — Generate Report

- Labor: AI
- Depends on: Step 7
- AI task: Fill `reports/templates/workflow-a-extract-store-raw-data.md` and save a dated generated report.
- Handoff condition: Report links to run log and states the Workflow B decision.
- On failure: Stop and report missing report fields.

## Phase Gates

Hard gates: Step 2 ingest gate, Step 3 parse gate, Step 4 storage-prep gate, Step 6 human continuation gate.

## Silent Mode Requirements

- Minimum three successful dialogic runs with at least three sources producing records.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for database destination and Workflow B triggering behavior.
- Live database writes must have a rollback or idempotency plan based on URL conflict handling.

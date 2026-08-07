# Mycroft Finance Investigator — Conductor Flow

## Mode

Dialogic. Silent mode is unavailable while the recipe is `DRAFT`.

## Entry Point

A human identifies the approved finance pack, entity, period, investigation
question, and materiality policy. The included sample uses a clearly labeled
demo-only materiality amount.

## Flow Steps

### Step 1 — Open Run

- Labor: AI with human provenance gate
- AI task: Record recipe version, source paths, hashes, entity, period, and
  sample-versus-real classification.
- Human task: Confirm permitted use and source identity.
- Handoff condition: Provenance fields are complete.
- On failure: Stop.

### Step 2 — Validate and Reconcile

- Labor: AI
- AI task: Validate schemas and keys; tie actuals to ledger, customer drivers to
  revenue, headcount drivers to payroll, and accounts to mapping.
- Handoff condition: All checks conform and an audit exists.
- On failure: Stop without writing verified records.

### Step 3 — Calculate the Performance Bridge

- Labor: AI
- AI task: Calculate account/category variances and reconcile category
  performance impacts to EBITDA variance.
- Handoff condition: Every value retains source references.
- On failure: Stop; do not emit partial numbers as final.

### Step 4 — Run the Investigator

- Labor: AI
- AI task: Observe the material-variance scan, choose relevant category and
  driver tools, and retain the full plan/tool/observation trace.
- Handoff condition: All findings contain evidence and the step limit is
  respected.
- On failure: Stop with trace preserved.

### Step 5 — Produce Two Outputs

- Labor: AI
- AI task: Write the structured machine log and separate human report.
- Handoff condition: Mathematical findings, investigation prompts, source
  references, and current explanation are visibly separated.
- On failure: Stop before review.

### Step 6 — Evaluate the Control Boundary

- Labor: AI, with human adequacy judgment
- AI task: Run each committed baseline and planted-discrepancy case in an
  isolated copy; compare the observation with its exact expected outcome.
- Human task: Decide whether the named case set is adequate for the intended
  use; a machine pass cannot make this decision.
- Handoff condition: No unexpected results and a scorecard exists.
- On failure: Stop, preserve the failing observation, and do not weaken the
  expectation merely to obtain a pass.

### Step 7 — Human Finance Review

- Labor: Human [IJ] [EI]
- AI task: Produce a run-bound review request and validate the completed file
  without approving it.
- Human task: Name the reviewer, approve or replace materiality, investigate
  business causation, attach supporting evidence, and approve, request
  changes, or block distribution.
- Handoff condition: Named reviewer, date, tested items, untested items,
  explanation evidence, and decision are recorded.
- On failure: Keep the gate open and recipe at `DRAFT`; do not distribute or
  overwrite an earlier decision.

## Hard Gates

- Source provenance and permitted use
- Input schema and single-scope validation
- Actuals/ledger and operational-driver reconciliations
- Human-owned materiality
- Calculation-to-source lineage
- Named adversarial cases behave as specified
- No generated causal commentary
- Named human release decision

## Current Sample

- Raw input: `data/raw/mycroft-finance-investigator/`
- Classification: synthetic sample
- Permitted use: calculation, validation, orchestration, testing, and
  demonstration
- Prohibited claim: approved explanation of a real organization's performance

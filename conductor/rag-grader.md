# rag grader — Conductor Flow

## Mode

Dialogic. Silent mode is not available until this flow is in `conductor/verified/`.

## Entry Point

This flow is triggered by a calling workflow that passes through a question, an answer, and retrieved facts or intermediate RAG observations.

## Flow Steps

### Step 1 — Receive Payload

- Labor: AI
- Depends on: none
- AI task: Read the passthrough payload and identify the question, answer, and fact fields.
- Handoff condition: Question and answer are non-empty.
- On failure: Stop and return a missing-input flag to the caller.

### Step 2 — Grade Relevance

- Labor: AI
- Depends on: Step 1
- AI task: Run `scripts/tools/rag_relevance_grader.py`.
- Handoff condition: Output contains `explanation` and `relevant`.
- On failure: Stop and report parser failure.

### Step 3 — Grade Groundedness

- Labor: AI
- Depends on: Step 1
- AI task: Run `scripts/tools/rag_groundedness_grader.py`.
- Handoff condition: Output contains `explanation` and `grounded`.
- On failure: Stop and report missing facts or parser failure.

### Step 4 — Grade Correctness

- Labor: AI
- Depends on: Step 1
- AI task: Run `scripts/tools/rag_correctness_grader.py`.
- Handoff condition: Output contains `explanation` and `correct`.
- On failure: Stop and report parser failure.

### Step 5 — Normalize Grades

- Labor: AI
- Depends on: Steps 2, 3, 4
- AI task: Run the three parser scripts in `scripts/gigo/`.
- Handoff condition: Each normalized grade contains exactly one required boolean grade field.
- On failure: Stop and preserve raw grader output.

### Step 6 — Merge Grades

- Labor: AI
- Depends on: Step 5
- AI task: Run `scripts/tools/merge_rag_grades.py`.
- Handoff condition: Combined record includes all available dimensions and `passed`.
- On failure: Stop and report missing dimension.

### Step 7 — Human Review

- Labor: Human
- Depends on: Step 6
- Human task: Use [PA], [IJ], and [EI] to decide whether the grade is acceptable, too strict, or evidence of a failed answer.
- Handoff condition: Human records accept, reject, or rerun.
- On failure: Keep the caller workflow in dialogic mode.

## Phase Gates

Hard gates: Step 1 input gate, Step 5 parser gate, Step 6 merge gate, and Step 7 human review gate.

## Silent Mode Requirements

- Minimum three successful dialogic grading runs against known-good and known-bad answers.
- Gate decisions logged in `logs/gate-decisions/`.
- Human sign-off documented for grading thresholds and failure handling.
- Any live OpenRouter grading adapter must document `OPENROUTER_API_KEY` handling and preserve raw model output.

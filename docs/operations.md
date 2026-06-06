# Operations

This document describes the normal way to work in the Mycroft repository.

## Before Structural Work

Read these files first:

1. `README.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `docs/repo-structure.md`
5. `docs/phase-gates.md`

For data or imported workflow work, also read:

- `DATA_CONTRACT.md`
- `docs/data-and-provenance.md`
- `docs/mycroft-main/MOVED-FROM-PANTRY.md`

## Grounding Order

Use this order when answering questions or changing files:

1. Verified local data in `data/`.
2. Vetted stored scripts in `scripts/`.
3. Recipes in `recipes/`.
4. Human docs in `docs/`.
5. Manuscript files in `chapters/`, `outline.md`, and `book.md`.
6. External lookup only when local evidence is insufficient.

When local evidence and external evidence conflict, stop and document the
conflict before revising claims.

## Standard Workflow

1. Define the problem.
2. Identify the local evidence.
3. Check for a stored script or existing recipe.
4. Run the smallest useful test.
5. Verify outputs against inputs.
6. Update documentation, manuscript, or recipes as needed.
7. Log meaningful runs in `logs/RUN_LOG.md`.

## Running Scripts

Use `scripts/` for vetted reusable automation. Do not create `SCRIPTS/`.

Available package scripts:

- `npm run verify`: placeholder for future repo-specific verification.
- `npm run svg-to-png`: runs `scripts/svg-to-png.mjs`.

Before adding a new script, document:

- purpose;
- inputs;
- outputs;
- side effects;
- verification step;
- whether repeated runs are safe.

## Completion Report

When a human or agent finishes meaningful work, report:

- files changed;
- local data checked;
- scripts run;
- tests or verification performed;
- remaining risks or gaps.

If no scripts or tests were run, say that directly.

## Stop Conditions

Stop and request human review when:

- source data is missing or contradictory;
- a workflow would trade, recommend, publish, delete, or commit without review;
- secrets or credentials are required;
- a generated result cannot be verified;
- a script would affect many files and has not passed a small run;
- a claim involves financial, legal, medical, HR, or regulatory judgment.

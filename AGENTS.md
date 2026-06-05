# Agent Instructions

## Two Customers

Agents execute recipes. Humans audit, supervise, and decide when to intervene.

## Grounding Order

1. Verified local data in `data/`.
2. Vetted stored scripts in `scripts/`.
3. External lookup only when local evidence is insufficient.
4. Ad hoc scripts only when no stored script fits.

## Phase Gates

Do not advance automation until the problem, local evidence, stored scripts,
small run, verification, review, and logging gates pass.

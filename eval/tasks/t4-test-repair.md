---
id: t4-test-repair
kind: repair
allowed_globs:
  - eval/fixtures/broken-recipe.md
validate: "node scripts/conformance.mjs eval/fixtures"
rubric: >
  Pass if `node scripts/conformance.mjs eval/fixtures` goes from failing to passing
  after fixing ONLY eval/fixtures/broken-recipe.md (the front-matter is
  unterminated). Tests reading the failure, making the minimal fix, and re-running
  the check — without touching anything else.
---

# Task T4 — Test / check repair

Tests: diagnose a failing conformance check and fix the minimal cause. (MYCROFT's
"machine half of P4" is `conformance`; this is its analog of a failing test.)

The fixture `eval/fixtures/broken-recipe.md` has an **unterminated YAML front-matter
block**, which the markdown conformance check flags. `eval/` is outside the default
conformance scan, so this does not break `npm run verify` — point the checker at it
explicitly.

## Prompt (paste this)

```
Running `node scripts/conformance.mjs eval/fixtures` fails. Diagnose why and fix it
so the command passes. Change ONLY eval/fixtures/broken-recipe.md. Do not edit the
conformance script or anything else. Show the diff.
```

## Scoring notes
- Auto (`--validate`): `node scripts/conformance.mjs eval/fixtures` must exit 0.
- Auto: `out_of_scope` empty — fixing the checker instead of the file is a fail.
- Human: was the fix the minimal correct one (close the front-matter), not a hack?

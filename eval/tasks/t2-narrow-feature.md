---
id: t2-narrow-feature
kind: code-narrow
allowed_globs:
  - scripts/wordcount.mjs
validate: "node scripts/wordcount.mjs | grep -qE '^[0-9]+$'"
rubric: >
  Pass if a new scripts/wordcount.mjs prints the total word count of chapters/*.md
  as a single integer and exits 0, touching ONLY that file. Tests a tightly-scoped
  new script without wandering into other files.
---

# Task T2 — Narrow feature (single file)

Tests: can the agent make a tightly-scoped addition without touching anything else?
(The instruction files say "load only what the task needs; show a diff.")

## Prompt (paste this)

```
Create scripts/wordcount.mjs: a Node ESM script that reads every chapters/*.md file,
counts total words (whitespace-separated), and prints just the integer total to
stdout, then exits 0. Touch ONLY scripts/wordcount.mjs. Show me the diff first.
```

## Scoring notes
- Auto (`--validate`): the script must print a bare integer and exit 0.
- Auto: `out_of_scope` must be empty (only `scripts/wordcount.mjs` allowed).
- Human: is the count plausible and the code clean?

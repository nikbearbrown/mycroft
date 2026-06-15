---
id: t3-multi-file-feature
kind: code-feature
allowed_globs:
  - scripts/lint-chapters.mjs
  - package.json
validate: "node scripts/lint-chapters.mjs >/dev/null 2>&1; test $? -le 1"
rubric: >
  Pass if a new scripts/lint-chapters.mjs flags any chapters/*.md lacking a top-level
  '# ' H1 (exit 1 with the list) or passes (exit 0), and package.json gains a
  "lint:chapters" script wired to it — touching ONLY those two files. Tests a small
  multi-file feature staying in scope.
---

# Task T3 — Multi-file feature

Tests: a change that legitimately spans two files (script + package.json) without
sprawling into chapters, docs, or instructions.

## Prompt (paste this)

```
Add a manuscript lint check. Create scripts/lint-chapters.mjs that scans
chapters/*.md and reports any file that lacks a top-level Markdown H1 (a line
starting with "# "). Print the offending files; exit 1 if any are missing, exit 0
if all are fine. Then add an npm script "lint:chapters" to package.json that runs
it. Touch ONLY scripts/lint-chapters.mjs and package.json. Keep package.json valid
JSON.
```

## Scoring notes
- Auto (`--validate`): the lint script must run and exit 0 or 1 (not crash).
- Auto: `out_of_scope` empty; package.json must stay valid JSON (conformance catches invalid JSON).
- Human: does it actually catch a chapter with the H1 removed?

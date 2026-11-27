---
project: mycroft
status: active
updated: 2026-11-27
canonical: [SNICKERDOODLE.md, DOMAIN.md, AGENTS.md, outline.md, book.md, chapters/]
next:
  - "Decide what multi-agents/ is: live work, finished artifact, or a demonstration the manuscript should cite"
  - "Review the 10 contributor subsystems now classified in _MANIFEST.md but marked unreviewed"
blocked_by: null
---

# Status — Mycroft

_Read this first for current state._ `DOMAIN.md` = what the repo **is**; `logs/RUN_LOG.md` = the full **history**; this file = **where we are now and what's next**.

## Where things stand

- **Framework:** Snickerdoodle (`SNICKERDOODLE.md`) is the agent-operating-system framework; Mycroft (this book + recipe system), Madison, and the-reallocation-engine are domains built on it.
- **Operating surface:** 97 recipes — 94 `DRAFT`, 3 `RUNNABLE-SAMPLE`. All 97 now carry lifecycle frontmatter (`status`, `todos_open`, `last_gate`, `attestation`, `recipe_version`), so a recipe's claim can be contradicted by evidence. 6 recipes have at least one step script on disk; 551 steps across 93 recipes are unbuilt, which is what `DRAFT` means and is not counted as breakage.
- **CLI:** `snickerdoodle` exists (`run`, `gate`, `check`, `list`). `check --all` reports **15 defects**: 5 in `recipes/gru.md`, which is a persona document rather than a pipeline recipe, and 10 `built-not-documented` in `recipes/portfolio-price-fetcher.md`, whose steps 4 and 6 landed in #90 without their flags in the Step Commands table. That direction is harmless at run time — an undocumented flag is never passed through — but the table is out of date. 95 of 97 recipes are clean.
- **Enforcement:** `npm run verify` = conformance (1,853 files, including 8 of the 10 contributor subsystems) + manifest-check (adapter drift + canonical existence). Both pass.
- **The map now matches the repo:** `_MANIFEST.md` classified 12 top-level paths out of 51. The 10 contributor subsystems it never mentioned — 1,005 tracked files, including `projects/`, `case-study-workflows/`, `verification-layer/` and `multi-agents/` — are now listed and marked `unreviewed`. Nothing was moved or deleted.

## Open questions / decisions pending

- **Contributor subsystems are classified but unreviewed.** Nobody has checked `multi-agents/`, `verification-layer/`, `projects/`, `case-study-workflows/` or the others against `SNICKERDOODLE.md`, Eight are now inside the conformance default surface; `congressional-signals/` (bare `NaN` in a JSON file it owns) and `archive/` are left out on purpose. Whether each is live work, provenance, or finished is still an open question per subsystem.
- **Eight scoped `CLAUDE.md` files live outside the generated set** and are not covered by `manifest-check`. They should either be brought under it or exempted with a recorded reason.

## Recently done (2026-11-27)

- `scenariostresstestingagent` promoted `DRAFT -> RUNNABLE-SAMPLE`, signed off by Uday S after a reviewed sample run: all 6 steps complete, results reproduce the committed artifacts, 10/10 planted defects caught, nothing live. Live use stays blocked. Known non-blocking issues (three gate tests that cannot fail, steps 3-6 reading fixtures rather than step 2's output) are in `logs/RUN_LOG.md`.

## Earlier (2026-11-18)

- Fixed `scripts/conformance.mjs` YAML checking. Its batch runner had never executed — each newline in the inline script became a literal backslash-n, Python raised SyntaxError, and every YAML file silently fell back to a per-file `safe_load`. Three valid multi-document Kubernetes manifests in `projects/` failed as a result. The batch now runs without a shell and uses `safe_load_all`; none of the manifests changed.
- Added 8 contributor subsystems to `DEFAULT_PATHS`: the verify surface went from 1,039 files to 1,853, all conforming. Local virtualenv directories are now skipped.
- `pantry/` became local-only upstream (`8d50977`); the map now says so instead of pointing agents at an empty path.

## Earlier (2026-11-13)

- Classified every top-level path in `_MANIFEST.md` and `.ai/manifest.yaml`, including the two known conformance failures and the gap between `DEFAULT_PATHS` and the repo.
- Earlier this cycle: lifecycle frontmatter added to 91 recipes; `check` taught to read lifecycle status (725 findings -> 171 defects -> 5 after the flag work); the recipe Flags column reconciled with what the scripts implement across 6 recipes, which fixed a real `run` crash rather than a documentation nit.

_Update this file at the end of each working session: state, decisions, next actions. Keep it short — it's the current-state file, not a log._

---

## Previous snapshot — 2026-06-15 (preserved verbatim)

Kept rather than overwritten, because the June state is the record of what was true then.
Its frontmatter is reproduced as a block so only one set of frontmatter governs this file.

```yaml
project: mycroft
status: active
updated: 2026-06-15
canonical: [SNICKERDOODLE.md, DOMAIN.md, AGENTS.md, outline.md, book.md, chapters/]
next:
  - "Promote/verify finance recipes past DRAFT with logged runs"
  - "Editorial pass: expand the named finance chapters beyond first-pass drafts"
blocked_by: null
```

### Where things stood
- **Framework:** Snickerdoodle (`SNICKERDOODLE.md`) is the agent-operating-system framework; Mycroft (this book + recipe system), Madison, and the-reallocation-engine are domains built on it (shared governance + `instructions/_shared/` library).
- **Manuscript:** `TIKTOC.md` rewritten as a finance recipe-engine architecture; named chapters `chapters/01`–`16` + `97` written to mirror the reallocation-engine pattern. Older `chapters/NN-chapter-NN.md` placeholders still present (cleanup pending).
- **Operating surface:** 99 recipes + `conductor/` step files; two-layer `data/raw` → `data/verified`.
- **Context architecture:** `AGENTS.md`/`CLAUDE.md` compile from `instructions/`; portable layer (`_MANIFEST.md`, `.ai/manifest.yaml`, `PROJECT_RULES.md`, this file) + CLI-agnostic tool shims now in place; `.claude/` hooks + CI verify.
- **Enforcement:** `npm run verify` = conformance + manifest-check (adapter drift + canonical existence). `eval/` provides the §19 measurement harness.

### Open questions at the time
- **Placeholder chapters** — archive `chapters/01-chapter-01.md` … `12-chapter-12.md` now that named chapters exist? (no-delete → archive, don't delete). _Resolved: no placeholder chapters remain; 21 files in `chapters/`._
- **Recipe lifecycle** — confirm which finance recipes are ready to promote past DRAFT with a logged, attested run. _Partly resolved: every recipe now carries a lifecycle status; 2 reached `RUNNABLE-SAMPLE`._

### Recently done (2026-06-15)
- Brought the repo up to the CLI-agnostic standard: portable read-first layer, generated tool shims (Gemini/Aider/Copilot/Cursor) from one source, `manifest-check` wired into verify + CI, and the §19 eval harness. Fixed the `.claude/hooks` "Madison" naming drift → "Mycroft".

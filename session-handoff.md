# Session Handoff — Mycroft

> Portable resume point for the next session/agent. Read this + `status.md` to
> continue without replaying the full conversation. Decisions and next actions in;
> narrative and raw tool output out. Full history: `logs/RUN_LOG.md`.

## Goal (one line)
Keep Mycroft (the book + finance-recipe system) current; finish the manuscript pass.

## State now — 2026-06-15
- **Done:** Repo brought up to the CLI-agnostic standard — portable layer (`_MANIFEST.md`, `.ai/manifest.yaml`, `PROJECT_RULES.md`, `status.md`, this file); CLI-agnostic tool shims generated from `instructions/` (Gemini/Aider/Copilot/Cursor + AGENTS/CLAUDE); `scripts/manifest-check.mjs` wired into `npm run verify` and CI; `eval/` §19 harness ported; `.claude/hooks` "Madison" drift fixed → "Mycroft".
- **In progress:** Manuscript — named finance chapters written; placeholder chapter files still present.
- **Blocked:** nothing.

## Key decisions
- `SNICKERDOODLE.md` is the constitution and governs; Snickerdoodle is the framework, and Mycroft, Madison, the-reallocation-engine are domains on it.
- Tool shims are generated, never hand-edited (rebuild via `node scripts/build-instructions.mjs --promote`).
- Portable layer is a thin index over the existing system — no content moved.

## Next 1–3 actions
1. Archive (not delete) the placeholder `chapters/NN-chapter-NN.md` files now that named chapters exist.
2. Promote/verify finance recipes past DRAFT with logged runs.
3. Run the `eval/` suite for real (full vs baseline) on the primary tool, then act on the scorecard.

## Files that matter (and only these)
- canonical: `SNICKERDOODLE.md`, `DOMAIN.md`, `AGENTS.md`, `status.md`, `logs/RUN_LOG.md`
- touch next: `instructions/mycroft.md` (then rebuild), `chapters/`

## Do NOT
- Edit `AGENTS.md`/`CLAUDE.md`/tool shims by hand (generated — edit `instructions/`, then rebuild).
- Load `scripts/|docs/|data/mycroft-main/` as source (quarantined Tier 3).
- Commit `data/private/` or `.env`.

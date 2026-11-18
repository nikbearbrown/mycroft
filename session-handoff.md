# Session Handoff — Mycroft

> Portable resume point for the next session/agent. Read this + `status.md` to
> continue without replaying the full conversation. Decisions and next actions in;
> narrative and raw tool output out. Full history: `logs/RUN_LOG.md`.

## Goal (one line)
Keep Mycroft (the book + finance-recipe system) current, and make the map match the repo.

## State now — 2026-11-13
- **Done:** Every recipe carries lifecycle frontmatter, so a status claim can be contradicted by evidence. `snickerdoodle` CLI (`run`/`gate`/`check`/`list`) is built and `check --all` is down to 5 defects, all in `recipes/gru.md`. The recipe Flags column was reconciled with what the step scripts implement — it gates `run`'s flag passthrough, so the mismatch was a crash, not a documentation nit. `_MANIFEST.md` and `.ai/manifest.yaml` now classify all 51 top-level paths, including the 10 contributor subsystems (1,005 tracked files) the map had never mentioned.
- **In progress:** Reviewing those subsystems. They are classified and marked `unreviewed`; none has been checked against `SNICKERDOODLE.md`, and none is inside the conformance default surface.
- **Blocked:** nothing.

## Key decisions
- `SNICKERDOODLE.md` is the constitution and governs; Snickerdoodle is the framework, and Mycroft, Madison, the-reallocation-engine are domains on it.
- Tool shims are generated, never hand-edited (rebuild via `node scripts/build-instructions.mjs --promote`).
- Portable layer is a thin index over the existing system — no content moved.
- Classifying a subsystem is not reviewing it. `unreviewed: true` is recorded deliberately so the open question stays visible instead of being silently resolved by listing it.
- Nothing belonging to another contributor is moved, renamed or edited. The map grows to fit the repo; the repo is not rearranged to fit the map.

## Next actions
1. **Promote `scenariostresstestingagent`** — 6/6 scripts built, 0 todos open, audits present for both fixture sets, and the frontmatter still reads `DRAFT`. This is a human gate, not an edit.
2. **Fix conformance's multi-document YAML handling** — `yaml.safe_load` reads one document, so three valid Kubernetes manifests under `projects/finance-event-signals/deploy/k8s/` fail. `safe_load_all` is the fix. The defect is in our checker.
3. **Decide what `multi-agents/` is.** It implements this book's central claim — a human answer key frozen and hashed before AI code generation, two independent checkers, a human approving — and nothing in the repo references it. Live work, finished artifact, or demonstration to cite from the manuscript?
4. **Run the `eval/` suite for real** — carried forward from the 2026-06-15 handoff and still open. Both runs under `eval/runs/` are named `__example`, so the §19 scorecard has never been produced from a real full-vs-baseline comparison (`npm run eval:score` / `eval:report`).

## Files that matter (and only these)
- canonical: `SNICKERDOODLE.md`, `DOMAIN.md`, `AGENTS.md`, `status.md`, `logs/RUN_LOG.md`
- the map: `_MANIFEST.md`, `.ai/manifest.yaml`
- touch next: `scripts/conformance.mjs` (YAML fix), `recipes/scenariostresstestingagent.md` (promotion)

## Do NOT
- Edit `AGENTS.md`/`CLAUDE.md`/tool shims by hand (generated — edit `instructions/`, then rebuild).
- Load `scripts/|docs/|data/mycroft-main/` as source (quarantined Tier 3).
- Commit `data/private/` or `.env`.
- Move, rename or rewrite another contributor's subsystem. Add to it or document it; do not rearrange it.

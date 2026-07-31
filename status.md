---
project: mycroft
status: active
updated: 2026-07-31
canonical: [SNICKERDOODLE.md, DOMAIN.md, AGENTS.md, outline.md, book.md, chapters/]
next:
  - "Have a named finance reviewer complete the Finance Investigator's open run-bound review request"
  - "Promote/verify finance recipes past DRAFT with logged runs"
  - "Editorial pass: expand the named finance chapters beyond first-pass drafts"
blocked_by: null
---

# Status — Mycroft

_Read this first for current state._ `DOMAIN.md` = what the repo **is**; `logs/RUN_LOG.md` = the full **history**; this file = **where we are now and what's next**.

## Where things stand
- **Framework:** Snickerdoodle (`SNICKERDOODLE.md`) is the agent-operating-system framework; Mycroft (this book + recipe system), Madison, and the-reallocation-engine are domains built on it (shared governance + `instructions/_shared/` library).
- **Manuscript:** `TIKTOC.md` rewritten as a finance recipe-engine architecture; named chapters `chapters/01`–`16` + `97` written to mirror the reallocation-engine pattern. Older `chapters/NN-chapter-NN.md` placeholders still present (cleanup pending).
- **Operating surface:** 100 recipes + 49 `conductor/` step files; two-layer `data/raw` → `data/verified`.
- **Applied projects:** AI Vendor Intelligence exercises, upstream case-study projects, and the DRAFT Mycroft Finance Investigator, which now runs locally from synthetic raw data through validation, deterministic EBITDA analysis, conditional tool selection, separate machine/human outputs, and a run-bound human review gate.
- **Context architecture:** `AGENTS.md`/`CLAUDE.md` compile from `instructions/`; portable layer (`_MANIFEST.md`, `.ai/manifest.yaml`, `PROJECT_RULES.md`, this file) + CLI-agnostic tool shims now in place; `.claude/` hooks + CI verify.
- **Enforcement:** `npm run verify` = conformance + manifest-check (adapter drift + canonical existence). `eval/` provides the §19 measurement harness.

## Open questions / decisions pending
- **Placeholder chapters** — archive `chapters/01-chapter-01.md` … `12-chapter-12.md` now that named chapters exist? (no-delete → archive, don't delete).
- **Recipe lifecycle** — confirm which finance recipes are ready to promote past DRAFT with a logged, attested run.

## Recently done (2026-07-31)
- Added the Finance Investigator's named-human review workflow: open request,
  exact-run hash binding, evidence validation, agent self-approval prevention,
  and append-only decision recording. The sample gate remains open.

## Previously done (2026-07-26)
- Implemented Weeks 1–3 of the Mycroft Finance Investigator: synthetic data contract and validation, deterministic account/category/EBITDA variance engine, evidence lineage, tests, and a single local observe-plan-act investigator.
- Completed the synthetic sample run with separate machine log and human report. Structural conformance passes; materiality, causal explanation, and distribution remain open human gates.

## Previously done (2026-06-15)
- Brought the repo up to the CLI-agnostic standard: portable read-first layer, generated tool shims (Gemini/Aider/Copilot/Cursor) from one source, `manifest-check` wired into verify + CI, and the §19 eval harness. Fixed the `.claude/hooks` "Madison" naming drift → "Mycroft".

_Update this file at the end of each working session: state, decisions, next actions. Keep it short — it's the current-state file, not a log._

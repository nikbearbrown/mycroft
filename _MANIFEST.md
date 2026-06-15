# _MANIFEST.md — read this first

> Portable read-first map for any agent, CLI, or human. A thin **index over the
> existing system**, not a second source of truth. If it conflicts with what you
> find on disk, trust the canonical file and flag the discrepancy in
> `logs/RUN_LOG.md`.
>
> **Governance:** `SNICKERDOODLE.md` is the constitution and governs all conflicts.
> `DOMAIN.md` is this repo's map. `AGENTS.md` (generated) is the cross-agent
> operating contract. This manifest just tells you *what to read and what to ignore*.

## Tier 1 — Canonical (read first)

| File | Purpose |
|------|---------|
| `SNICKERDOODLE.md` | Constitution: principles, verification stack, recipe lifecycle, gates, logging. Governs all conflicts. |
| `DOMAIN.md` | Repo map — layout, what is runnable today, the relationship to Madison. |
| `AGENTS.md` | Generated cross-agent instructions (built from `instructions/`). |
| `PROJECT_RULES.md` | Thin precedence/compatibility pointer to the files above. |
| `DATA_CONTRACT.md` | What data exists, where it lives, the raw→verified rule. |
| `status.md` | Current state, latest decisions, next actions (where we are *now*). |
| `logs/RUN_LOG.md` | Ground-truth run history (what actually happened). |

## Tier 2 — Task-relevant (load only when the task needs it)

| Path | Use when |
|------|----------|
| `recipes/` | The operating surface — 99 recipes (monitor/pipeline + agent recipes). |
| `conductor/` | Per-recipe conductor step files — the orchestration layer. |
| `scripts/` | Executable code (conformance, build-instructions, to-markdown, manifest-check, svg-to-png, ingest/, gigo/, tools/). |
| `chapters/` | Manuscript — the Mycroft book. |
| `data/raw/`, `data/verified/` | Two-layer data; nothing enters `verified/` unvalidated. |
| `pantry/` | Raw provenance inputs the recipes were derived from. |
| `reports/` | Report templates the recipes emit. |
| `docs/` | Durable human docs. Design reference (not governing): `docs/cli-agnostic-ai-tooling-grade.md`. |
| `instructions/` | Source for the generated `AGENTS.md`/`CLAUDE.md` — edit here, then rebuild. |
| `eval/` | §19 measurement harness — does the instruction scaffolding actually help? (`npm run eval:score` / `eval:report`). |
| `session-handoff.md` | Resume point when continuing a prior session. |

## Tier 3 — Generated / quarantined / private (ignore unless explicitly requested)

| Path | Rule |
|------|------|
| `output/` | Generated deliverables; **not** a source of truth. |
| `node_modules/` | Dependencies; never read broadly. |
| `instructions/.build/`, `**/__pycache__/`, `*.pyc`, `*.bak` | Rebuildable; the only safe `rm` targets (see `instructions/_shared/no-delete.md`). |
| `data/private/` | **Private by default** — never commit; read only when the task requires it. |
| `scripts/mycroft-main/`, `docs/mycroft-main/`, `data/mycroft-main/` | **Quarantined Tier 3** (vendored upstream import) — provenance only; do not load or treat as source. |

## Maintenance

- Machine-readable twin: `.ai/manifest.yaml` (keep in sync with this file).
- Update this manifest when Tier 1 files or top-level structure change.
- `_Last updated: 2026-06-15._`

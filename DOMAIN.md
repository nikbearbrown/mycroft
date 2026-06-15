# DOMAIN — Mycroft

Mycroft is **both a book and an agentic Cowork system**: the manuscript explains the method; the repo gives agents and humans a verified way to operate it. This file is the index — what's here and what is runnable today. `SNICKERDOODLE.md` is the constitution (it governs); read it first.

## Layout

| Path | What it is |
|---|---|
| `SNICKERDOODLE.md` | the constitution — principles, verification stack, recipe lifecycle, logging rules (governs) |
| `recipes/` | the operating surface: 99 recipes (monitor/pipeline + agent recipes), each with lifecycle frontmatter |
| `conductor/` | per-recipe conductor step files (49) — the orchestration layer |
| `reports/` | report templates the recipes emit |
| `data/raw/`, `data/verified/` | the two-layer data architecture — nothing enters `verified/` without validation |
| `data/mycroft-main/` | **quarantined Tier 3** (vendored upstream import); provenance only, do not load |
| `pantry/` | raw provenance inputs the recipes were derived from |
| `logs/` | `RUN_LOG.md` (canonical log) + run artifacts — real run history |
| `scripts/` | executable code only — `conformance.mjs`, `to-markdown.mjs`, `build-instructions.mjs`, `svg-to-png.mjs`, plus `ingest/`, `gigo/`, `tools/`. `scripts/mycroft-main/` is quarantined Tier 3 |
| `chapters/` | the book manuscript (17 chapters + front/appendix) — no scripts or data here |
| `docs/` | durable human docs (architecture, phase-gates, workflows, recipes, data-and-provenance, labor-separation…) |
| `d3/`, `images/` | figures and authoring tools |

## Instruction files are generated (do not hand-edit)

`AGENTS.md` (the cross-tool standard) and `CLAUDE.md` (Claude Code's name; a thin `@AGENTS.md` import + a Claude-only tail) are **build artifacts**, compiled from `instructions/` by `scripts/build-instructions.mjs` (`npm run build-instructions`). Source = `instructions/_shared/*.md` (portable rule modules, the same library Madison draws from) + `instructions/mycroft.md` (identity + the `help` menu) + `instructions/manifest.yml` (which modules, in order, + the Claude-only tail). Edit the source and rebuild; never hand-edit the root files — the build overwrites them. `--promote` writes the root files; `instructions/.build/` is the gitignored staging where you review the diff first.

## Enforcement

- **Conformance** (`scripts/conformance.mjs`, `npm run verify`) — JSON/YAML/JS/MD well-formedness, the machine half of P4.
- **Hooks** (`.claude/`, Claude Code only) — `archive-guard.sh` (PreToolUse·Bash: deny `rm` of non-rebuildables — the no-delete rule) and `conformance-check.sh` (Stop: run conformance, block on failure).
- **CI** (`.github/workflows/verify.yml`) — conformance + a drift guard that rebuilds `AGENTS.md`/`CLAUDE.md` and fails if they diverge from source.

## Relationship to Madison

**Snickerdoodle** (`SNICKERDOODLE.md`) is the **framework**; Mycroft and Madison (branding & marketing intelligence) are **domains** built on it. They are sibling repos sharing the same governance (`SNICKERDOODLE.md`), the same gate stack, and the same `instructions/_shared/` rule-module library — each selecting the subset it needs via its own `instructions/manifest.yml`, so neither carries the other's bloat.

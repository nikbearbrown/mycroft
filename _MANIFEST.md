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
| `pantry/` | Raw provenance inputs the recipes were derived from. **Local-only since `8d50977`** (2026-11): untracked and gitignored, so a fresh clone has none of it. |
| `reports/` | Report templates the recipes emit. |
| `docs/` | Durable human docs. Design reference (not governing): `docs/cli-agnostic-ai-tooling-grade.md`. |
| `instructions/` | Source for the generated `AGENTS.md`/`CLAUDE.md` — edit here, then rebuild. |
| `eval/` | §19 measurement harness — does the instruction scaffolding actually help? (`npm run eval:score` / `eval:report`). |
| `session-handoff.md` | Resume point when continuing a prior session. |

## Tier 2 — Contributor subsystems (classified here, not yet reviewed)

Self-contained work by named contributors. Each is tracked and on disk, but **none was named
by any Tier 1 file**, so an agent following this map would never have loaded it — 1,005
tracked files the map did not mention. Listing them is what makes the map match the repo.
`unreviewed` means nobody has checked the subsystem against `SNICKERDOODLE.md`; it does not
mean the work is suspect.

| Path | Tracked | What it is | Conformance | In `npm run verify` |
|------|---------|------------|-------------|---------------------|
| `verification-layer/` | 154 | Verification subsystem with its own scoped `CLAUDE.md`. Network-free, model-free test suite: `python -m unittest discover -s tests -t .` from inside the directory. | 107 files, all conform | yes |
| `projects/` | 435 | Per-project working trees (ECIS, Patents-Intelligence-Engine, finance-event-signals). | 372 files, all conform | yes |
| `case-study-workflows/` | 277 | Runnable workflow implementations, paired with the narratives in `case-studies/`. | 265 files, all conform | yes |
| `multi-agents/` | 41 | Policy-as-code verification harness: a human answer key is frozen and hashed *before* AI code generation, then two independent checkers compare the generated code against it and a human approves. Ships `DESIGN_DECISIONS.md` and `LIMITATIONS.md`. | 28 files, all conform | yes |
| `congressional-signals/` | 39 | Congressional trading-signal pipeline with its own `data/verified/`. | 1 file fails — see below | **no** — would fail every run |
| `provenance-gatekeeper/` | 17 | FastAPI gatekeeper service. The only subsystem with its own CI job (`.github/workflows/ci.yml`). | 14 files, all conform | yes |
| `case-studies/` | 14 | Case-study narratives; the prose half of `case-study-workflows/`. | 14 files, all conform | yes |
| `archive/` | 12 | Superseded material, kept under the never-delete rule. | 12 files, all conform | **no** — kept so it stops changing |
| `my_chapters/` | 10 | Contributor manuscript workspace (backlog, theses, evidence) with its own scoped `CLAUDE.md`. | 10 files, all conform | yes |
| `github-assistant/` | 6 | GitHub assistant utility. | 4 files, all conform | yes |

### Scoped `CLAUDE.md` files outside the generated set

`scripts/manifest-check.mjs` verifies that the **root** adapters match `instructions/`. Eight
other `CLAUDE.md` files exist below the root — in `verification-layer/`, `my_chapters/`, five
chapter folders under `projects/Patents-Intelligence-Engine/`, and one under `data/raw/`.
They are not generated, not checked, and not reviewed. `verification-layer/CLAUDE.md` is a
good example of the kind: it defers to `SNICKERDOODLE.md` explicitly and adds subsystem rules
rather than overriding anything. They are recorded here so they stop being invisible.

### Conformance failures

- **Open:** `congressional-signals/data/verified/conformance_report.json` contains bare `NaN`
  literals. Python's `json.dump` emits them by default; they are not valid JSON, so
  `JSON.parse` rejects the file. A real defect, owned by that subsystem's producing script.
  This is the only reason `congressional-signals/` is outside `npm run verify`.
- **Resolved 2026-11-18 — the defect was ours:**
  `projects/finance-event-signals/deploy/k8s/{infra,observability,pipeline}.yaml` are
  multi-document YAML, standard for Kubernetes manifests, and always valid. The checker
  rejected them for two compounding reasons: it called `yaml.safe_load`, which reads one
  document; and its batch runner had never executed — it built a shell string that turned
  every newline into a literal backslash-n, Python raised SyntaxError, and every YAML file
  silently fell back to a per-file check. The batch now passes its script to Python with no
  shell and uses `safe_load_all`. None of the three files was changed.

### The default conformance surface

Until 2026-11-18 `npm run verify` read none of the subsystems above. Eight are now in
`DEFAULT_PATHS`, which took the checked surface from 1,039 files to 1,853. The two left out
are named in the table, with the reason, and in a comment beside `DEFAULT_PATHS` itself.

## Loose files at the repository root

Tracked, unclassified until now, and left exactly where they are.

| File | What it is |
|------|------------|
| `answers.json`, `answers1.json` | Working answer-key templates for `scripts/gateway/bench/label.py` (`--template` in, `--from` back). They sit at the root because that is the working directory the tool's usage text assumes. |
| `enrichment-log.md` | One-off record of the 2026-06-15 chapters enrichment pass. |
| `_mvtest2` | Empty (0 bytes) since 2026-06-15; nothing reads it. Retained under the never-delete rule. |
| `LICENSE.md`, `.gitattributes`, `metadata.yaml` | Repository housekeeping. |
| `TIKTOC.md`, `book.md`, `outline.md` | Manuscript scaffolding for `chapters/`. |

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

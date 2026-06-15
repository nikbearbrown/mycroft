# CLI-Agnostic AI Tooling — Repo Grade

**Repository:** `mycroft` (a book + recipe system on the Snickerdoodle framework)
**Graded against:** *CLI-Agnostic AI Tooling for Local Project Workflows* — v1.0 (June 2026)
**Grade date:** 2026-06-15
**Basis:** repo inspection + the local `conformance` / `manifest-check` / `eval` gates.

## Overall: **A (≈ 94 / 100)**

Mycroft is a book + recipe system on the Snickerdoodle framework, alongside Madison
and the-reallocation-engine, and it now matches the-reallocation-engine's standard. It implements the guide's
strongest recommendations: compile-level instruction generation (§6 level 3), the
PreToolUse no-delete hook (§11), the manifest + machine-readable twin (§4), and an
enforced, drift-proof adapter set. `SNICKERDOODLE.md` is a full constitution, stronger
than the generic `PROJECT_RULES.md` the guide assumes.

## Section scorecard

| § | Area | Grade | Evidence / gap |
|---|------|-------|----------------|
| 3 | Directory architecture | A− | Clean canonical/transient split; `data/raw`→`data/verified`, `pantry/`, `conductor/`, quarantined `*/mycroft-main/`. Uses `output/` singular — documented in `_MANIFEST.md`. |
| 4 | Manifest pattern | A | `_MANIFEST.md` (tiered) + `.ai/manifest.yaml` twin with `invariants`, `private`, `quarantine`, `permissions`. |
| 5 | Project rules & precedence | **A+** | `SNICKERDOODLE.md` constitution + `PROJECT_RULES.md` shim + explicit precedence. |
| 6 | One folder, many surfaces | **A+** | Compile level: `instructions/` → `AGENTS.md`, `CLAUDE.md`, `.gemini/settings.json`, `.aider.conf.yml`, `.github/copilot-instructions.md`, `.cursor/rules/mycroft.mdc`, all generated, with a CI drift check. |
| 7 | Ignore files / Tier-3 | A− | `.gitignore` covers generated, private (`data/private/`), and quarantined `*/mycroft-main/`. No per-tool ignore files (low priority — shims are pointers). |
| 8 | Token optimization | A | Tiny `CLAUDE.md` (`@import`); concise generated files; modular instructions. |
| 9 | Session hygiene & state | A | `status.md` (frontmatter+prose) and `session-handoff.md` present and accurate. |
| 10 | Agent patterns | A | Gates, `subagent-scoping.md`, conformance/adequacy split. |
| 11 | File safety | **A+** | `no-delete.md` + `.claude/hooks/archive-guard.sh` PreToolUse deny; git checkpoints. |
| 12 | Governance & security | B+ | `permissions` block, private + quarantine policy, `logs/RUN_LOG.md` audit. Network allowlist documented not enforced; no dedicated pre-commit secret scan. |
| 13 | Templates & skills | A− | Shared instruction modules + recipes; size discipline. |
| 14 | Tool comparison / portability | A | Portable filesystem layer + generated adapters for the matrix tools. |
| 15 | Claude-specific mechanisms | A | Hooks, `@import`. |
| 16 | Building CLI tools | A− | Scripts use flags/exit codes/stdout-stderr (`--promote`, `--strict`, `--validate`). |
| 17 | Anti-patterns | A | Avoids all listed; quarantine keeps the vendored import from misleading agents. |
| 18 | Failure-mode catalog | A | `manifest-check.mjs` enforces drift / missing canonical / contradictions. |
| 19 | Does it help? / measurement | **B** | `eval/` harness built: 5-task suite, config matrix, deterministic scorer (`eval:score`) + aggregator (`eval:report`). Proven on example runs (`full` beats `baseline`). Remaining for A: real cross-tool runs (agent execution is manual). |
| 20 | Build order | A | Followed. |
| 21 | Data / large files | B+ | `DATA_CONTRACT.md` + two-layer raw→verified + quarantine; `.gitignore` covers heavy/private. No dedicated size-guard hook yet (reallocation-engine has one — portable to add). |

## What's excellent

- **Framework discipline.** The same `instructions/_shared/` library feeds Mycroft, Madison, and the-reallocation-engine, vendored per-repo so they can diverge without coupling — and now all three compile the same CLI-agnostic adapter set.
- **Enforcement, not just advice.** No-delete is a hook; adapter drift fails `verify` and CI; the quarantine of `*/mycroft-main/` is stated in every layer (manifest, instructions, gitignore).

## To reach A+ (ranked)

1. **Run the `eval/` suite for real** (`full` vs `baseline` on your primary tool), then prune rules that don't earn their tokens (§19).
2. **Enforce governance** — a pre-commit secret scan and a real network allowlist guard (§12).
3. **Add a size-guard** `.githooks/pre-commit` (port from the-reallocation-engine) for §21 parity.

## Bottom line

The hard parts — portable compiled instructions, deterministic safety enforcement,
a maintained manifest, a measurement harness — are **done and verified** (`npm run
verify` is green: conformance + manifest-check, zero warnings). Mycroft is now a
reference implementation alongside the-reallocation-engine; the only real headroom
is executing the §19 benchmark for real.

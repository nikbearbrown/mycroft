# PROJECT_RULES.md

> Portable compatibility pointer. This repository's rules are **not** duplicated
> here — they live in the constitution and the domain map. This file exists so any
> tool or maintainer expecting the conventional `PROJECT_RULES.md` lands on the
> right source of truth.

## Precedence

`SNICKERDOODLE.md` governs. If anything in this repository conflicts with it,
`SNICKERDOODLE.md` wins and the conflict is a bug — log it in `logs/RUN_LOG.md`.
Explicit instructions from the human in chat override generated defaults.

## Where the real rules live

| Read | For |
|------|-----|
| `SNICKERDOODLE.md` | The constitution — principles, verification stack, recipe lifecycle, gates, logging. **Governs.** |
| `DOMAIN.md` | Repo layout, the runnable surface, the relationship to Madison. |
| `AGENTS.md` | Generated cross-agent operating instructions (built from `instructions/`). |
| `_MANIFEST.md` | What to read first and what to ignore (portable map). |
| `DATA_CONTRACT.md` | What data exists, where it lives, the raw→verified rule. |
| `logs/RUN_LOG.md` | Ground-truth run history. |
| `status.md` | Current state and next actions. |

## The rules in one breath (SNICKERDOODLE.md governs in full)

1. Verified local data before external lookup; nothing enters `data/verified/` unvalidated.
2. Never invent a count, rate, or confidence; label model judgments as judgments.
3. Gates are hard stops cleared by a named human and logged.
4. Machines verify conformance; humans verify adequacy.
5. Never delete source, data, recipes, or logs — archive instead.
6. `data/private/` is private; `scripts/|docs/|data/mycroft-main/` are quarantined Tier 3 — do not load as source.
7. `AGENTS.md`/`CLAUDE.md` and the tool shims are generated — edit `instructions/`, then rebuild (`node scripts/build-instructions.mjs`).

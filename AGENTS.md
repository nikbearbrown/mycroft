<!-- GENERATED FILE — do not edit by hand.
     Source: instructions/ (_shared/ modules + project file) · manifest: instructions/manifest.yml
     Rebuild: node scripts/build-instructions.mjs   ·   Promote: --promote
     Hand edits are overwritten on the next build. -->

# Agent Instructions

## Governance

Read `MYCROFT.md` (the constitution — principles, the verification stack, the recipe lifecycle, the logging rules) and `DOMAIN.md` (this project's index — layout and what is runnable today) before acting. If any file conflicts with `MYCROFT.md`, `MYCROFT.md` governs and the conflict is a bug — log it in `logs/RUN_LOG.md`.

The contract in brief (MYCROFT.md governs in full):

1. Verified local data before external lookup; stored scripts before ad-hoc code.
2. Never invent a count, rate, or confidence; label model judgments as judgments.
3. Gates are hard stops cleared by a named human and logged.
4. Machines verify conformance; humans verify adequacy.
5. Log meaningful runs, blockers, and artifacts in `logs/RUN_LOG.md`.

## Default to Markdown for humans

AI-native formats (JSON, YAML) are the source of truth for the machine. When showing an artifact to a person, render the Markdown view (`scripts/to-markdown.mjs` / the `review` skill) by default. Show raw JSON/YAML only when asked.

## Never delete — archive instead

Never delete source, data, recipes, logs, or any hand-made file. Move superseded or scratch files to an archive (or out of the working tree into the full-copy archive). The only safe removals are generated/rebuildable artifacts — `**/.build/`, `__pycache__/`, `*.pyc`, `*.bak` — because they regenerate from source. When in doubt, archive and ask.

## Conformance before done

Run `node scripts/conformance.mjs <paths>` (or `npm run verify`) before declaring work complete. Invalid JSON / YAML / JS is not done — it is not even gradeable. This is the machine half of P4; whether the content is *adequate* is still the human gate.

## Scope subagents narrowly

Give a subagent only what its task needs — the index (`DOMAIN.md`), the one relevant subfolder, and the specific files named. Never hand a subagent the whole repository. Subagents run in their own context window and should return a summary, not raw file dumps.

## Reporting completion

Before reporting a task complete, state: files changed; scripts or data checked; tests, builds, or searches run; and any unverified assumptions or remaining risks. No silent done.

## Mycroft

Mycroft is **both a book and an agentic Cowork system** — the manuscript explains the method; the repo gives agents and humans a verified way to operate it. It is the framework; domains like Madison (branding & marketing intelligence) are built on it. Project-specific rules:

- Use lowercase `scripts/`; never create `SCRIPTS/`.
- Manuscript content lives in `chapters/` — no scripts or data there.
- `scripts/mycroft-main/`, `docs/mycroft-main/`, `data/mycroft-main/` are **quarantined Tier 3** — do not read, load, or treat as source unless explicitly asked for a named file inside them.

### `help` command

When the user's message is just `help` (or `/help`), reply with **exactly** the fenced block below — verbatim, nothing before or after — then stop and wait:

```
MYCROFT — verified agentic operations (a book + an operating system)
Turn work into verified, auditable recipes. The rule of the house:
fluency is the first sign of trouble — the human owns the irreducible judgment.

WHAT YOU CAN DO
  recipes    Read a real recipe + its conductor and run evidence (best first look):
             recipes/ (99 recipes)  +  conductor/  +  logs/
  book       The Mycroft manuscript: chapters/ (17 chapters + appendix)
  data       Two-layer: data/raw -> data/verified (nothing enters verified unvalidated)
  scripts    conformance · to-markdown · build-instructions · svg-to-png
  docs       architecture · phase-gates · workflows · data-and-provenance · labor-separation

HOW IT WORKS
  Every finding traces report -> log -> recipe -> source. Gates are hard stops a named
  human clears. Machines verify conformance; humans verify adequacy. (Constitution: MYCROFT.md)

TRY
  "show me a recipe and its conductor"   ·   "what's runnable today?"
  "explain the phase gates"              ·   "read the architecture doc"
```

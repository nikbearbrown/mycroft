# Mycroft

**Author:** Nik Bear Brown

## Overview

This repository is both a book and an agentic Cowork system. The book explains
the ideas. The repo gives agents and humans a verified way to operate them.

## Repository Structure

- `README.md` - human-facing overview.
- `CLAUDE.md` - Claude/Cowork operating rules.
- `AGENTS.md` - cross-agent operating rules.
- `docs/` - human-readable system documentation.
- `data/` - verified local data, exports, metadata, and audits.
- `scripts/` - tested, vetted, reusable automation.
- `recipes/` - agent-readable recipes with human-readable summaries.
- `chapters/` - book manuscript.
- `slides/` - optional decks and teaching material.
- `pantry/` - research notes and source material.
- `output/` - generated artifacts, not source of truth.

Use lowercase `scripts/`. Do not create `SCRIPTS/`.

## Operating Rule

Run the script and read the audit before you prompt. If the script does not
exist, say so before inventing one.

## Human Docs

- `docs/README.md`
- `docs/repo-structure.md`
- `docs/recipes.md`
- `docs/phase-gates.md`
- `docs/operations.md`
- `docs/data-and-provenance.md`
- `docs/workflows.md`
- `docs/manuscript.md`
- `docs/contributing.md`

## Book Map

| # | Chapter | Purpose |
|---|---|---|
| 00 | `chapters/00-introduction.md` | Introduces the book and repo. |
| 98 | `chapters/98-appendix-best-practices.md` | Best practices for agentic operation. |
| 99 | `chapters/99-back-matter.md` | Back matter. |

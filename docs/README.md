# Mycroft Documentation

This directory is the human-facing documentation hub for the Mycroft book and
agentic Cowork repository.

Mycroft has two connected products:

- a manuscript about using agentic systems to study AI-powered investing;
- an operational repository of imported workflows, recipes, scripts, data, and
  review gates that make the book's ideas inspectable.

Use this documentation when changing structure, running workflows, adding data,
promoting scripts, revising recipes, or reviewing generated artifacts.

## Start Here

- `repo-structure.md` explains where files belong.
- `operations.md` explains how to work in the repo safely.
- `phase-gates.md` defines the gates that must pass before automation expands.
- `data-and-provenance.md` explains source data, generated data, and evidence
  rules.
- `workflows.md` summarizes the imported n8n workflow system and generated
  recipes.
- `recipes.md` defines the required shape of agent-facing recipes.
- `manuscript.md` explains how book files relate to operational material.
- `contributing.md` gives the review checklist for humans and agents.

## Operating Model

The repo follows a simple chain of trust:

1. Read the local docs and instructions.
2. Check verified local data.
3. Prefer vetted stored scripts.
4. Run a small test before scaling.
5. Verify the output.
6. Record meaningful runs.

Do not use chat history as the only source of truth for durable decisions.
Write decisions, runs, and unresolved risks into repo files.

## Key Files

- `README.md`: public overview.
- `AGENTS.md`: cross-agent operating rules.
- `CLAUDE.md`: Claude/Cowork-specific rules.
- `DATA_CONTRACT.md`: compact data rules.
- `logs/RUN_LOG.md`: log for meaningful agent and workflow runs.
- `docs/mycroft-main/MOVED-FROM-PANTRY.md`: import summary and provenance for
  the Mycroft-main source material.

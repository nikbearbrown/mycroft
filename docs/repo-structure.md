# Repository Structure

This repo is organized by function and audience.

## Root Files

- `README.md`: human-facing overview and map.
- `AGENTS.md`: cross-agent operating rules.
- `CLAUDE.md`: Claude/Cowork-specific rules.
- `DATA_CONTRACT.md`: compact data rules.
- `package.json`: Node package metadata and script entry points.
- `metadata.yaml`: book metadata.
- `book.md`: high-level book positioning.
- `outline.md`: manuscript outline.

## Human-Facing Documentation

- `docs/`: durable human-facing documentation.
- `docs/README.md`: documentation index.
- `docs/mycroft-main/`: import notes and explanatory material from the
  Mycroft-main source bundle.

## Manuscript

- `chapters/`: book manuscript files.
- `chapters/00-frontmatter.md`: front matter.
- `chapters/00-introduction.md`: introduction.
- `chapters/01-chapter-01.md` through `chapters/12-chapter-12.md`: main
  chapters.
- `chapters/98-appendix-best-practices.md`: operational appendix.
- `chapters/99-back-matter.md`: back matter.

## Agent-Facing Recipes

- `recipes/`: agent-readable recipes with human-readable summaries.
- `recipes/README.md`: recipe index.
- `logs/RUN_LOG.md`: log of meaningful agent and workflow runs.
- `recipes/n8n-*.md`: generated cards for imported n8n workflows.

## Automation

- `scripts/`: tested, vetted, reusable automation.
- `scripts/README.md`: script rules.
- `scripts/svg-to-png.mjs`: SVG rendering utility.
- `scripts/mycroft-main/`: curated source/configuration from the Mycroft-main
  import.

## Evidence

- `data/`: verified local data, exports, source workflow JSON, assets, and
  approved reference material.
- `data/mycroft-main/`: organized import from the Mycroft-main source bundle.
- generated audits and reports: evidence of runs, not automatically source of
  truth.

Use lowercase `scripts/` only.

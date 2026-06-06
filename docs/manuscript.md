# Manuscript

The manuscript explains the ideas behind Mycroft. The repository demonstrates
how those ideas can be inspected through data, workflows, scripts, and recipes.

## Manuscript Files

- `book.md`: high-level book positioning.
- `outline.md`: chapter map and back matter plan.
- `chapters/00-frontmatter.md`: front matter.
- `chapters/00-introduction.md`: introduction.
- `chapters/01-chapter-01.md` through `chapters/12-chapter-12.md`: main
  chapters.
- `chapters/98-appendix-best-practices.md`: operational appendix.
- `chapters/99-back-matter.md`: back matter.

## Relationship to the Repo

Chapters should explain concepts in reader-facing prose. Operational details
belong in docs, recipes, scripts, data contracts, and run logs.

Use this split:

- Conceptual argument: chapter.
- How to operate the repo: `docs/`.
- How an agent should execute a repeatable workflow: `recipes/`.
- Reusable automation: `scripts/`.
- Evidence and imported source material: `data/`.
- What actually happened during a run: `logs/RUN_LOG.md` or a generated
  audit/report.

## Claim Discipline

For claims about agents, finance, markets, data quality, or performance:

- cite local evidence when available;
- name uncertainty;
- avoid implying investment advice;
- distinguish experimental design from proven result;
- preserve limitations in the prose.

If a chapter depends on a workflow, reference the workflow family or recipe
rather than duplicating operational instructions in the chapter.

## Revision Checklist

Before revising manuscript material, check:

- Does the change preserve the educational/experimental framing?
- Are repo paths still accurate?
- Are data-backed claims traceable?
- Are risks and limitations visible?
- Does the prose avoid overclaiming what the agents can do?
- Should a related doc, recipe, or data contract also change?

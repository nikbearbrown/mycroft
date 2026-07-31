# Recipes

Recipes are human-readable specifications for repeatable work: they describe the inputs a flow accepts, the steps it follows, the output contract it must satisfy, and the phase gates that must pass before the work proceeds. They are written for both humans and the conductor, so every recipe should make its assumptions, stop conditions, and review requirements explicit.

Every recipe has a corresponding implementation in `scripts/`. Scripts are also callable as tools by the conductor, whether the conductor is Cowork or Codex.

For the operating principle behind this separation, see [AI does AI things; humans do human things](../docs/labor-separation.md).

## Project Recipes

- [`mycroft-finance-investigator.md`](mycroft-finance-investigator.md) — DRAFT runnable sample for validated monthly performance investigation in `projects/Mycroft-Finance-Investigator/`.

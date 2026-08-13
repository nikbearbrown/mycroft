# Recipes

Recipes are human-readable specifications for repeatable work: they describe the inputs a flow accepts, the steps it follows, the output contract it must satisfy, and the phase gates that must pass before the work proceeds. They are written for both humans and the conductor, so every recipe should make its assumptions, stop conditions, and review requirements explicit.

Every recipe has a corresponding implementation in `scripts/`. Scripts are also callable as tools by the conductor, whether the conductor is Cowork or Codex.

For the operating principle behind this separation, see [AI does AI things; humans do human things](../docs/labor-separation.md).

## Project Recipes

- [`earnings-call-sentiment-analyzer.md`](earnings-call-sentiment-analyzer.md) — DRAFT integration for the full-stack FinBERT earnings-call analyzer in `projects/Earnings-Call-Sentiment-Analyzer/`.

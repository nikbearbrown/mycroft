# Data and Provenance

Mycroft treats local evidence as the first source of truth. Data files explain
what the repository can know; generated audits explain what happened to that
data.

## Source Data

Put original exports, approved reference records, imported workflow JSON, and
curated assets in `data/`.

The major imported source bundle is:

- `data/mycroft-main/`

The import summary is:

- `docs/mycroft-main/MOVED-FROM-PANTRY.md`

That summary records the original pantry import, counts of moved files, skipped
generated/dependency/cache files, and the 48 generated n8n workflow recipes.

## Generated Data

Generated reports and audits should sit near the data they inspect and should
use clear names such as:

- `*-audit.md`
- `*-report.md`
- `*-summary.md`

Generated files are evidence of a run. They are not automatically source of
truth until a human or documented workflow accepts them.

## Provenance Rules

- Check local data before external lookup.
- Never invent counts, rates, coverage, confidence, holdings, prices, or
  performance.
- Mark missing data as missing.
- Record where imported material came from.
- Preserve original workflow JSON when generating recipes or summaries.
- Do not store secrets in tracked data files.
- Do not promote generated caches, dependencies, or build outputs into source
  data unless a human intentionally curates them.

## Financial Data Caution

Mycroft is educational and experimental. Treat market, portfolio, SEC filing,
patent, sentiment, and news outputs as research artifacts, not financial advice.

Any workflow that could influence an investment decision requires:

- source provenance;
- timestamp or data date;
- limitation statement;
- human review;
- audit trail;
- clear separation between observation and recommendation.

## Data Review Checklist

Before using data in a chapter, recipe, or workflow, check:

- Is the data local and identifiable?
- Is the original source or import path documented?
- Is the data current enough for the claim being made?
- Are missing fields marked instead of inferred?
- Are generated summaries traceable to source files?
- Has any risky claim been reviewed by a human?

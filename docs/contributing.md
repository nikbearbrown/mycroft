# Contributing

Contributions can be prose, documentation, data curation, workflow review,
script improvements, or recipe refinements. The same rule applies to all of
them: make the work inspectable.

## Before You Start

Read:

1. `README.md`
2. `AGENTS.md`
3. `docs/README.md`
4. `docs/operations.md`
5. Any domain-specific doc related to the change

For workflow or data changes, also read `DATA_CONTRACT.md`.

## Contribution Types

## Documentation

- Put repo-wide human docs in `docs/`.
- Put agent recipes in `recipes/`.
- Keep operational docs short and current.
- Update indexes when adding durable docs.

## Manuscript

- Edit chapters for reader-facing explanation.
- Keep operational details in docs or recipes.
- Tie factual claims to local evidence where possible.

## Data

- Preserve provenance.
- Mark missing data honestly.
- Do not commit secrets.
- Keep generated artifacts distinct from source data.

## Scripts

- Use `scripts/`.
- Document inputs, outputs, side effects, and verification.
- Run a small test before using a script broadly.

## Recipes

- Keep recipes executable by agents and auditable by humans.
- Include required reads, phase gates, workflow, output contract, logging rule,
  and stop conditions.
- Update `recipes/README.md` when adding or removing recipes.

## Review Checklist

Before considering a change complete, verify:

- The file belongs in its current directory.
- Related indexes or READMEs are updated.
- Source data or source workflow material is named.
- Side effects are documented.
- Phase gates have been considered.
- A small-run or verification step was performed when relevant.
- Meaningful runs are logged in `logs/RUN_LOG.md`.
- Remaining risks are stated clearly.

## Financial and Advisory Boundary

Mycroft is an educational experiment. Contributions must not turn generated
analysis into personalized financial advice.

Use language that distinguishes:

- educational explanation;
- research observation;
- model or workflow output;
- human-reviewed conclusion;
- investment recommendation.

Only the first four belong in this repository without explicit human approval.

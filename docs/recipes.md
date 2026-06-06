# Recipes

Recipes are agent-facing recipes with human-readable executive summaries.

Each recipe should include:

1. Executive summary
2. Required reads
3. Phase gates
4. Primary stored scripts or a clear "not implemented yet"
5. Workflow
6. Output contract
7. Logging rule
8. Stop conditions

## Purpose

Recipes turn repeatable work into inspectable instructions. They should be
specific enough for an agent to execute and clear enough for a human to audit.

Use a recipe when a workflow:

- will be repeated;
- has multiple steps or tools;
- depends on local data;
- has meaningful side effects;
- needs phase gates or review points.

## Required Reads

Required reads should point to the minimum context needed before execution.
Common required reads include:

- `README.md`
- `AGENTS.md`
- `docs/phase-gates.md`
- `DATA_CONTRACT.md`
- relevant files in `docs/`
- source workflow JSON or local data paths

## Output Contract

The output contract should say:

- what files or messages are produced;
- what format they use;
- whether the output is provisional or reviewed;
- where the output should be stored;
- how it should be verified.

## Stop Conditions

A recipe should stop when:

- required input data is missing;
- credentials or secrets are needed;
- outputs cannot be verified;
- the workflow would make or imply investment advice without review;
- the workflow would publish, trade, delete, or commit without approval;
- the result conflicts with local evidence.

## Imported n8n Recipes

Imported n8n workflow recipes live in `recipes/n8n-*.md`. Their original source
material is recorded under `data/mycroft-main/`, and the import summary is in
`docs/mycroft-main/MOVED-FROM-PANTRY.md`.

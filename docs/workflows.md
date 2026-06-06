# Workflows

Mycroft includes imported n8n workflows converted into agent-readable recipes.
These workflows are educational artifacts for studying how specialized agents
can gather, verify, synthesize, and communicate investment intelligence.

## Source and Generated Artifacts

- Original/imported workflow material: `data/mycroft-main/`
- Original n8n workflow JSON: `data/mycroft-main/n8n-workflows/originals/`
- Generated recipe cards: `recipes/n8n-*.md`
- Import report: `docs/mycroft-main/MOVED-FROM-PANTRY.md`
- Recipe index: `recipes/README.md`

The import report records 48 n8n workflows and 48 generated recipes.

## Workflow Families

The imported workflows cover several broad families:

- research and analytics;
- news and sentiment monitoring;
- SEC filing analysis;
- patent intelligence;
- portfolio intelligence;
- risk management and stress testing;
- forecasting;
- financial literacy and advisory interfaces;
- orchestration and cross-agent synthesis;
- open-source engineering health signals;
- retail investor anxiety and behavioral analysis.

## How to Use a Workflow Recipe

1. Read the recipe card in `recipes/`.
2. Read any required local docs named by the recipe.
3. Check the source workflow JSON or imported source material when behavior is
   unclear.
4. Confirm the phase gates in `docs/phase-gates.md`.
5. Run only a small test unless the workflow has already been verified for the
   current data and environment.
6. Log meaningful runs in `logs/RUN_LOG.md`.

## Documentation Expectations

Each workflow recipe should document:

- executive summary;
- original workflow path;
- required reads;
- phase gates;
- node or tool inventory;
- input expectations;
- output contract;
- logging rule;
- stop conditions.

When a workflow changes, update both the recipe card and any human-facing docs
that describe the workflow family.

## Orchestration Rule

Do not let an orchestrator workflow hide risk. If a workflow coordinates other
agents, its docs must identify:

- what each sub-agent contributes;
- how conflicts are detected;
- how contradictions are resolved;
- when human review is required;
- what output counts as final.

## Verification Questions

Before treating workflow output as evidence, ask:

- Which input files or services were used?
- What date or timestamp does the output represent?
- Which assumptions are encoded in the workflow?
- Was the run partial, simulated, or complete?
- Can a human trace the output back to source material?
- Are observations clearly separated from recommendations?

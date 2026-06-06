# Documentation Guide

This guide defines how to write documentation for this repository. The repo
contains books, research, reusable scripts, recipes, agent instructions, and
generated artifacts, so documentation must serve two audiences at once:
humans who audit and decide, and agents that need reliable context for work.

Good documentation here is not just explanation after the fact. It is operating
context. It should make the next human reviewer faster and the next agent less
likely to improvise.

## Core Principle

Document the difference between what something is, what it can do, what it
should do, and what it already did.

- What it is: purpose, location, owner, inputs, and outputs.
- What it can do: capabilities, scripts, tools, data sources, and permissions.
- What it should do: constraints, phase gates, review rules, and stop
  conditions.
- What it did: logs, audits, run summaries, generated artifacts, and decisions.

Do not describe uncertain, agentic behavior as if it were deterministic. For
prompts, recipes, and agent workflows, document intended behavioral envelopes:
acceptable actions, unacceptable actions, fallback paths, and human escalation
points.

## Where Documentation Belongs

Use the narrowest location that matches the audience.

- Root `README.md`: short orientation to the whole workspace.
- Root `docs/`: repo-wide documentation standards and shared operating rules.
- `books/<book>/README.md`: human-facing overview for one book or book-system.
- `books/<book>/docs/`: human-readable documentation for that book's structure,
  workflows, evidence, and operations.
- `books/<book>/AGENTS.md`: concise agent-facing operating rules.
- `books/<book>/CLAUDE.md`: Claude/Cowork-specific operating rules when needed.
- `books/<book>/recipes/`: agent-readable recipes with human-readable summaries.
- `books/<book>/scripts/`: vetted reusable automation, with script docs nearby.
- `logs/`, `output/`, generated reports, and run logs: evidence of what
  happened, not primary design documentation.

For the active `mycroft` book, prefer book-specific docs under
`books/mycroft/docs/` unless the rule applies to the whole workspace.

## Required Qualities

Every durable documentation file should make clear:

- Audience: human, agent, operator, author, reviewer, or mixed.
- Scope: what the document covers and what it does not cover.
- Source of truth: the files, data, scripts, or decisions the doc relies on.
- Current workflow: the normal path a user or agent should follow.
- Failure modes: what commonly goes wrong and how to respond.
- Stop conditions: when to pause, ask for review, or avoid automation.
- Update trigger: what kind of change requires the document to be revised.

If a document cannot answer these questions, it is probably a note, not durable
documentation. Put notes in the appropriate research, pantry, or log location.

## Agent-Facing Documentation

Agent-facing documentation should be short, explicit, and operational.

Use `AGENTS.md` for cross-agent rules such as:

- grounding order;
- build and test commands;
- forbidden directories or naming conventions;
- required checks before editing, generating, or publishing;
- review gates and escalation rules.

Use recipes for repeatable recipes. A recipe should include:

1. Executive summary.
2. Required reads.
3. Phase gates.
4. Primary stored scripts, or a clear "not implemented yet."
5. Workflow.
6. Output contract.
7. Logging rule.
8. Stop conditions.

Agents execute recipes. Humans audit, supervise, and decide when to intervene.
Write agent docs accordingly.

## System Prompts, Recipes, and Behavioral Rules

Treat prompt and recipe changes like software changes. A small wording change can
alter tool use, refusals, routing, or generated output.

When documenting prompts, recipes, or agent behavior, include:

- intended behavior;
- known edge cases;
- behaviors explicitly ruled out;
- tool and data dependencies;
- evaluation or verification steps;
- change rationale when behavior is adjusted.

Avoid claiming exact outputs for non-deterministic systems. Instead, describe
acceptable output ranges, required evidence, and checks that must pass.

## Tool and Script Documentation

Tool and script docs must go beyond "how to run it." They should document
operational constraints.

For each durable script or tool workflow, include:

- purpose and expected input files;
- output files and whether they are source of truth or generated artifacts;
- side effects, including network calls, file writes, deletes, or commits;
- idempotency: whether repeated runs are safe;
- failure modes and ambiguous results;
- verification step after the run;
- logging requirement.

Prefer stored scripts over ad hoc commands when a workflow will be repeated.
If no stored script exists, say so in the documentation before inventing a new
one.

## Workflow Documentation

For multi-step workflows, document the sequence, not only the tools.

A good workflow doc includes:

- start conditions;
- required local evidence;
- step order;
- decision points where human or agent judgment is allowed;
- success criteria;
- fallback paths;
- loop prevention;
- termination criteria;
- human escalation triggers.

When a workflow has deterministic subflows and agentic decision points, keep the
deterministic steps in scripts and document the agentic decision points
separately.

## Evidence, Logs, and Audits

Runtime records are documentation too. They answer what actually happened.

Use logs and audits for:

- script runs;
- generated artifacts;
- data refreshes;
- model or prompt evaluations;
- publishing actions;
- decisions that affect book structure, evidence, or claims.

A good run log records:

- date;
- command or workflow name;
- inputs;
- outputs;
- verification result;
- unresolved issues;
- follow-up action.

Do not rely on memory or chat history as the only record of an important
operation.

## Compliance and Safety Notes

When a workflow involves regulated, financial, medical, legal, HR, educational,
or other high-impact decisions, documentation must be more conservative.

Include:

- human oversight points;
- review requirements;
- data provenance;
- limitation statements;
- audit trail location;
- rollback or correction path;
- known risks and mitigations.

For agentic systems, document what the agent is allowed to do separately from
what it is technically capable of doing.

## Writing Style

Write docs as working instructions, not essays.

- Prefer direct headings and short paragraphs.
- Use checklists for operational gates.
- Use tables only when comparison helps.
- Link to source files rather than duplicating large content.
- Keep claims tied to evidence.
- Mark unfinished docs with clear `TODO` items and owners when known.
- Remove obsolete instructions instead of layering contradictions.

Use plain language. The best repo documentation is boring in the right way:
clear, findable, and hard to misread.

## Documentation Review Checklist

Before adding or changing durable documentation, check:

- Does this belong at the root, in a book folder, in a recipe, or in a log?
- Is the audience explicit?
- Is the source of truth named?
- Are commands, paths, and outputs current?
- Are side effects and stop conditions documented?
- Are agentic behaviors described as behavioral envelopes rather than exact
  guarantees?
- Is there a verification or audit trail for important operations?
- Will a future agent know what to read before acting?
- Will a future human know when to intervene?

If the answer to either of the last two questions is no, keep revising.

# MYCROFT

**Version:** 0.1.0 · **Date:** 2026-06-11 · **Canonical home:** mycroft.biz (this is the vendored copy for this repository)

Mycroft is an agent-operating system: a contract between human judgment and AI execution, run by Claude Code, Cowork, Codex, or any agent that can read this file. It exists to teach and enforce one claim — AI made execution cheap; it did not make judgment cheap — by making people build actually useful things, iteratively and transparently.

## Precedence

If any file in this repository conflicts with MYCROFT.md, MYCROFT.md governs. The conflict is a bug — log it in `logs/RUN_LOG.md`. This file is domain-agnostic; everything specific to this repository's domain lives in `DOMAIN.md`, which you read next.

## Principles

**P1 — Labor separation.** AI executes: fetch, parse, score, transform, draft. Humans decide: scope, gate clearance, interpretation, release. Machines verify **conformance**; humans verify **adequacy**. Whether a thing is actually useful is not an AI question — it is an experiential one. A step that requires human judgment is not a bottleneck; it is the point.
*Violated when:* a pipeline proceeds past a judgment because no failure was detected.

**P2 — Verified data, structurally.** Only ingest scripts touch the network. Nothing enters the verified layer without passing validation. Tools read only verified data. Agents working conversationally: local verified data before external lookup, always.
*Violated when:* a tool fetches, or an agent answers from priors what a local record could answer.

**P3 — Provenance or it isn't evidence.** Every finding traces report → log → script → recipe → source. Never invent a count, rate, or confidence. Break one link and you have an output, not evidence.
*Violated when:* a number exists that no record produced.

**P4 — Gates are hard stops.** A phase gate requires a specific, testable handoff condition, cleared by a named human, logged with who/what/when. "Looks good" is not a handoff condition.
*Violated when:* a gate clears itself, or clears on vibes.

**P5 — Two customers, twice.** Every recipe is executable by the agent and readable by the domain human. Every run produces a log for agents and a report for humans. One artifact cannot serve both.
*Violated when:* a human can't read their own pipeline, or a stakeholder is handed a log.

**P6 — Intent lives in the recipe; truth lives in the run.** The recipe is authoritative for what should happen; the audit is authoritative for what did happen. A recipe's authority grows with its lifecycle stage (below): a DRAFT is a hypothesis; only a VERIFIED recipe carries evidence its intent is achievable. Disagreement between recipe, script, and run is a logged defect — no artifact silently wins.
*Violated when:* an agent "fixes" a mismatch without logging it.

**P7 — The margin is part of the record.** Anyone may comment on data, scripts, and recipes. Comments are addressed to a versioned artifact, attributed, append-only, and logged. Gate decisions cite relevant comments.
*Violated when:* judgment is shared verbally and lost, or a comment is edited after the fact.

**P8 — Trust is earned, not configured.** Dialogic mode is the default: a human at every gate. Silent mode is earned through documented runs and a recorded attestation, and is revoked by any change to the recipe or its scripts, any upstream schema change, or implausible output. Model judgments are always labeled as judgments.
*Violated when:* autonomy is granted by a config flag instead of a track record.

## The Verification Stack

Four layers, in order. Each layer feeds the next; none substitutes for the next.

1. **Conformance checks** — what the machine genuinely can judge: a JSON file that doesn't parse, a missing schema field, a script that exits nonzero. These **halt the run**. They never become polite reports.
2. **Audits** — scripts that count, compare, and surface: records in, records out, rejects and why, anomalies, examples. Audits are **reports for human judgment**, written beside the data they inspect as `*-audit.md`. An audit does not say pass; it says what it found.
3. **Attestation** — the human's record of having judged the audits and the running system. The record **is** the attestation; there is no verdict field (see format below). Thin testing exposes itself.
4. **VERIFIED** — the status transition is the verdict; the record is the justification.

## Recipe Lifecycle

Every recipe carries status frontmatter. The status is a claim; per P3, each transition needs a logged evidence artifact. Editing the status field without the evidence is a violation, not a promotion.

```
DRAFT ──► SPECIFIED ──► RUNNABLE-SAMPLE ──► RUNNABLE-LIVE ──► VERIFIED
```

| Transition | Gate test | Evidence |
|---|---|---|
| DRAFT → SPECIFIED | zero open `[TODO]` items; each closure has its required evidence (table below) | the closures themselves, in the recipe |
| SPECIFIED → RUNNABLE-SAMPLE | full sample run completes; conformance checks pass; audits generated and read | RUN_LOG entry + audit files |
| RUNNABLE-SAMPLE → RUNNABLE-LIVE | live run with a human clearing every gate | logged gate decisions |
| RUNNABLE-LIVE → VERIFIED | attestation recorded, bound to this recipe version | attestation record |

```yaml
---
status: DRAFT          # DRAFT | SPECIFIED | RUNNABLE-SAMPLE | RUNNABLE-LIVE | VERIFIED
todos_open: 0
last_gate: null        # e.g. "sample-run, 2026-06-14, logs/RUN_LOG.md#2026-06-14"
attestation: null      # path to attestation record, set only at VERIFIED
recipe_version: 0.1.0
---
```

## TODO Closure

A `[TODO]` without evidence of closure is still open, whatever the text says.

| TODO type | Closed by | Evidence required |
|---|---|---|
| `DATA SOURCE` | human | file exists at the named path + one-line provenance note (origin, date) |
| `DEFINE` | human | the value, in the recipe, with one sentence of reasoning |
| `DEV` | AI (via scored prompt) | script exists + conformance checks pass + handoff condition met |
| `APPROVE` | human | a logged gate decision — this is a gate, not a checkbox |
| `REPORT FIELD` | human | all three: exact columns/sections, reader role, decision enabled |

## Attestation Format

No verdict sentence. Every row pairs what was run with what was seen and what was expected. The **Did not test** section is mandatory — an empty one is the new "it works."

```markdown
## Attestation
- Recipe: <name> v<version>
- By: <name> · <date>

### Tested
| Ran | Saw | Expected |
|---|---|---|
| <command or action> | <observed result> | <expected result> |
| <at least one deliberate attempt to break it> | ... | ... |

### Did not test
- <honest list>

### Broke during testing, fixed
- <what failed, what changed, where>
```

Any edit to the recipe or its scripts after attestation voids it.

## Logging

Record in `logs/RUN_LOG.md`: every script run against real data, every audit created, every gate decision, every TODO closure batch, every blocker, every artifact change. Short and concrete: date, recipe, inputs, outputs, result, open issues. No secrets, no personal contact details, no private application notes.

## Start

1. Read `DOMAIN.md` — what this repository's domain is, what is runnable today, and your first command.
2. Trust recipe frontmatter status only as far as its evidence; when in doubt, the RUN_LOG is the ground truth.
3. When you change anything meaningful, log it.

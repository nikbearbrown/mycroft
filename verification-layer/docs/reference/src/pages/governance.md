---
title: Principles in the code
slug: governance
section: Architecture
order: 30
summary: Where each of the constitution's eight principles is enforced, and where the code still falls short of one.
---

This repository runs under `SNICKERDOODLE.md`, whose eight principles are written as rules with
a "violated when" test. This page maps each one to the code that enforces it here, and to what is
still open. The subsystem's own rules (log every change, stay self-contained, test before claiming
done, don't overclaim) are in [[CLAUDE.md]].

| Principle | In the code | Still open |
|---|---|---|
| **P1: labour separation.** AI executes; humans decide; machines verify conformance, humans verify adequacy. | The gate: every two-sided conflict waits for a named reviewer ([[validation/gate.py]]). The synthesis proposes, never decides ([[validation/divergence.py]]). Investors see only a grade a human recorded. | A proposed consensus can't be confirmed as a published grade ([synthesis-thin-and-lexical](ledger.html#synthesis-thin-and-lexical)). |
| **P2: verified data, structurally.** Only ingest code touches the network. | Data egress is confined to [[datasources/edgar.py]] and [[datasources/filings.py]]; the model and search to [[adapters/langchain_adapter.py]]; citation checks to [[validation/verification.py]]. [[tests/test_layering.py]] checks for egress outside them. | The egress check searches for two strings only (noted in [[tests/test_layering.py]]). |
| **P3: provenance or it isn't evidence.** Never invent a count, rate or confidence. | Each figure carries its concept, period and accession number ([[datasources/edgar.py]]); every attempt records its directive and inputs ([[core/schemas.py]]); evidence is counted, never scored; values outside a vocabulary are refused, not coerced ([[core/assessment.py]]); "couldn't compare" is never reported as "no contradiction" ([[validation/cross_validation.py]]). | `confidence_score` is a configured value, not computed (noted in [[core/schemas.py]]). |
| **P4: gates are hard stops.** A specific, testable handoff condition, cleared by a named human, logged. | The handoff condition is "every gated item cited by a recorded decision"; decisions need a name and a 20-character rationale and are stored append-only ([[web/db.py]]). No AI session records a decision. | The name is typed, not authenticated ([gate-identity-self-declared](ledger.html#gate-identity-self-declared)). |
| **P5: two customers, twice.** A log for agents, a report for humans. | Each run has the stored record and trace (for agents and auditors) and the review app and Markdown export (for people) ([[validation/audit.py]]). | |
| **P6: intent in the recipe, truth in the run.** Disagreement between recipe, script and run is a logged defect. | Directives are versioned and never edited in place ([[core/directive.py]]); every run stores what it was given. Disagreements found while writing these docs are logged ([Drift found while documenting](drift.html)). | The trace shows the consistency probe as a retry ([consistency-probe-shown-as-retry](ledger.html#consistency-probe-shown-as-retry)). |
| **P7: the margin is part of the record.** Comments attributed, append-only, logged. | Reviewer flags and gate decisions are separate rows; runs and decisions can't be updated or deleted ([[web/db.py]]); `logs/RUN_LOG.md` is corrected by appending ([[logs/RUN_LOG.md]]). | `DELETE /api/runs` still drops everything, unauthenticated ([audit-criticals](ledger.html#audit-criticals)). |
| **P8: trust is earned, not configured.** Model judgments labelled as judgments. | Grades, directions and assumptions are internal tier and labelled as model judgments everywhere ([[core/assessment.py]], [[web/frontend/src/components/Grades.tsx]]). A human is at every gate; there is no silent mode. | |

## The verification stack

The constitution's four layers, as they appear here:

1. **Conformance checks halt.** A reply that breaks the output contract is retried, then halted
   ([The validation loop](f-validation-loop.html)); invalid data in a decision is refused.
2. **Audits report.** The comparison rows, the checks and the synthesis say what they found and
   never say "pass" ([Cross-agent comparison](f-compare.html), [Accounting checks](f-checks.html)).
3. **Attestation.** Not yet: no attestation has been recorded for this subsystem.
4. **Verified.** Nothing here is in the VERIFIED lifecycle stage.

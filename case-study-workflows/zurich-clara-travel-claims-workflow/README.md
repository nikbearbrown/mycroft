# Zurich / Clara (AgentricAI) Travel Claims — Reference Implementation

**Status:** Built and tested. Seven modules, 28 passing tests, all asserting sequencing (via spy/mock, not just final output), following this series' standard pattern.

**Source case study:** [`case-studies/11-zurich-agentic-ai-travel-claims.md`](../../case-studies/11-zurich-agentic-ai-travel-claims.md) — Zurich / AgentricAI, Agentic AI in Travel Insurance Claims (Series: Agentic AI Adoption in Financial Services, 2025–2026). This is the thinnest-sourced entry in the series to date. This implementation corresponds to Section 4 (Illustrated Workflow) and is documented in the case study's Section 4b.

This repository is **not** a disclosure of AgentricAI's actual Clara system. See **Explicit Non-Claims** below before reading further.

---

## What This Is

Zurich's own materials confirm, in full, and no more:
- Clara is an "AI Digital Colleague" built by AgentricAI, demonstrating how agentic AI can revolutionize travel claims processing.
- Built on "an intelligent orchestration system that coordinates specialized AI agents."
- "Keeps humans in control where it matters most."
- Maintains "a transparent and auditable trail of the reasoning behind decisions."
- Won one of five spots in Zurich's 2025 Agentic AI Hyper Challenge.

That is the entire confirmed factual basis for this build. Verified against Zurich's official Hyper Challenge page and its October 17, 2025 media release. AgentricAI's UK incorporation (1 May 2025) is independently confirmed via Companies House.

Zurich discloses **no**: agent count or individual agent roles; threshold, claim type, or confidence score triggering human intervention; technical composition of the audit trail; claim volume, processing time, or accuracy figure specific to Clara; confirmation that Clara is among the "5 pilots now moving to production" Zurich mentions elsewhere (it is not individually named there).

This code does not attempt to fill in any of the above. Where Zurich's disclosure stops, this implementation stops too.

**Two sourcing risks worth naming explicitly, because they're easy to trip over even when trying to be careful:**
1. A separate, unrelated "Clara" exists from a company called Agent Workforce (Digital Workforce Services Plc), with a documented ingestion/policy/resolution architecture, named agents, and configurable confidence thresholds. It was not consulted and does not inform any design choice here.
2. A different Zurich Hyper Challenge winner — Wangari Global's Etio — is disclosed as having "11 modular AI Agents." That figure belongs to Etio, not Clara, and must not be transferred. AgentricAI's own site separately claims its product processes "each claim end-to-end in under two minutes with a high degree of accuracy" — a generic product-marketing claim, not tied to Clara or the Zurich pilot by name, and not used anywhere in this build.

---

## Architecture

A single, linear pipeline — not a multi-agent orchestration layer simulating Clara's undisclosed internal architecture:

```
Intake → Extraction → Coverage Check → Authorization Gate → Resolve/Escalate
```

Five stages, matching the case study's own framing that travel claims' added complexity (multiple documents, multiple languages, multiple sub-claims) needs Extraction separated from Intake, and Coverage Check separated from a final Authorization Gate — unlike simpler entries in this series where those could collapse into fewer stages.

**A design question surfaced during dependency mapping (/v2) that this series' DBS precedent raised but didn't force the same way here:** should Coverage Check fetch its own policy data (impure), or receive it pre-fetched by a separate Policy Lookup stage (pure, six stages)? DBS's build split lookup out specifically to keep its heaviest-logic stage pure and independently testable. This build made the opposite call, deliberately: **Coverage Check fetches its own mock policy record.** Rationale, logged as a departure from DBS's precedent: for a build this thin-sourced, the test-isolation benefit of a pure Coverage Check didn't justify a sixth module the case study's design never specified — the halt/reason granularity in the test suite already independently proves each escalation path fires correctly regardless of where the fetch happens.

**Halt map:**

| # | Condition | Owner | Reason string |
|---|---|---|---|
| 1 | Intake structurally incomplete (missing document, type tag, or language tag) | `intake.py` | — (status object, no named reason) |
| 2 | Required document type missing given claimed sub-claims (e.g., claimed medical expense with no receipt) | `intake.py` | `missing_document` |
| 3 | Extraction or translation confidence below threshold | `extraction.py` | `low_extraction_confidence` / `low_translation_confidence` |
| 4 | Cross-document contradiction (checked before policy fetch — see ordering note below) | `coverage_check.py` | `cross_document_contradiction` |
| 5 | No matching policy record | `coverage_check.py` | `no_matching_policy` |
| 6 | Sub-claim dependency unresolvable | `coverage_check.py` | `unresolvable_sub_claim_dependency` |
| 7 | Gate returns `escalated_to_human` | `authorization_gate.py` → `resolve_escalate.py` | `authorization_gate_rejection` |
| 8 | All conditions clear | — | `resolved_by_human` terminal state |

Two additional failure modes are **exceptions**, not halt conditions — misuse of the code, not a domain outcome:
- Constructing the Authorization Gate without a decision function → `TypeError`
- A supplied decision function returning anything other than `resolved_by_human` or `escalated_to_human` → `ValueError`

**Coverage Check's internal ordering is fixed, not incidental:** contradiction check → policy fetch → three coverage rules → sub-claim dependency check. This was locked during design review specifically because a claim could otherwise trigger both a contradiction and a missing-policy condition simultaneously with no defined precedence — a real gap the review process caught, not a hypothetical. Contradiction is checked first because it requires no policy data at all; a test in `test_coverage_check.py` locks this ordering by construction.

---

## Module Reference

| File | What it does | Confirmed / Constructed |
|---|---|---|
| `mock_data.py` | Fabricated policy records and claim documents only — no real Zurich or AgentricAI data anywhere. Includes fixtures for every named halt condition, plus the case study's own Kwame scenario as the canonical happy path. | CONSTRUCTED |
| `intake.py` | Validates structural completeness of a submission (documents present, each tagged with type and language) **and** document-completeness (a required document type isn't missing given what the claim itself asserts). Document-completeness ownership moved here from Extraction during design review — it is a tag-level cross-reference, not a confidence-scoring problem. | Document-type taxonomy and language-tagging schema are `[DEV]` CONSTRUCTED — Zurich/AgentricAI disclose no intake schema at all. |
| `extraction.py` | Pure function. Validates per-document extraction-confidence and, separately, translation-confidence for non-English documents. Does not fetch data itself. | Synthesis *capability* is CONFIRMED at the level Zurich states it (an orchestration system coordinating specialized agents). The requirement to track extraction and translation confidence as two distinct values is this case study's own design requirement — no source states Zurich/AgentricAI actually separates these. Specific thresholds are `[DEV]` CONSTRUCTED. |
| `coverage_check.py` | Fetches its own mock policy record (deliberately impure — see Architecture) and evaluates three interacting rules: is the cancellation reason covered, is timing within the covered window, is the dependent tour sub-claim covered given the flight cancellation's own coverage outcome. Also owns cross-document contradiction detection, checked first in a fixed internal order. | The *existence* of conditional multi-variable logic is CONSTRUCTED — this case study's own construction to demonstrate the "conditional, multi-variable policy logic" problem layer, not a Zurich disclosure. Minimum three interacting rules is a non-negotiable floor, not illustrative. |
| `authorization_gate.py` | **The deliberately-absent-default component.** Contains zero built-in approval criteria — no confidence score, no dollar threshold, no claim-type restriction. Requires an externally supplied decision function at construction or raises immediately. Strictly validates that function's return value. Ships with a demo-only decision function, explicitly not `[DEV]`-marked, for end-to-end runnability. | Absence is deliberate by design, directly grounded in Zurich's own confirmed language: "keeping humans in control where it matters most" states a category without disclosing a boundary. The demo policy is a named, logged exception with no claim to represent Clara's actual authority boundary — same treatment as this series' prior Gate demo policies. |
| `resolve_escalate.py` | Terminal stub. On resolution, marks the claim resolved. On escalation, attaches one of seven specific named reasons — never a generic flag. | CONSTRUCTED stub. Nothing is disclosed about what happens after Clara's stage. |
| `orchestrator.py` | Runs all five stages in strict sequence per the halt map. The only module with dependencies on all the others. | Mirrors Zurich's disclosed shape (orchestration coordinating specialized handling, human-control point, auditable trail) without adding steps, agent counts, or handoff protocols Zurich never described. |

---

## Naming: Why `resolved_by_human` / `escalated_to_human`, Not This Series' Usual Convention

This series has generally used `not_authorized` as its default rejected/blocked-outcome convention, with logged departures at HSBC (`not_approved`) and DBS (`cleared_for_finalization` / `not_cleared_for_finalization`).

This build departs again, deliberately. Zurich's confirmed language is "keeping humans in control where it matters most" — narrower and differently shaped than DBS's "finalizes the memo" framing, and without a natural verb the way DBS had. `resolved_by_human` / `escalated_to_human` frames the Gate's decision as a question of *who* holds control at this point, matching Zurich's own phrase, rather than importing an authorization or finalization framing this case study's confirmed record doesn't use.

---

## What the Tests Prove

28 tests, all passing. Following this series' spy/mock-assertion pattern — proving sequencing, not just final output:

- Structurally incomplete intake → extraction, coverage check, and the Gate all asserted **never called**.
- Low extraction confidence → coverage check and the Gate asserted never called.
- No matching policy record → the Gate asserted never called.
- Extraction-confidence and translation-confidence failures produce **different** escalation reasons — proving the two-score separation matters, not just that two fields exist.
- The tour sub-claim's coverage outcome actually **changes** based on the flight-cancellation sub-claim's outcome (covered vs. not covered), tested against two different claim shapes — not just described as dependent.
- A claim engineered to trigger both a contradiction and a missing-policy condition deterministically returns `cross_document_contradiction` — locking the fixed internal ordering by construction, not by accident.
- Authorization Gate contract tests only (honors whatever the supplied function returns; raises on missing function or invalid return value) — not tests of what should authorize a claim, since no disclosed rule exists to test against.
- A clean, complete case (the Kwame scenario) runs end-to-end to a `resolved` terminal state — proving the happy path works, not only the halts.
- Missing decision function still raises `TypeError` at Gate construction, even when invoked through the orchestrator's entry point. Invalid decision-function return values raise `ValueError` and are asserted to never reach `resolve()` or `escalate()`.

Every source file has a companion test file in `tests/`. From this directory:

```bash
python3 -m unittest discover -s tests      # all 28
python3 tests/test_orchestrator.py         # one file
```

Standard-library `unittest` — **not pytest**. `pytest` is not required and is not
assumed to be installed; a reader who reaches for it and finds nothing should not
conclude the suite is broken.

## Layout

```
src/      seven modules — the pipeline
tests/    six files, 28 tests
```

Tests resolve `src/` via a path shim (`sys.path.insert(..., "..", "src")`), matching
the convention used by the DBS and Morgan Stanley workflows in this directory.

---

## Known Limitations

- This is the thinnest-sourced entry in this series to date; nearly everything beyond the five confirmed Zurich bullets above is constructed.
- Translation is not a real multi-language NLP system — mock fixtures carry pre-computed extracted facts and confidence scores, matching this series' established pattern of deterministic stand-ins for real AI calls.
- Mock data only; no real Zurich, AgentricAI, or Clara system, credential, or data involved anywhere.
- The three-sub-claim dependency structure (flight cancellation → medical treatment → missed tour) is one illustrative shape of "conditional multi-variable logic," not a claim about how Clara — or any real travel-claims system — actually resolves dependent coverage questions.
- Coverage Check's impurity (fetching its own policy data rather than receiving it pre-fetched) is a deliberate, logged departure from this series' usual data/logic separation precedent, made because the test-isolation cost wasn't judged worth an unspecified sixth module for a build this thin-sourced. This trades slightly less clean test isolation for staying at the five stages the case study specifies.
- The Authorization Gate's total absence of default criteria is the clearest expression of where Zurich's public disclosure actually stops. This is not a placeholder awaiting a future threshold — it is the deliberate point.

---

## Explicit Non-Claims

This repository is not a disclosure of AgentricAI's actual Clara system. It does not claim to replicate Clara's agent architecture, agent count, or reasoning-trail mechanism, and should not be cited as evidence of how Clara works. It is built from the five confirmed Zurich bullets above, plus explicitly labeled construction everywhere the public record stops — with the Authorization Gate's total absence of default criteria standing, as in prior entries in this series, as the clearest expression of where that record actually ends.

Two specific figures that could plausibly but wrongly be attributed to Clara are explicitly disclaimed: the "11 modular AI Agents" figure belongs to a different Hyper Challenge winner (Wangari Global's Etio), and AgentricAI's generic "under two minutes per claim" marketing claim is not Zurich-pilot-specific and is not used anywhere in this build's reasoning.

---

*This README describes the implementation as built and tested. It is intended for reconciliation against the case study's illustrated workflow section, and as source material for drafting that section's reference-implementation discussion.*

---

## See also

- [`../../case-studies/11-zurich-agentic-ai-travel-claims.md`](../../case-studies/11-zurich-agentic-ai-travel-claims.md) — the case study this implements
- `DESIGN_SPECS.md` — component-by-component technical reference
- `DESIGN_DECISIONS.md` — why the judgment calls were made the way they were

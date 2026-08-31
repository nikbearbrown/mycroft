# DBS Credit-Memo Agentic System — Reference Implementation

**Status:** Built and tested. Six modules, all with passing tests that assert sequencing (via spy/mock, not just final output), following this series' standard pattern.

**Source case study:** DBS Bank — Agentic AI in Investment & Commercial Banking (Series: Agentic AI Adoption in Financial Services, 2025–2026). This reference implementation corresponds to Section 4 (Illustrated Workflow: A Relationship Manager Preparing a Credit Memo) and is intended to inform the case study's Section 4b.

This repository is **not** a disclosure of DBS's actual credit-memo system. See **Explicit Non-Claims** below before reading further.

---

## What This Is

DBS's own 19 August 2026 newsroom release describes specialised agents "tackling more than 70 different tasks" to synthesise raw data into a "review-ready first draft of a credit memo," rolled out to roughly 1,500 employees in DBS's Institutional Banking Group following a 150-participant pilot, targeting at least a 30% reduction in preparation time against a baseline where this work can consume up to 40% of a relationship manager's time.

That is the entire confirmed factual basis for this build. DBS discloses:
- **No** agent count (the release says "70+ tasks," not "70+ agents" — a distinct secondary source, Computer Weekly quoting DBS's Chief Data and Transformation Officer Nimish Panchmatia, characterizes it as "70 to 80 agents," but this is a journalist's paraphrase, not a DBS-stated figure, and is treated separately rather than merged in)
- **No** breakdown of what the 70+ tasks individually are
- **No** data-source list beyond "raw data"
- **No** specific approval or review protocol for agent-drafted memos
- **No** description of what happens after a relationship manager submits a finalized memo

This code does not attempt to fill in any of the above. Where DBS's disclosure stops, this implementation stops too — the gaps below are deliberate, not omissions to be improved on.

---

## Architecture

A single, linear-with-halts pipeline — not a multi-agent orchestration layer simulating DBS's undisclosed internal architecture:

```
Intake → Client Lookup → Draft Synthesis → Human Review Gate → Finalize/Submit
```

This is more precisely a **five-condition state machine** than the "four stages" the original pre-build blueprint described. That shift happened during design, not as an accident: keeping Draft Synthesis a pure function (no internal data-fetching) meant the client-lookup step needed its own halt condition, distinct from intake validation. The extra precision came from making the design buildable, not from adding scope DBS's disclosure doesn't support.

**Halt map:**

| # | Condition | Halts before | Mechanism |
|---|---|---|---|
| 1 | Intake incomplete (missing `client_id`, `facility_type`, or `requested_action`) | Client lookup | Returns a status object |
| 2 | Client record not found in mock data | Draft synthesis | Returns a status object |
| 3 | Draft synthesis flags a data gap | Human review | Returns a status object |
| 4 | Human Review Gate returns `not_cleared_for_finalization` | Finalize/submit | Returns a status object |
| 5 | All conditions clear | — | Finalize/submit runs, pipeline reaches terminal state |

Two additional failure modes are **exceptions**, not halt conditions, because they represent misuse of the code rather than a normal domain outcome:
- Constructing the Human Review Gate without a decision function → `TypeError`
- A supplied decision function returning anything other than `cleared_for_finalization` or `not_cleared_for_finalization` → `ValueError`

That second exception matters more than it looks: without it, an unrecognized return value would silently fail open — proceeding to finalize by default rather than by any deliberate answer. That's the one place in this codebase where a bug in *someone else's* code (a badly written decision function) could otherwise defeat the entire point of the gate below.

---

## Module Reference

| File | What it does | Confirmed / Constructed |
|---|---|---|
| `mock_data.py` | Fabricated client/credit records only — no real DBS data anywhere. Includes one deliberately incomplete record (`CLIENT-003`, missing `credit_rating`) so the gap-flagged path has something real to test against. | CONSTRUCTED |
| `intake.py` | Validates a memo request has the minimum required fields before anything else runs. | Required field list is CONSTRUCTED — DBS discloses no request schema or intake mechanism at all (Section 4, Step 1 states this directly). |
| `draft_synthesis.py` | Stand-in for the "70+ tasks" aggregate. One undecomposed function — deliberately does **not** simulate 70 discrete steps, agent handoffs, or a task list DBS never published. Also contains the data-gap-detection check. Pure function: receives an already-fetched client record, does not call `mock_data.py` itself. | Synthesis *capability* is CONFIRMED (DBS's own release). Internal mechanism, output shape, and the gap-detection check are all CONSTRUCTED. |
| `human_review_gate.py` | **The deliberately-absent-default component.** Contains zero built-in approval criteria — no confidence score, no dollar threshold, no severity rule. Requires an externally supplied decision function at construction or raises immediately. Strictly validates that function's return value. | Absence is deliberate by design, not a gap to fill. Directly grounded in DBS's own governance language (Panchmatia: AI capability innovation currently outpaces governance and control roughly five to one — "we need to close this gap before we allow autonomy"). |
| `finalize_submit.py` | Terminal stub representing a human finalizing and submitting the memo to DBS's existing, undisclosed credit-approval process. Returns a minimal status object only so the pipeline's completion is observable in tests. | CONSTRUCTED stub. Does not model DBS's actual downstream process — Section 4, Step 5 states directly that DBS discloses nothing about what happens next. |
| `orchestrator.py` | Runs all five stages in strict sequence per the halt map above. The only module with dependencies on all the others. | Mirrors DBS's disclosed shape (raw data in → review-ready draft → human review → finalize) without adding steps DBS hasn't described. |

---

## Naming: Why `cleared_for_finalization`, Not `not_authorized`

This series has generally used `not_authorized` as its convention for a rejected/blocked outcome (see HSBC's `not_approved` for a prior documented departure). This build uses `cleared_for_finalization` / `not_cleared_for_finalization` instead, deliberately.

**Reasoning:** "authorize" implies a credit decision. This gate doesn't make one. Section 4, Step 5 of the case study is explicit that after a relationship manager finalizes and submits a memo, it enters DBS's existing, separate credit-approval process — which this code does not model at all. What the Human Review Gate actually decides is narrower: whether a draft is fit to *proceed toward* that process. The naming reflects Section 4's own language ("finalises the memo"), not an invented decision category.

One more thing worth being direct about: **Section 4 never illustrates a rejection.** Wei Ling reviews, edits as needed, finalizes, and submits — one continuous path, no branch where a draft is killed. `not_cleared_for_finalization` is CONSTRUCTED specifically because a review step that structurally cannot say no isn't a review step — it's grounded in Panchmatia's governance-gap statement, not in a worked example from the case study. That distinction is worth preserving if this README informs Section 4b: the *naming* is source-grounded; the *existence of a rejection path* is a reasoned construction, not something DBS illustrated.

---

## What the Tests Prove

Following this series' mock/spy-assertion pattern — proving sequencing, not just final output:

- Incomplete intake → client lookup and draft synthesis are asserted **never called** (not just: the result looks halted).
- Unknown client ID → draft synthesis asserted never called.
- Data-gap-flagged synthesis → Human Review Gate construction asserted never called.
- Gate returns `not_cleared_for_finalization` → finalize asserted never called.
- Gate's decision function returns an unrecognized value → `ValueError` propagates, and finalize is asserted never called — this is the test that actually proves the zero-default gate can't be silently defeated by a malformed caller.
- A clean, complete case (`CLIENT-001`, decision function returns `cleared_for_finalization`) runs end-to-end to a `handoff_attempted` terminal state — proving the happy path works, not only the halts.
- Missing decision function still raises `TypeError` at gate construction, even when invoked through the orchestrator's entry point.

Every source file has a companion test file in `tests/`. Run any of them directly (e.g. `python3 tests/test_orchestrator.py`) or as a suite via your test runner of choice.

---

## Known Limitations

- Draft Synthesis is a deterministic stand-in, not a real multi-agent system. It does not model 70 discrete tasks, agent-to-agent handoff, or DBS's actual data pipeline — and it was deliberately never decomposed to look like it does.
- No real LLM, credit data, or DBS system is used anywhere in this repository.
- This pipeline models one memo's path through the system, not throughput at DBS's actual institutional-banking scale.
- The Human Review Gate's total absence of default criteria is the clearest expression of where DBS's public disclosure actually stops. This is not a placeholder awaiting a future threshold — it is the deliberate point.
- The gate's `not_cleared_for_finalization` outcome, and the naming built around it, is a reasoned construction from DBS's governance language, not a scenario DBS's own Section 4 illustration ever depicts.

---

## Explicit Non-Claims

This repository is not a disclosure of DBS's actual credit-memo system. It does not claim to replicate DBS's agent architecture, agent count, task breakdown, data sources, or review process, and should not be cited as evidence of DBS's technical design. Every CONSTRUCTED element above exists to make a testable reference implementation possible — not as a guess about what DBS actually built.

---

*This README describes the implementation as built and tested, superseding the original pre-build blueprint's four-stage framing where the two differ (see "Architecture" above). It is intended for reconciliation against Section 4 of the DBS case study, and as source material for drafting Section 4b.*

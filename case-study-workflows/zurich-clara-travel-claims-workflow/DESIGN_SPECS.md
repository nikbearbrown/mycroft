# Design Specs

Technical reference for each component in this pipeline: purpose, interface,
inputs/outputs, and explicit scope boundaries. For *why* certain choices were
made, see `DESIGN_DECISIONS.md`. For a narrative walkthrough, see `README.md`.

---

## Pipeline Shape

```
claim ──► Intake ──► Extraction ──► Coverage Check ──► Authorization Gate ──► Resolve
             │            │               │                     │
             ▼            ▼               ▼                     ▼
          reason=      reason=         reason=               reason=
           None      low_extraction  cross_document    authorization_gate
        (structural)  _confidence     _contradiction       _rejection
        missing_      low_translation no_matching_policy
        document      _confidence     unresolvable_sub_claim_dependency
```

Strict, linear, fail-fast, with **eight halt conditions across four stages**.
A claim that fails at any stage never reaches a later one: Extraction is never
called for a structurally incomplete claim, Coverage Check is never called for
a low-confidence extraction, the Gate is never constructed for a claim with no
matching policy, and **neither terminal state is reached** when the Gate's
decision function returns something malformed.

Each of those properties is asserted directly with mock spies, not inferred
from the returned status — eight `assert_not_called()` assertions in total.

**Five stages rather than the three used at CommBank, Klarna and Lemonade.**
The travel-claims scenario genuinely requires Extraction separated from Intake
(multiple documents, multiple languages) and Coverage Check separated from a
final Gate (interacting sub-claims). This still matches what Zurich's record
supports: one orchestration system, not a documented multi-agent handoff
protocol with named roles or a disclosed agent count.

The Gate has no default criteria and cannot run without an externally supplied
decision function — see `DESIGN_DECISIONS.md` §1.

---

## `src/intake.py`

**Purpose.** Validate a bundled claim submission before anything downstream
runs.

**Interface.** `validate_intake(claim) -> dict`

**Owns two distinct checks:**

1. **Structural completeness** — every document carries a `type` and a
   `language` tag.
2. **Document completeness** — a required document type is not missing given
   what the claim itself asserts (a claimed medical expense with no receipt).

**Returns.**

| status | reason | when |
|---|---|---|
| `ok` | — | both checks pass |
| `halted` | `None` | structural incompleteness |
| `halted` | `missing_document` | a required document type is absent |

**The `None` reason is deliberate**, not an oversight — see
`DESIGN_DECISIONS.md` §3. At that point the pipeline has not extracted enough
to characterise the failure, so it declines to manufacture a specific-sounding
reason it cannot support.

**Scope boundary.** The document-type taxonomy (`flight_notice` /
`medical_receipt` / `free_text_note`) and the language-tagging schema are
`[DEV]` construction. Zurich and AgentricAI disclose no intake schema at all.

---

## `src/extraction.py`

**Purpose.** Validate per-document extraction and translation confidence
against thresholds.

**Interface.** `extract(documents) -> dict`

**Pure function.** Receives already-tagged documents from Intake, fetches
nothing, does not touch `mock_data.py`.

**Returns.**

| status | reason |
|---|---|
| `ok` | — |
| `halted` | `low_extraction_confidence` |
| `halted` | `low_translation_confidence` |

**The two scores are tracked separately and this is load-bearing** — see
`DESIGN_DECISIONS.md` §2. A document can be translated with high linguistic
confidence and still yield low-confidence structured extraction, or the
reverse. Collapsing them into one score would hide exactly the failure this
pipeline exists to surface.

Extraction confidence is checked for **every** document. Translation
confidence is checked only where it is not `None` — i.e. non-English documents
under the `[DEV]` language-tagging schema.

**Scope boundary.** The specific thresholds (0.70 / 0.70) are `[DEV]`. This
module is a deterministic stand-in for real extraction and translation; it
calls no LLM and no NLP system, and the mock fixtures carry pre-computed facts
and scores.

---

## `src/coverage_check.py`

**Purpose.** Evaluate an extracted claim against a mock policy record.

**Interface.** `check_coverage(claim_id, policy_id, documents) -> dict`

**Owns four responsibilities, in a fixed order** locked during design review:

1. Cross-document contradiction check
2. Policy record fetch
3. Three interacting coverage rules
4. Sub-claim dependency check

**The order is fixed by design, not by accident** — see
`DESIGN_DECISIONS.md` §4. A claim that could trigger both a contradiction and
a missing-policy halt has a deterministic, designed answer for which fires,
and a test locks it by construction.

**Returns.**

| status | reason |
|---|---|
| `ok` | — (with `coverage_result`) |
| `halted` | `cross_document_contradiction` |
| `halted` | `no_matching_policy` |
| `halted` | `unresolvable_sub_claim_dependency` |

**Deliberately impure.** This module fetches its own policy record rather than
receiving one pre-fetched — a logged departure from this project's usual
data/logic separation, reasoned in `DESIGN_DECISIONS.md` §5.

**Scope boundary.** The *existence* of conditional multi-variable coverage
logic is this case study's construction, built to demonstrate the operational
problem in case study §2 — not a Zurich- or AgentricAI-disclosed mechanism.
A minimum of three interacting rules is a hard floor.

---

## `src/authorization_gate.py`

**Purpose.** Gate a claim between Coverage Check and Resolve/Escalate.

**Interface.** `AuthorizationGate(decision_fn)` · `.decide(coverage_result) -> str`

**Contains zero built-in approval criteria** — no dollar threshold, no
confidence cutoff, no claim-type restriction, under any label anywhere in the
file. Verified: the class body contains no numeric literals at all.

| condition | behaviour |
|---|---|
| `decision_fn is None` | raises `TypeError` at construction |
| return value not in `VALID_DECISIONS` | raises `ValueError` |
| valid | returns `resolved_by_human` or `escalated_to_human` |

**Terminal-state naming** is `resolved_by_human` / `escalated_to_human` rather
than this series' more common `not_authorized` — a logged departure grounded
in Zurich's own "keeping humans in control" phrasing, which frames this as a
control-locus question rather than an authorization one.

`demo_decision_fn` exists solely so the pipeline is runnable end to end. It is
**explicitly not `[DEV]`-marked**: it is a named, logged exception carrying no
claim to represent Clara's actual authority boundary.

---

## `src/orchestrator.py`

**Purpose.** Run all five stages in strict sequence per the locked halt map.
The only module with dependencies on all the others.

**Interface.** `run_pipeline(claim, decision_fn) -> dict`

**No default `decision_fn` is provided anywhere in this pipeline.** A caller
must supply one, or the Gate raises.

Mirrors Zurich's disclosed shape only at the level Zurich actually confirmed:
orchestration exists, coordinates specialised handling, keeps a human-control
point, and produces an auditable trail — here, the sequence of stage results
this function naturally returns. It does not add steps, agent counts, or
handoff protocols Zurich never described.

---

## `src/resolve_escalate.py` · `src/mock_data.py`

`resolve_escalate.py` — the two terminal states, kept in one small module so
the orchestrator's exits are symmetrical and both are patchable by name in
tests.

`mock_data.py` — fabricated claim fixtures and policy records. The Kwame happy
path plus six halt scenarios. No external services, credentials, or
Zurich/AgentricAI systems are involved anywhere in this repository.

---

## Tests

**28 tests across six files**, following this project's spy/mock-assertion
pattern that proves *sequencing* rather than only final output.

```bash
cd tests && for f in test_*.py; do python3 "$f"; done
```

Standard-library `unittest` — **not pytest**. Run per file, or a reader will
conclude the suite is broken.

What they prove, beyond return values:

- A structurally incomplete claim never reaches Extraction, Coverage Check or
  the Gate.
- Low extraction and low translation confidence each independently halt before
  Coverage Check, with **different named reasons** — proving the score
  separation does functional work rather than existing as an unused field.
- The tour sub-claim's coverage outcome actually changes across two
  differently-shaped claims depending on the flight sub-claim's own outcome.
- A claim engineered to trigger both a contradiction and a missing-policy
  condition **deterministically resolves to the contradiction**, locking the
  fixed ordering by construction.
- The Gate raises `TypeError` on a missing decision function and `ValueError`
  on an invalid return, and in both cases **neither `resolve` nor `escalate`
  is reached**.
- The complete Kwame scenario runs end to end to a resolved terminal state —
  so the happy path is proven, not only the halts.

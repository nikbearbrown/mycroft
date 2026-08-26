# Design Specs

Technical reference for each component in this pipeline: purpose, interface,
inputs/outputs, and explicit scope boundaries. For *why* certain choices were
made, see `DESIGN_DECISIONS.md`. For a narrative walkthrough, see `README.md`.

---

## Pipeline Shape

```
request ──► Intake ──► Client Lookup ──► Draft Synthesis ──► Human Review Gate ──► Finalize
               │             │                  │                    │
               ▼             ▼                  ▼                    ▼
         halt_stage=     halt_stage=       halt_stage=          halt_stage=
          "intake"     "client_lookup"  "draft_synthesis"  "human_review_gate"
```

Strict, linear, fail-fast, with five halt conditions. A request that fails at
any stage never reaches a later one: Client Lookup is never called for
incomplete intake, Draft Synthesis is never called for an unknown client, the
Gate is never even *constructed* for a gap-flagged draft, and Finalize is never
called for a draft the Gate did not clear. Each of those properties is asserted
directly with mock spies, not inferred from the returned status.

The Gate has no default criteria and cannot run without an externally supplied
decision function — see `DESIGN_DECISIONS.md` §1.

---

## Intake (`intake.py`)

**Purpose:** validate that a memo request carries the fields the pipeline needs
before any data is fetched.

```python
REQUIRED_FIELDS = ["client_id", "facility_type", "requested_action"]  # [DEV]

def validate_intake(request: dict) -> IntakeResult
```

**Returns:** `IntakeResult` — `{status: "complete" | "incomplete",
missing_fields: list[str], request: dict}`.

**Scope:** the three required fields are **CONSTRUCTED**. DBS discloses no
request schema; this asserts only that some triggering action exists, since a
memo has to start somewhere. Validation is presence-only — no type coercion, no
business-rule checking, no client-id format validation.

---

## Client Lookup (`mock_data.py`)

**Purpose:** resolve a `client_id` to a client record, so Draft Synthesis can
remain a pure function.

```python
def get_client_record(client_id: str) -> Optional[dict]
```

**Returns:** the record, or `None` for an unknown id — which halts the pipeline
at `halt_stage="client_lookup"`.

**Scope:** entirely fabricated mock data. No real DBS systems, credentials, or
client data are involved anywhere in this repository. One record is
deliberately incomplete, to exercise the gap-flagged path (`DESIGN_DECISIONS.md`
§7).

---

## Draft Synthesis (`draft_synthesis.py`)

**Purpose:** turn a client record into a review-ready first draft, and flag the
draft if required information is absent.

```python
REQUIRED_SYNTHESIS_FIELDS = [...]

def synthesize_draft(client_record: dict) -> DraftResult
```

**Returns:** `DraftResult` — `{status: "complete" | "gap_flagged",
draft: Optional[dict], gap_reason: Optional[str]}`. The orchestrator halts on
`status == "gap_flagged"`.

**A pure function by design.** It receives an already-fetched record and never
fetches data itself. That constraint is what forced Client Lookup into its own
stage (`DESIGN_DECISIONS.md` §3).

**Scope:** this is a deterministic stand-in. It does **not** decompose into 70
discrete tasks, simulate agent handoffs, or model DBS's data pipeline. DBS
describes "more than 70 different tasks" only in aggregate and discloses no
breakdown; the confirmed capability is treated as a single unit because that is
how it was confirmed. Note that "70+" is a **task** count, not an agent count —
see `DESIGN_DECISIONS.md` §5.

---

## Human Review Gate (`human_review_gate.py`)

**Purpose:** decide whether a synthesized draft proceeds to finalization. This
is the deliberately-absent-default component.

```python
VALID_OUTCOMES = ("cleared_for_finalization", "not_cleared_for_finalization")

class HumanReviewGate:
    def __init__(self, decision_function: Callable[[dict], str])
    def review(self, draft: dict) -> str
```

**Two distinct failure modes, deliberately distinguished:**

| Raised | When | Why it exists |
|---|---|---|
| `TypeError` | at construction, if no callable decision function is supplied | the gate ships with no approval logic and will not invent one |
| `ValueError` | at `review()`, if the decision function returns an unrecognized value | prevents failing open — proceeding by default rather than by a deliberate answer |

**Contains no approval logic of its own.** No confidence score, no dollar
threshold, no severity rule, under any marker, anywhere. See
`DESIGN_DECISIONS.md` §1 and §2.

**On the outcome names:** this gate does not authorize a credit decision — a
finalized memo enters DBS's separate, undisclosed credit-approval process after
this point. The names follow the case study's own language rather than this
series' usual `not_authorized` convention (`DESIGN_DECISIONS.md` §4).

---

## Finalize / Submit (`finalize_submit.py`)

**Purpose:** terminal handoff.

```python
def finalize(draft: dict) -> FinalizeResult
```

**Returns:** `FinalizeResult` — `{status: "handoff_attempted", client_id: str,
memo_reference: str}`. `status` is always `handoff_attempted`: this stub
records that handoff was reached, and claims nothing about what DBS's
downstream process then does.

**Scope:** a stub, and deliberately so. Section 4 of the case study ends at
handoff; DBS has not described what happens after a relationship manager
submits a finalized memo. Modelling a downstream approval workflow would be
inventing the part the record does not contain.

---

## Orchestrator (`orchestrator.py`)

**Purpose:** run the five stages in order, halting at the first condition that
is not clear to proceed, and never calling a later stage after a halt.

```python
def run(request: dict, decision_function: Callable[[dict], str]) -> PipelineResult
```

**Returns:** `PipelineResult` — `{halted: bool, halt_stage: Optional[str],
reason: Optional[str], finalize_result: Optional[dict]}`. When `halted` is
`True`, `halt_stage` names the stage that stopped it and `finalize_result` is
`None`.

**Halt map:**

| # | Condition | `halt_stage` | Halts before |
|---|---|---|---|
| 1 | intake incomplete | `"intake"` | client lookup |
| 2 | client record not found | `"client_lookup"` | draft synthesis |
| 3 | draft synthesis returns `status == "gap_flagged"` | `"draft_synthesis"` | Gate **construction** |
| 4 | gate returns `not_cleared_for_finalization` | `"human_review_gate"` | finalize / submit |
| 5 | decision function returns an unrecognized value | *(raises `ValueError`)* | finalize / submit |

The decision function is passed through to the Gate rather than held by the
orchestrator, so the "no default criteria" property holds at the entry point
too: calling `run()` without one raises at gate construction.

---

## Test Suite

Six modules, six companion test files, standard-library `unittest`, no
dependencies. Each runs standalone:

```bash
python3 tests/test_orchestrator.py
```

**Sequencing is asserted with mock spies, not inferred from output.** A
pipeline can return the correct final status while still having executed work
it should have skipped, so the tests patch downstream stages and assert they
were never called.

What the suite proves:

- incomplete intake halts before client lookup **and** draft synthesis are called
- an unknown client id halts before draft synthesis is called
- a gap-flagged draft halts before the Human Review Gate is even constructed
- `not_cleared_for_finalization` halts before finalize is called
- an unrecognized decision-function return raises `ValueError` and **still**
  halts before finalize — the test that specifically proves the zero-default
  gate cannot be silently defeated by a malformed caller
- a missing decision function raises `TypeError` at gate construction, including
  when invoked through the orchestrator's entry point
- a clean, complete case runs end-to-end to a terminal `handoff_attempted`
  state — confirming the happy path works, not only the halts

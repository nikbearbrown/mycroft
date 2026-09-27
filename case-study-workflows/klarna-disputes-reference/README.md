# Klarna Disputes Reference Implementation

A small, fully-tested reference implementation illustrating one plausible way to
build a customer-service dispute pipeline consistent with what Klarna's own
February 2024 press release confirms its AI assistant does — while making every
undisclosed mechanism an explicit, labeled, testable decision instead of a
hidden assumption.

**This is not Klarna's real system, does not use any real Klarna data, and does
not claim to disclose how Klarna's actual assistant works.** It's a starting
point for understanding one honest way to design and test this kind of
workflow, built so you don't have to design it from scratch.

If you're new to this repo, read this file top to bottom before opening any
code — it's written so that alone is enough to make sense of what's here and why.

---

## 1. What This Actually Is

Klarna confirms, in its own words, that its AI assistant handles refunds,
returns, payment-related issues, cancellations, disputes, and invoice
inaccuracies; provides real-time balance and payment-schedule updates;
explains spending limits; operates in 35+ languages; and always preserves a
human option. It confirms **nothing** about how any of that actually works —
no authentication flow, no data-access mechanism, no escalation logic.

This repo picks two of those confirmed functions — a **late fee dispute**
(an invoice-inaccuracy question) and a **refund request** — and builds a
complete, working, tested pipeline around them. Everything beyond "these two
functions exist" is invented for this build, and every invented piece is
marked `[DEV]` in the code so you know exactly what to swap out if you adopt
this for your own use.

**Why only two functions, not all six confirmed ones?** Depth over breadth.
This repo demonstrates two functions completely — full pipeline, full test
coverage, every decision path exercised — rather than six functions
shallowly. See `docs/DESIGN_DECISIONS.md`, DD-006, for the reasoning.

---

## 2. How a Request Actually Flows Through This System

```
Customer message + customer_id
            |
            v
      ┌─────────────┐
      │  intake.py  │   classifies the dispute type, extracts the one
      └─────────────┘   claim detail that matters for that type
            |
            | IntakeResult
            v
   ┌──────────────────┐
   │ verification.py  │   looks up the customer's record, checks the
   └──────────────────┘   claim against it
            |
            | VerificationResult
            v
      ┌───────────┐
      │  gate.py  │   decides: auto-resolve, or escalate to a human?
      └───────────┘
            |
            | GateDecision
            v
   ┌────────────────────┐
   │  orchestrator.py   │   calls all three above, in strict order,
   └────────────────────┘   stopping immediately on any structural failure

```

**The orchestrator is the only file that runs this whole sequence.** If you
only read one file to understand how a request moves through this system,
read `src/orchestrator.py` — it's short, and its whole job is to make the
sequencing itself provably correct, not just described correctly in prose.

---

## 3. The Two Dispute Types, and Why They're Not Symmetric

| | `late_fee_dispute` | `refund_request` |
|---|---|---|
| What the customer is claiming | "I paid on time" | "I want this amount back" |
| The field that actually matters | a **date** | an **amount** |
| What gets checked against the record | claimed date vs. the record's `payment_date` | claimed amount vs. the record's `amount_paid` |
| The one escalation reason unique to this type | `ambiguous_delay` — a late payment the record itself flags as a processing delay | *(none — always resolves to the generic `mismatch` on disagreement)* |

This asymmetry is deliberate, not an oversight — see `docs/DESIGN_DECISIONS.md`
DD-007. A refund request and a late-fee dispute aren't the same *kind* of
claim, and treating them identically (checking both a date and an amount for
both types) would have made `refund_request` nearly impossible to complete,
since customers disputing a refund amount rarely mention a date at all.

---

## 4. Every Way a Request Can End Up

Six possible outcomes, each independently tested (see `tests/test_escalation_paths.py`):

| Reason | What it means | Who decides it |
|---|---|---|
| *(none — resolved)* | Everything checked out; no human needed | `gate.py` |
| `unclassified` | The message didn't match either dispute type at all | `orchestrator.py` (via `intake.py`) |
| `no_record` | We don't recognize this customer | `orchestrator.py` (via `verification.py`) |
| `incomplete_claim` | Customer is real, but didn't give us the one detail this dispute type needs | `orchestrator.py` (via `verification.py`) |
| `mismatch` | The record disagrees with the customer's claim, plainly | `gate.py` |
| `ambiguous_delay` | The record disagrees, but flags a reason outside the customer's control (`late_fee_dispute` only) | `gate.py` |
| `low_confidence` | The record actually agrees with the customer — we just weren't confident about what they were even asking for | `gate.py` |

Notice the three orchestrator-owned reasons are about the **pipeline failing
to even check** something (unknown customer, missing detail, unreadable
message). The three gate-owned reasons are about **what happens once a check
actually runs**. That split is a real design decision, not just a filing
convenience — see DD-002.

---

## 5. Repo Layout

```
src/
  intake.py         classifies the message, extracts the relevant claim detail
  verification.py   looks up the record, checks the claim against it
  gate.py           decides auto-resolve vs. escalate
  orchestrator.py   runs the above three in strict, fail-fast sequence

mock_data/
  transactions.json  four fabricated customer records — no real data

tests/
  test_intake_verification_dependency.py   Verification fails gracefully, never crashes, on bad Intake input
  test_verification_gate_dependency.py     Gate defends its precondition and enforces the mismatch-before-confidence rule
  test_fail_fast_pipeline.py               Orchestrator actually stops before Gate on every structural failure
  test_escalation_paths.py                 All six outcomes are independently reachable with the right reason
  test_negative_and_positive_cases.py      Both dispute types have a working "everything's fine" path, not just failure paths

docs/
  DESIGN_DECISIONS.md   every invented decision, why it was made, and — where it happened — what the rejected alternative was
  DESIGN_SPECS.md        the full technical spec: data contracts, component behavior, escalation ownership
```

---

## 6. Running It

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

All 23 tests pass as of this writing. If you change anything in `src/`, run
the suite again before trusting the change — this repo's whole premise is
that running tests catches things a design review doesn't, and that held
true even during this build (see DD-014: two real gaps in the original
design specs — a missing function parameter and undefined comparison
semantics — only surfaced once the code actually had to run, after four
separate design review passes had already signed off on the spec).

---

## 7. Every `[DEV]` Marker In This Repo, In One Place

If you're adapting this for your own use, these are the places built to be
swapped, not just left as-is:

- **`intake.py`** — the keyword lists (illustrative, not tuned on real
  message data), the confidence tier values (`0.9` / `0.5` / `0.0`), and the
  `late_fee_dispute`-before-`refund_request` tiebreak order.
- **`verification.py`** — the exact-match tolerance (a real system almost
  certainly needs a grace window; this doesn't, on purpose, so the omission
  is visible), and the mock data file path (swap for a real database call).
- **`gate.py`** — the `0.6` confidence threshold, explicitly not derived from
  any real data.
- **`orchestrator.py`** — the response dict shape, which is illustrative and
  should be adapted to whatever your actual API contract needs.

---

## 8. What This Repo Deliberately Does *Not* Do

- Does not use machine learning anywhere — `intake.py`'s classification is
  plain keyword matching, stated as such in its own docstring.
- Does not disclose or claim to disclose Klarna's real architecture,
  authentication flow, or data infrastructure.
- Does not cover all six of Klarna's confirmed functions — see Section 1.
- Does not include a "high-value" or "VIP" routing flag. One was considered
  during design and cut entirely — see DD-003 — because nothing in Klarna's
  public disclosures or this build's own illustrative scenario ever
  supported inventing one.

---

## 9. Where to Go Next

- **Want the full rationale behind every invented decision, including the
  ones that were debated and reversed?** Read `docs/DESIGN_DECISIONS.md`.
- **Want the full technical specification — every data contract, every
  component's exact behavior?** Read `docs/DESIGN_SPECS.md`.
- **Want to see the decisions actually enforced, not just described?** Run
  the test suite (Section 6) and read `tests/test_escalation_paths.py` first —
  it's the one file that proves every outcome in the table in Section 4
  is real and independently reachable.

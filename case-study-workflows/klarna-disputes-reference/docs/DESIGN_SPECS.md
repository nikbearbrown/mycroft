# DESIGN_SPECS.md

**WHAT THIS FILE DOES:** Describes the architecture of this reference implementation — data flow, contracts between components, and what each component is and isn't responsible for — as it was designed before any code was written.

---

## 1. What This Repo Is

Klarna's own February 2024 press release confirms *what* its AI assistant does: handling refunds, returns, payment-related issues, cancellations, disputes, and invoice inaccuracies; providing real-time balance and payment-schedule updates; explaining spending limits; operating in 35+ languages; preserving a human option. It confirms nothing about *how* — no authentication flow, no data-access mechanism, no escalation threshold logic.

This repo builds the thinnest working system that performs a narrow, illustrative slice of the confirmed functions, and makes every unconfirmed mechanism an explicit, labeled, testable decision rather than an assumed one. It is not a disclosure of Klarna's real system. Every invented value is marked `[DEV]` in code as a signal to customize it.

**Scope, stated plainly:** this build covers two dispute types — `late_fee_dispute` and `refund_request` — not the full confirmed function list. That's a deliberate scope decision (see `DESIGN_DECISIONS.md`, DD-006), not an oversight.

---

## 2. Data Flow

```
Customer message
        |
        v
   [intake.py]  --classifies dispute type, extracts the relevant claim field--
        |
        | IntakeResult
        v
 [verification.py]  --looks up record, checks the relevant field against it--
        |
        | VerificationResult
        v
     [gate.py]  --decides auto-resolve vs. escalate, only for substantive outcomes--
        |
        | GateDecision
        v
 [orchestrator.py]  --sequences all three, stops early on structural failure--
```

Orchestrator is the only component responsible for sequencing. It stops the pipeline at two points before Gate is ever invoked; Gate is never called with a status it can't handle.

---

## 3. Data Contracts

### `IntakeResult`
| Field | Type | Notes |
|---|---|---|
| `status` | `"ok"` \| `"escalate_unclassified"` | The one field downstream code dispatches on |
| `dispute_type` | `"late_fee_dispute"` \| `"refund_request"` \| `"unclassified"` | |
| `confidence` | `float` | `0.9` exact single-type match, `0.5` ambiguous/multi-type match, `0.0` no match |
| `claimed_date` | `str` \| `None` | Only relevant for `late_fee_dispute` |
| `claimed_amount` | `float` \| `None` | Only relevant for `refund_request` |

### `VerificationResult`
| Field | Type | Notes |
|---|---|---|
| `status` | `"match"` \| `"mismatch"` \| `"escalate_no_record"` \| `"escalate_incomplete_claim"` | One dispatch field, same pattern as `IntakeResult` |
| `mismatch_reason` | `None` \| `"claim_mismatch"` \| `"processing_delay_noted"` | Only populated when `status == "mismatch"`. `processing_delay_noted` is only reachable for `late_fee_dispute` |

Only `"match"` and `"mismatch"` ever reach Gate. `"escalate_no_record"` and `"escalate_incomplete_claim"` are structural failures, handled entirely by the orchestrator.

### `GateDecision`
| Field | Type | Notes |
|---|---|---|
| `outcome` | `"resolved"` \| `"escalated"` | |
| `reason` | `None` \| `"mismatch"` \| `"ambiguous_delay"` \| `"low_confidence"` | Only populated when `outcome == "escalated"` |

**Naming note:** `VerificationResult.mismatch_reason` and `GateDecision.reason` are two different vocabularies describing the same underlying event at two layers — one is "what Verification found," the other is "what Gate decided to do about it." Gate's `evaluate()` maps `mismatch_reason == "claim_mismatch"` to its own `reason: "mismatch"`. This is intentional, not duplicated by accident.

---

## 4. Component Specifications

### `intake.py`
**Confirmed-function mapping:** handling disputes and invoice inaccuracies (`late_fee_dispute`), and refunds (`refund_request`).

- `classify_intent(message)`: keyword-set matching, checked in fixed order — `late_fee_dispute` before `refund_request` `[DEV]`. Both sets match → `dispute_type` = first-checked, `confidence = 0.5`. One set matches → that type, `confidence = 0.9`. Neither → `"unclassified"`, `confidence = 0.0`.
- `extract_claim_details(message)`: pattern-matches a date and/or amount. Returns `None` per field if not found — must not guess.
- `run_intake(message)`: combines both, sets `status`.

**Must not:** use ML/embedding calls — regex/keyword matching only, stated in the docstring. Never return more than one `dispute_type`. Never fabricate a claim field it didn't find.

### `verification.py`
**Confirmed-function mapping:** real-time balance and payment-schedule updates — this file is the constructed stand-in for that function; nothing about its internal matching logic is Klarna-disclosed.

**Correction made during implementation:** every design pass before code wrote this as `run_verification(intake_result)`. That signature is incomplete — `lookup_record` needs a `customer_id`, and `IntakeResult` never carries one (customer identity comes from the caller, not from anything in the message text). No review pass caught this, because a spec bullet doesn't have to compile. The corrected signature is `run_verification(intake_result, customer_id)`, and the orchestrator passes `customer_id` through from its own parameters.

- `run_verification(intake_result, customer_id)`:
  1. `lookup_record(customer_id)` — no record → `status = "escalate_no_record"`.
  2. Only if a record exists: check whether the field relevant to `dispute_type` (`claimed_date` for `late_fee_dispute`, `claimed_amount` for `refund_request`) is present → missing → `status = "escalate_incomplete_claim"`.
  3. Only if both pass: `compare_claim_to_record`, checking only the relevant field.
- Comparison outcomes: exact match on the relevant field → `"match"`. Mismatch, with the record's `delay_reason` flag present (only meaningful for `late_fee_dispute`) → `"mismatch"` / `"processing_delay_noted"`. Mismatch, no flag, or any `refund_request` mismatch → `"mismatch"` / `"claim_mismatch"`.
- **Comparison semantics, made explicit during implementation (see DD-014):** for `late_fee_dispute`, `claimed_date` is compared against the record's `payment_date` — the customer's account of when they paid, checked against what's on file. For `refund_request`, `claimed_amount` is compared against the record's `amount_paid` — the customer's account of how much they paid, which they're asking back. Neither of these specific field-to-field mappings was decided in any review pass before code; they were the first workable reading available once the function actually had to compare something to something.

**Must not:** call the comparison step before both the record-exists and completeness checks pass. Invent a match tolerance beyond exact-match — none is disclosed, so none is assumed `[DEV]`.

### `gate.py`
**Confirmed-function mapping:** none — this file exists entirely to make Klarna's undisclosed "nuanced vs. straightforward" routing decision visible and swappable, not defensible as correct.

**Precondition (defended in code, not assumed):** only ever called with `VerificationResult.status` in `{"match", "mismatch"}`. Called with either escalate-status → raises, as a contract-violation signal, not a silent mis-evaluation.

**Decision order:**
1. `status == "mismatch"` → `outcome = "escalated"`, `reason` = `"ambiguous_delay"` if `mismatch_reason == "processing_delay_noted"` else `"mismatch"`.
2. Else `confidence < 0.6` `[DEV]` → `outcome = "escalated"`, `reason = "low_confidence"`.
3. Else → `outcome = "resolved"`.

Mismatch-family checked before confidence: a disagreement with Klarna's own record is treated as a more urgent finding than Intake's self-reported uncertainty.

**Must not:** reintroduce a "high-value" or any other criterion beyond what's specified above.

### `orchestrator.py`
**Confirmed-function mapping:** the human-option-preserved principle, realized as fail-fast sequencing — this is the only file that proves the pipeline actually runs in order rather than a story-shaped approximation of one.

`handle_query(message, customer_id)`:
1. `run_intake` → `status == "escalate_unclassified"` → return `{escalated: True, reason: "unclassified"}`.
2. `run_verification` → `status == "escalate_no_record"` → return with `reason: "no_record"`. `status == "escalate_incomplete_claim"` → return with `reason: "incomplete_claim"`.
3. Only if both pass → `gate.evaluate()` → return its outcome and reason.

**Must not:** fall back, retry, or guess on partial data anywhere in this file.

---

## 5. Escalation Reason Inventory

| Reason | Owner | Reachable when |
|---|---|---|
| `unclassified` | Orchestrator | Intake couldn't classify the message at all |
| `no_record` | Orchestrator | No customer record found |
| `incomplete_claim` | Orchestrator | Record exists, but the type-relevant claim field is missing |
| `mismatch` | Gate | Record found, relevant field doesn't match, no delay flag |
| `ambiguous_delay` | Gate | `late_fee_dispute` only — record found, date doesn't match, delay flag present |
| `low_confidence` | Gate | Relevant field matches, but Intake's confidence was below threshold |

---

## 6. Mock Data Schema

`mock_data/transactions.json` — four records, each fabricated, no real Klarna data:

| Record | `due_date` vs. `payment_date` | `amount_due` vs. `amount_paid` | `delay_reason` | Drives |
|---|---|---|---|---|
| R1 | On time | Equal | None | Positive cases (both dispute types), `low_confidence` |
| R2 | Late | Unequal | None | `mismatch` (both dispute types — date for `late_fee_dispute`, amount for `refund_request`) |
| R3 | *(no record for this customer)* | | | `no_record` |
| R4 | Late | Equal | Present | `ambiguous_delay` |

`unclassified` and `incomplete_claim` need no dedicated record — driven by message content alone.

---

## 7. Test Coverage Map

| File | Proves |
|---|---|
| `test_intake_verification_dependency.py` | Verification fails gracefully (never crashes) when the type-relevant claim field is missing, and correctly ignores the *other* field's absence |
| `test_verification_gate_dependency.py` | Gate refuses structurally-invalid input (raises), and its mismatch-before-confidence precedence holds regardless of confidence value |
| `test_fail_fast_pipeline.py` | Orchestrator stops before Gate on every structural failure, and does call Gate exactly once when it shouldn't stop |
| `test_escalation_paths.py` | All six escalation reasons are independently reachable with the correct reason attached |
| `test_negative_and_positive_cases.py` | Both dispute types have a working auto-resolve path (not just escalation paths), and the `ambiguous_delay` case produces an observable, correct output |

---

## 8. Non-Claims

This repo does not disclose Klarna's real architecture. Every mechanism above beyond the confirmed function list (Section 3.1 of the accompanying case study) is a labeled construction for illustrative purposes.

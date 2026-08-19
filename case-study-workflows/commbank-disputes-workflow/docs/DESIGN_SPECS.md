# Design Specs — Filled Out Before Any Code

This file is completed before any code, matching the case study's own
Section 4 (Illustrated Workflow) and Section 4b (Reference Implementation).
The orchestrator does not get written until every row below has an
explicit CONFIRMED or CONSTRUCTED tag with a stated reason — not a guess.

---

## Dependency-Mapping Worksheet

| Step | Produces (output fields) | Consumes (needs as input) | Confirmed or Constructed dependency |
|---|---|---|---|
| **Intake** | `dispute_type`, `claimed_amount`, `claimed_merchant`, `claimed_date`, `extraction_confidence` | raw customer text (external) | N/A — first step, no upstream dependency |
| **Verification** | `record_found` (bool), `match_result` (bool), `match_detail` (per-field bool) | `claimed_amount`, `claimed_merchant`, `claimed_date` (from Intake) | **CONSTRUCTED** — Verification cannot check fields it hasn't received; Intake must run first. There is no way to query "the transaction the customer means" without the extracted claim details existing first. |
| **Gate** | `auto_lodge_decision` (bool), `escalation_reason` (nullable string) | `match_result`, `record_found` (from Verification); `claimed_amount`, `dispute_type` (from Intake) | **CONSTRUCTED** — the gate's criteria include the verification outcome, the claim amount, and (as of Review Pass 1's resolution) `dispute_type`, which now actively determines the applicable threshold rather than being a declared-but-unused field. Verification (and, transitively, Intake) must resolve first. |

**Negative check:** no two steps' "consumes" columns are independent of each other — every row after the first references a prior step's output. There is no parallelism to justify here, and none is claimed. This is a strictly linear pipeline: Intake → Verification → Gate.

---

## Component Specification Cards

### Component: Intake

| Field | Value |
|---|---|
| Component name | `intake` |
| Purpose | Classify dispute type and extract structured claim details from the customer's natural-language description. |
| Confirmed basis | Jermyn, Evident Insights, 20 Feb 2025: "understanding customer intent." **CONSTRUCTED**: that extraction of amount/merchant/date is *part of* this function, rather than a separate undisclosed step, is this case study's own resolution of its open PENDING marker (see `docs/DESIGN_DECISIONS.md`, entry 001) — not something Jermyn's quote states directly. |
| Input schema | `raw_text: str` — from the customer, external to the system. |
| Output schema | `dispute_type: enum[unrecognized_charge, unauthorized_transaction, duplicate_charge, other]`, `claimed_amount: float`, `claimed_merchant: str`, `claimed_date: date`, `extraction_confidence: float (0-1)` — confidence is **CONSTRUCTED**, added so a downstream escalation trigger exists for low-confidence extraction; no source confirms CBA's tool exposes a confidence score. |
| Downstream consumers | Verification (needs `claimed_amount`, `claimed_merchant`, `claimed_date`); Gate (needs `dispute_type`, `claimed_amount`). |
| Escalation / failure behavior | Escalates directly to human review (Verification never called) if any of: `extraction_confidence` falls below a **CONSTRUCTED** threshold (0.6); `claimed_amount`, `claimed_merchant`, or `claimed_date` is missing; **or `dispute_type` could not be classified** (added per Review Pass 2's finding, entry 006 — since Gate now risk-tiers its threshold by `dispute_type`, a claim whose type Intake can't determine is exactly the case that tiering can't be applied to, so it's treated as an escalation trigger rather than silently defaulted to a middle tier). |

### Component: Verification

| Field | Value |
|---|---|
| Component name | `verification` |
| Purpose | Check the claimed transaction details against CBA's internal transaction record. |
| Confirmed basis | Jermyn, Evident Insights: "verifying details about the transaction." **CONFIRMED (partial)** — that this function exists is sourced; the specific matching mechanism below is **CONSTRUCTED**. |
| Input schema | `claimed_amount: float`, `claimed_merchant: str`, `claimed_date: date` — all three from Intake's output. |
| Output schema | `record_found: bool`, `match_result: bool`, `match_detail: dict[field, bool]` — `match_detail` is **CONSTRUCTED**, added so Gate's escalation reason can name which field mismatched. |
| Downstream consumers | Gate (needs `record_found`, `match_result`). |
| Escalation / failure behavior | Two distinct fail-fast escalation paths, both bypassing Gate entirely: (1) `incomplete_claim_details` — triggered if `claimed_merchant` or `claimed_date` is `None`, i.e. Verification was called with an incomplete claim (guards against Intake's fail-fast being bypassed; discovered by running `tests/test_intake_verification_dependency.py` — see `docs/DESIGN_DECISIONS.md`, entry 003). (2) `no_matching_transaction_record` — triggered if `record_found` is `False`, i.e. no transaction matching the claimed merchant/date exists in the mock record. In both cases Gate is never called, because there is nothing for Gate to evaluate a match against. If a record *is* found but fields mismatch, `match_result=False` is passed forward to Gate as a normal (not fail-fast) result — Gate, not Verification, owns the auto-lodge-vs-escalate decision. |

### Component: Gate

| Field | Value |
|---|---|
| Component name | `gate` |
| Purpose | Decide auto-lodge vs. escalate to human review, using a risk-tiered threshold that varies by dispute type. |
| Confirmed basis | Evident Insights description of the tool's behavior: dispute "lodged automatically upon satisfaction of the right criteria." **CONFIRMED (partial)** — that a gate exists, and that it applies "criteria" (plural), is sourced. The specific criteria below, including the decision to make the threshold vary by `dispute_type`, are **CONSTRUCTED** and explicitly not CBA's actual logic, which has never been disclosed (Section 6.3). This particular design choice was made against this project's own recommendation for the more conservative alternative (a single flat threshold) — see `docs/DESIGN_DECISIONS.md`, entry 005, for the full reasoning and the record of that disagreement. |
| Input schema | `record_found: bool`, `match_result: bool` (from Verification); `claimed_amount: float`, `dispute_type: str` (from Intake) — `dispute_type` is now an active decision input, not a declared-but-unused field (see entry 005; this closes the finding from Review Pass 1). |
| Output schema | `auto_lodge_decision: bool`, `escalation_reason: str \| None`. |
| Downstream consumers | None — this is the terminal step. Output either auto-lodges the dispute or hands off to the human-review queue with a stated reason. |
| Escalation / failure behavior | Auto-lodge only if `match_result is True` AND `claimed_amount` is under the threshold for the claim's `dispute_type`: `duplicate_charge` → **$750** (CONSTRUCTED — treated as lower fraud-risk; typically a merchant/system billing error rather than a compromised account), `unrecognized_charge` → **$500** (CONSTRUCTED — the baseline/default case), `unauthorized_transaction` → **$250** (CONSTRUCTED — treated as higher fraud-risk; no customer consent claimed, so tighter scrutiny before auto-resolving). The `other`/unclassified → $500 fallback is now a **defensive branch only** — reachable if Gate is called directly (e.g. in a unit test) bypassing the orchestrator, but not reachable via the actual pipeline, since Intake now escalates on an unclassified `dispute_type` before Gate is ever called (entry 006). Otherwise, escalate with an explicit reason: `"unmatched_transaction"` or `"above_auto_lodge_threshold"`. |

---

## Escalation Paths Named (maps to case study Section 4's three named triggers)

1. **Ambiguous input** → Intake low-confidence/missing-field escalation (fail-fast, before Verification runs)
2. **Unmet criteria** → Verification record-not-found escalation (fail-fast, before Gate runs) *and* Gate's `match_result=False` escalation (Gate-owned decision)
3. **High-value threshold** → Gate's `above_auto_lodge_threshold` escalation (threshold now varies by `dispute_type`, per entry 005: $750 / $500 / $250 / $500 fallback — no longer a single flat $500 figure)

Every one of these gets its own test in `tests/` — not just a description in this file.

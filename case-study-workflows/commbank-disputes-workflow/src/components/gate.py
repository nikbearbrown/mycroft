"""
Gate component — CommBank Disputes Workflow (Illustrative Reference Implementation)

WHAT THIS FILE DOES: makes the final call — auto-lodge this dispute, or
send it to a human reviewer? Checks whether Verification found a genuine
match and whether the claimed amount is under the risk threshold for this
kind of dispute. Terminal step in the pipeline; see README.md for the full
workflow.

CONFIRMED (partial) basis: Evident Insights' description of the tool's
behavior — a dispute is "lodged automatically upon satisfaction of the right
criteria." That a gate exists, and applies "criteria" (plural), is sourced.
The specific criteria below — including the decision to risk-tier the
threshold by dispute_type — are CONSTRUCTED and explicitly NOT CBA's actual
logic, which CBA has never disclosed (see case study Section 3.1 and 6.3).

CONSTRUCTED (entry 005): the auto-lodge threshold now varies by dispute_type
rather than being a single flat figure. This was decided against this
project's own recommendation for a flat threshold — see
docs/DESIGN_DECISIONS.md, entry 005, for the full reasoning and the
recorded disagreement.

Requires output from: Verification (record_found, match_result) and Intake
(claimed_amount, dispute_type). This is a real, stated dependency — see
docs/DESIGN_SPECS.md.
"""

from dataclasses import dataclass
from typing import Optional

# [DEV] These thresholds are invented for this illustration. CBA has never
# disclosed a dollar figure, tiered or otherwise — set your own values here
# if adapting this scaffold, and update docs/DESIGN_DECISIONS.md when you do.
# [DEV] Adding a new dispute type? Add its threshold here with the same key
# used in intake.py's DISPUTE_TYPES — otherwise it silently falls through to
# DEFAULT_AUTO_LODGE_THRESHOLD below instead of getting its own tier.
AUTO_LODGE_THRESHOLDS = {
    "duplicate_charge": 750.00,        # lower fraud-risk: typically a billing/system error
    "unrecognized_charge": 500.00,     # baseline/default case
    "unauthorized_transaction": 250.00,  # higher fraud-risk: no customer consent claimed
}
# Defensive-only fallback (entry 006): reachable if Gate is called directly
# with an unclassified dispute_type, bypassing the orchestrator — not
# reachable via the actual pipeline, since Intake now escalates on an
# unclassified dispute_type before Gate is ever called.
DEFAULT_AUTO_LODGE_THRESHOLD = 500.00


@dataclass
class GateResult:
    auto_lodge_decision: bool
    escalation_reason: Optional[str]


def run_gate(record_found: bool, match_result: bool, claimed_amount: float, dispute_type: Optional[str]) -> GateResult:
    """
    Entry point for the Gate component. Terminal step — no downstream consumer.

    Input: record_found, match_result — MUST come from Verification's output.
    claimed_amount, dispute_type — from Intake's output (carried through the
    pipeline). dispute_type now determines which threshold tier applies
    (entry 005).
    """
    if not record_found:
        # Defensive: this path should already have been intercepted by
        # Verification's fail-fast escalation and Gate should not be reached.
        # Included so Gate never silently auto-lodges on malformed input.
        return GateResult(auto_lodge_decision=False, escalation_reason="no_matching_transaction_record")

    if not match_result:
        return GateResult(auto_lodge_decision=False, escalation_reason="unmatched_transaction")

    threshold = AUTO_LODGE_THRESHOLDS.get(dispute_type, DEFAULT_AUTO_LODGE_THRESHOLD)

    if claimed_amount >= threshold:
        return GateResult(auto_lodge_decision=False, escalation_reason="above_auto_lodge_threshold")

    return GateResult(auto_lodge_decision=True, escalation_reason=None)

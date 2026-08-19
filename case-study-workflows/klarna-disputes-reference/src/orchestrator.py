"""
WHAT THIS FILE DOES: Calls Intake, then Verification, then Gate, in strict
sequence — stopping early the moment any stage reports a structural failure.
This is the only file that proves the three stages actually run in a real,
fail-fast order rather than a story-shaped approximation of one. A prose-only
workflow description can claim a sequence without anyone noticing it's wrong;
this file is what a test suite can actually catch a mis-ordering in.

See docs/DESIGN_DECISIONS.md DD-002, DD-004, DD-013.
"""

from . import intake
from . import verification
from . import gate


def handle_query(message: str, customer_id: str) -> dict:
    """
    The single public entrypoint for the whole pipeline.

    No fallback, no retry, no partial-data guessing anywhere in this
    function. If this function ever needs to guess, that's a signal a
    lower-level function returned something ambiguous and needs fixing —
    not a reason to add a guess here.

    Returns a plain dict — illustrative response shape, adapt it to whatever
    your own API contract actually needs to look like. [DEV]
    """
    intake_result = intake.run_intake(message)

    # Stop #1: Intake couldn't classify the message at all. Gate is never
    # invoked — "unclassified" belongs to the orchestrator, not to Gate.
    if intake_result.status == "escalate_unclassified":
        return {"resolved": False, "escalated": True, "reason": "unclassified"}

    verification_result = verification.run_verification(intake_result, customer_id)

    # Stop #2a: no record found for this customer at all.
    if verification_result.status == "escalate_no_record":
        return {"resolved": False, "escalated": True, "reason": "no_record"}

    # Stop #2b: record exists, but the claim was missing the field this
    # dispute type actually needs to check.
    if verification_result.status == "escalate_incomplete_claim":
        return {"resolved": False, "escalated": True, "reason": "incomplete_claim"}

    # Only if both checks passed does Gate get invoked. verification_result.status
    # is guaranteed to be "match" or "mismatch" here — exactly what gate.evaluate()
    # requires.
    gate_decision = gate.evaluate(verification_result, intake_result)

    return {
        "resolved": gate_decision.outcome == "resolved",
        "escalated": gate_decision.outcome == "escalated",
        "reason": gate_decision.reason,
    }

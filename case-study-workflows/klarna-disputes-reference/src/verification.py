"""
WHAT THIS FILE DOES: Looks up a customer's account record and checks whether
their claim (a date or an amount, depending on dispute type) actually matches
what's on file. This is the constructed stand-in for Klarna's confirmed
function of providing "real-time balance and payment-schedule updates" —
Klarna confirms the DATA exists; it confirms nothing about matching logic,
tolerance, or failure handling. All of that is invented here, on purpose,
and labeled as such.

See docs/DESIGN_DECISIONS.md DD-002, DD-004, DD-007, DD-008, DD-009, DD-013.
"""

from dataclasses import dataclass
from typing import Optional
import json
import os

from .intake import IntakeResult


# [DEV] Path to the mock data file. A real system would replace lookup_record
# entirely with a call to an actual account database — this constant is the
# seam where that swap happens.
_MOCK_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "mock_data", "transactions.json"
)

# Which claim field actually matters for each in-scope dispute type.
# late_fee_dispute is a date question; refund_request is an amount question —
# they are NOT the same kind of claim, and comparing both uniformly for both
# types was considered and rejected (DD-007) because it would make
# refund_request nearly impossible to complete: customers disputing a refund
# amount don't usually mention a date.
REQUIRED_FIELD_BY_DISPUTE_TYPE = {
    "late_fee_dispute": "claimed_date",
    "refund_request": "claimed_amount",
}


@dataclass
class VerificationResult:
    """
    status:          "match" | "mismatch" | "escalate_no_record" |
                      "escalate_incomplete_claim" — the ONE field Gate and
                      the orchestrator dispatch on.
    mismatch_reason: None | "claim_mismatch" | "processing_delay_noted".
                      Only ever populated when status == "mismatch".
                      "processing_delay_noted" is only reachable for
                      late_fee_dispute — a record's delay flag describes a
                      payment posting late, which has no equivalent meaning
                      for a refund-amount question (DD-008).
    """
    status: str
    mismatch_reason: Optional[str]


def lookup_record(customer_id: str) -> Optional[dict]:
    """
    Reads the fabricated mock dataset. Returns the record dict, or None if
    the customer_id isn't in the file — a normal, expected outcome, not an
    error. This must never raise on a missing customer; the whole point of
    this function returning None cleanly is so run_verification can fail
    fast and gracefully instead of crashing (the exact bug class a prior
    build in this series actually hit).
    """
    with open(_MOCK_DATA_PATH) as f:
        data = json.load(f)
    return data["records"].get(customer_id)


def compare_claim_to_record(claim_value, record: dict, dispute_type: str) -> VerificationResult:
    """
    Exact-match comparison only — Klarna discloses no tolerance, so none is
    assumed. [DEV] A real system would very likely need a grace window here;
    this doesn't have one on purpose, so that omission is visible rather than
    silently baked in.

    claim_value is whichever field is relevant for this dispute_type — the
    caller (run_verification) is responsible for picking the right one
    before calling this function. This function doesn't know which raw field
    it came from; it only knows what it's comparing against.
    """
    if dispute_type == "late_fee_dispute":
        record_value = record["payment_date"]
        if claim_value == record_value:
            return VerificationResult(status="match", mismatch_reason=None)

        # Mismatch. Whether it's "ambiguous_delay" or a plain "claim_mismatch"
        # depends entirely on whether the record itself flags a delay reason.
        if record.get("delay_reason"):
            return VerificationResult(status="mismatch", mismatch_reason="processing_delay_noted")
        return VerificationResult(status="mismatch", mismatch_reason="claim_mismatch")

    if dispute_type == "refund_request":
        record_value = record["amount_paid"]
        if claim_value == record_value:
            return VerificationResult(status="match", mismatch_reason=None)

        # No equivalent to "ambiguous_delay" here — refund_request can only
        # ever reach "claim_mismatch" on a mismatch (DD-008).
        return VerificationResult(status="mismatch", mismatch_reason="claim_mismatch")

    # Should be unreachable — Intake never produces a dispute_type outside
    # the two handled above once status == "ok". Fail loudly if it happens;
    # silently guessing here would hide a real upstream bug.
    raise ValueError(f"compare_claim_to_record got an unhandled dispute_type: {dispute_type!r}")


def run_verification(intake_result: IntakeResult, customer_id: str) -> VerificationResult:
    """
    The single public entrypoint. Order matters and is locked (DD-013):

      1. Look up the record FIRST, before checking claim completeness.
      2. Only if a record exists, check whether the relevant claim field
         is present.
      3. Only if both pass, actually compare.

    This order was reversed from an earlier draft that checked completeness
    first purely because it's cheaper (no I/O). That was deliberately
    changed: an unrecognized customer is a more serious finding than an
    incompletely-worded message, and that priority is worth one avoidable
    lookup call on cases that turn out incomplete anyway.
    """
    record = lookup_record(customer_id)
    if record is None:
        return VerificationResult(status="escalate_no_record", mismatch_reason=None)

    required_field = REQUIRED_FIELD_BY_DISPUTE_TYPE[intake_result.dispute_type]
    claim_value = getattr(intake_result, required_field)

    if claim_value is None:
        return VerificationResult(status="escalate_incomplete_claim", mismatch_reason=None)

    return compare_claim_to_record(claim_value, record, intake_result.dispute_type)

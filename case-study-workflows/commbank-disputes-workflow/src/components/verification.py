"""
Verification component — CommBank Disputes Workflow (Illustrative Reference Implementation)

WHAT THIS FILE DOES: takes the claim details Intake extracted and checks
them against the bank's internal transaction record — does a transaction
matching this merchant/date even exist, and if so, does the claimed amount
match it? Second step in the pipeline; see README.md for the full workflow.

CONFIRMED (partial) basis: Dan Jermyn, Evident Insights, 20 Feb 2025 —
"verifying details about the transaction." That this function exists is
sourced. The specific matching mechanism, tolerance, and output shape below
are CONSTRUCTED — no source describes them.

Requires output from: Intake (claimed_amount, claimed_merchant, claimed_date).
This is a real, stated dependency, not narrative convenience — see
docs/DESIGN_SPECS.md, Dependency-Mapping Worksheet.
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Optional

from src.mock_data.transactions import find_transaction


@dataclass
class VerificationResult:
    record_found: bool
    match_result: bool
    match_detail: Dict[str, bool]
    escalate: bool
    escalation_reason: Optional[str]


def run_verification(claimed_amount: float, claimed_merchant: str, claimed_date: date) -> VerificationResult:
    """
    Entry point for the Verification component.

    Input: claimed_amount, claimed_merchant, claimed_date — MUST come from
    Intake's output. This function cannot run meaningfully without them,
    which is the entire reason the Intake -> Verification dependency in the
    worksheet is marked CONSTRUCTED rather than assumed.
    """
    # Defensive guard: if Intake's fail-fast path was somehow bypassed and
    # this component is called with an incomplete claim, it must escalate
    # gracefully rather than raise — an unhandled exception is not the
    # documented behavior in docs/DESIGN_SPECS.md. Discovered by running
    # tests/test_intake_verification_dependency.py; see docs/DESIGN_DECISIONS.md.
    if claimed_merchant is None or claimed_date is None:
        return VerificationResult(
            record_found=False,
            match_result=False,
            match_detail={},
            escalate=True,
            escalation_reason="incomplete_claim_details",
        )

    # [DEV] Replace find_transaction with a real core-banking API call when
    # adapting this scaffold for an actual integration.
    record = find_transaction(claimed_merchant, claimed_date)

    if record is None:
        # Fail-fast: nothing to compare the claimed amount against. Gate is
        # never called in this path — see docs/DESIGN_SPECS.md.
        return VerificationResult(
            record_found=False,
            match_result=False,
            match_detail={},
            escalate=True,
            escalation_reason="no_matching_transaction_record",
        )

    amount_matches = abs(record["amount"] - claimed_amount) < 0.01
    match_detail = {"amount": amount_matches, "merchant": True, "date": True}
    match_result = all(match_detail.values())

    # Not a fail-fast case: a mismatched-but-found record is a normal result
    # passed forward. Gate, not Verification, decides what happens next.
    return VerificationResult(
        record_found=True,
        match_result=match_result,
        match_detail=match_detail,
        escalate=False,
        escalation_reason=None,
    )

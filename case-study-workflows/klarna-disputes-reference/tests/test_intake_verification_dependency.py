"""
WHAT THIS FILE DOES: Proves Verification cannot be called meaningfully
without complete Intake output, and specifically proves it fails
GRACEFULLY (returns escalate_incomplete_claim) rather than crashing when
the field this dispute type actually needs is missing.

This is the single most likely bug class in this repo — a prior build in
this series hit exactly this shape of bug (Verification crashing on a
missing field instead of handling it).

NOTE: every case below uses customer_id="cust_001", a record that DOES
exist in the mock data. This is required, not incidental — DD-013 locked
record lookup to happen BEFORE the completeness check, so a test using an
unregistered customer_id here would get escalate_no_record instead of
escalate_incomplete_claim, and silently prove the wrong thing.
"""

from src.intake import IntakeResult
from src.verification import run_verification, VerificationResult


VALID_CUSTOMER = "cust_001"  # exists in mock_data/transactions.json


def test_missing_both_fields_escalates_incomplete_claim_not_a_crash():
    intake_result = IntakeResult(
        status="ok",
        dispute_type="late_fee_dispute",
        confidence=0.9,
        claimed_date=None,
        claimed_amount=None,
    )

    result = run_verification(intake_result, VALID_CUSTOMER)

    assert isinstance(result, VerificationResult)
    assert result.status == "escalate_incomplete_claim"


def test_refund_request_missing_its_relevant_field_amount():
    # claimed_date is present, but refund_request cares about claimed_amount,
    # not claimed_date. This is the direct test of the field-relevance fix:
    # having an irrelevant field present must NOT rescue this from
    # incomplete_claim.
    intake_result = IntakeResult(
        status="ok",
        dispute_type="refund_request",
        confidence=0.9,
        claimed_date="2024-03-01",
        claimed_amount=None,
    )

    result = run_verification(intake_result, VALID_CUSTOMER)

    assert result.status == "escalate_incomplete_claim"


def test_late_fee_dispute_missing_its_relevant_field_date():
    # Mirror image of the test above: claimed_amount is present, but
    # late_fee_dispute cares about claimed_date, not claimed_amount.
    intake_result = IntakeResult(
        status="ok",
        dispute_type="late_fee_dispute",
        confidence=0.9,
        claimed_date=None,
        claimed_amount=50.00,
    )

    result = run_verification(intake_result, VALID_CUSTOMER)

    assert result.status == "escalate_incomplete_claim"


def test_complete_relevant_claim_proceeds_past_the_completeness_check():
    # Positive control: proves the completeness check doesn't fire when it
    # shouldn't. cust_001's on-file payment_date is "2024-02-28" — an exact
    # match, so this should reach a real "match", not "escalate_incomplete_claim".
    intake_result = IntakeResult(
        status="ok",
        dispute_type="late_fee_dispute",
        confidence=0.9,
        claimed_date="2024-02-28",
        claimed_amount=None,
    )

    result = run_verification(intake_result, VALID_CUSTOMER)

    assert result.status == "match"

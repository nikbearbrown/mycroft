"""
Dependency test — proves Intake -> Verification is a real dependency, not
an assumed one: run the downstream step with the upstream step's output
deliberately withheld or malformed, confirm documented behavior.
"""

from src.components.verification import run_verification


def test_verification_fails_gracefully_with_missing_merchant():
    # Malformed input: merchant is None, as if Intake had never run or had
    # failed to extract it. Verification must not silently succeed.
    result = run_verification(claimed_amount=340.00, claimed_merchant=None, claimed_date=None)
    assert result.record_found is False
    assert result.escalate is True
    assert result.escalation_reason == "incomplete_claim_details"


def test_verification_uses_intake_fields_correctly_when_present():
    # Correct usage: fields as Intake would actually produce them.
    from datetime import date
    result = run_verification(claimed_amount=340.00, claimed_merchant="Amazon", claimed_date=date(2026, 6, 12))
    assert result.record_found is True
    assert result.match_result is True

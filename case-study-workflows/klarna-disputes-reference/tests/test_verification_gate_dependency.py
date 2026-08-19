"""
WHAT THIS FILE DOES: Proves Gate refuses to be tricked into evaluating a
VerificationResult it was never designed to handle (raises on structural
statuses), and proves Gate's mismatch-before-confidence precedence actually
holds in code, not just on paper (DD-012).
"""

import pytest

from src.verification import VerificationResult
from src.intake import IntakeResult
from src.gate import evaluate, GateDecision


def _intake(confidence: float) -> IntakeResult:
    # Only confidence matters for these tests; other fields are filled in
    # with plausible values so the dataclass is valid.
    return IntakeResult(
        status="ok",
        dispute_type="late_fee_dispute",
        confidence=confidence,
        claimed_date="2024-03-01",
        claimed_amount=None,
    )


def test_gate_raises_on_escalate_no_record():
    # Contract violation: Gate should never see this status. It belongs to
    # the orchestrator. Raising here is the correct behavior, not a bug.
    bad_verification = VerificationResult(status="escalate_no_record", mismatch_reason=None)

    with pytest.raises(ValueError):
        evaluate(bad_verification, _intake(confidence=0.9))


def test_gate_raises_on_escalate_incomplete_claim():
    bad_verification = VerificationResult(status="escalate_incomplete_claim", mismatch_reason=None)

    with pytest.raises(ValueError):
        evaluate(bad_verification, _intake(confidence=0.9))


def test_mismatch_escalates_regardless_of_high_confidence():
    # The core precedence test: even with high confidence, a mismatch always
    # escalates on "mismatch" — confidence never overrides a record disagreement.
    verification = VerificationResult(status="mismatch", mismatch_reason="claim_mismatch")

    decision = evaluate(verification, _intake(confidence=0.95))

    assert decision.outcome == "escalated"
    assert decision.reason == "mismatch"


def test_ambiguous_delay_reason_surfaces_correctly():
    verification = VerificationResult(status="mismatch", mismatch_reason="processing_delay_noted")

    decision = evaluate(verification, _intake(confidence=0.95))

    assert decision.outcome == "escalated"
    assert decision.reason == "ambiguous_delay"


def test_match_with_high_confidence_resolves():
    verification = VerificationResult(status="match", mismatch_reason=None)

    decision = evaluate(verification, _intake(confidence=0.9))

    assert decision == GateDecision(outcome="resolved", reason=None)


def test_match_with_low_confidence_escalates():
    verification = VerificationResult(status="match", mismatch_reason=None)

    decision = evaluate(verification, _intake(confidence=0.5))

    assert decision.outcome == "escalated"
    assert decision.reason == "low_confidence"

"""
Fail-fast test — confirms the pipeline actually stops rather than
continuing to call downstream steps with unusable data.
"""

from src.orchestrator import run_pipeline


def test_pipeline_stops_at_intake_on_ambiguous_input():
    # Text with no extractable merchant, amount, or date at all.
    result = run_pipeline("Something seems off with my account, not sure what.")
    assert result.stage_reached == "intake"
    assert result.verification_result is None
    assert result.gate_result is None
    assert result.escalation_reason == "ambiguous_input_low_extraction_confidence"


def test_pipeline_stops_at_verification_when_no_record_exists():
    # Well-formed input, but the merchant/date pair doesn't exist in mock data.
    result = run_pipeline(
        "I don't recognize a $99 charge from JB Hi-Fi on 2026-01-01."
    )
    assert result.stage_reached == "verification"
    assert result.gate_result is None
    assert result.escalation_reason == "no_matching_transaction_record"

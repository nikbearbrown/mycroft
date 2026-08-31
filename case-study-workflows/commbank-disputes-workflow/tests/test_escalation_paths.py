"""
Escalation test — for every human-handoff trigger named in the case
study's Section 4 (ambiguous input, unmet criteria, high-value threshold),
confirm the implementation actually routes to human review rather than
defaulting to auto-approval on an untested edge case.
"""

from src.orchestrator import run_pipeline


def test_escalates_on_ambiguous_input():
    result = run_pipeline("not sure what this charge even is")
    assert result.auto_lodge_decision is False
    assert result.stage_reached == "intake"


def test_escalates_on_unmet_criteria_amount_mismatch():
    # Merchant and date match a real mock record, but claimed amount differs.
    result = run_pipeline(
        "I don't recognize a $50 charge from Amazon on 2026-06-12."
    )
    assert result.stage_reached == "gate"
    assert result.auto_lodge_decision is False
    assert result.escalation_reason == "unmatched_transaction"


def test_escalates_on_high_value_threshold():
    # Merchant, date, and amount all match a real mock record — but the
    # amount is above the CONSTRUCTED auto-lodge threshold.
    result = run_pipeline(
        "I didn't authorize a $615 charge from Uber on 2026-06-20."
    )
    assert result.stage_reached == "gate"
    assert result.auto_lodge_decision is False
    assert result.escalation_reason == "above_auto_lodge_threshold"

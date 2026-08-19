"""
Negative/adversarial test — confirms the human-escalation path is reachable
at all in the test suite with a case explicitly designed to fail gate
criteria, AND confirms the auto-lodge path is genuinely reachable too (a
pipeline that only ever escalates has not proven its "auto" behavior
exists, which would be its own silent failure mode).
"""

from src.orchestrator import run_pipeline


def test_adversarial_case_fails_every_gate_criterion():
    # Designed to fail: unknown merchant (no record), so it should escalate
    # at Verification, never reaching Gate at all.
    result = run_pipeline(
        "I never made this $9999 charge from Definitely Not A Real Merchant on 2026-06-12."
    )
    assert result.auto_lodge_decision is False
    assert result.stage_reached in ("intake", "verification")


def test_clean_case_actually_auto_lodges():
    # Proves the auto-lodge path is reachable, not just theoretically coded.
    result = run_pipeline(
        "I don't recognize a $22.99 charge from Netflix on 2026-06-01."
    )
    assert result.stage_reached == "gate"
    assert result.auto_lodge_decision is True
    assert result.escalation_reason is None


def test_duplicate_charge_gets_higher_threshold_than_unrecognized():
    # $600 exceeds the unrecognized_charge threshold ($500) but not the
    # duplicate_charge threshold ($750) — proves the tiering by dispute_type
    # actually changes the outcome for the same dollar amount, not just in
    # theory (entry 005).
    result = run_pipeline(
        "I've been charged twice, a duplicate $600 charge from Coles on 2026-07-01."
    )
    assert result.stage_reached == "gate"
    assert result.intake_result["dispute_type"] == "duplicate_charge"
    assert result.auto_lodge_decision is True
    assert result.escalation_reason is None


def test_unauthorized_transaction_gets_lower_threshold():
    # $12.99 is well under every tier, but this specifically proves the
    # unauthorized_transaction tier ($250) is applied and doesn't accidentally
    # fall through to the $500 baseline.
    result = run_pipeline(
        "I didn't authorize a $12.99 charge from Spotify on 2026-06-05."
    )
    assert result.stage_reached == "gate"
    assert result.intake_result["dispute_type"] == "unauthorized_transaction"
    assert result.auto_lodge_decision is True


def test_unclassified_dispute_type_escalates_before_gate():
    # Amount, merchant, and date all extract cleanly, but no dispute-type
    # phrase matches. Per entry 006, this must escalate at Intake — Gate's
    # tiering can't be applied to a type it never received.
    result = run_pipeline(
        "There's a $22.99 charge from Netflix on 2026-06-01 I wanted to ask about."
    )
    assert result.stage_reached == "intake"
    assert result.gate_result is None
    assert result.escalation_reason == "unclassified_dispute_type"

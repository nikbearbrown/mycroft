"""
Dependency test — proves Verification -> Gate is a real dependency: run
Gate with Verification's output withheld/malformed.
"""

from src.components.gate import run_gate


def test_gate_does_not_auto_lodge_when_record_not_found():
    # Malformed/withheld input: record_found=False, as if Verification's
    # fail-fast path had been bypassed. Gate must still refuse to auto-lodge.
    result = run_gate(record_found=False, match_result=False, claimed_amount=50.00, dispute_type="unrecognized_charge")
    assert result.auto_lodge_decision is False
    assert result.escalation_reason == "no_matching_transaction_record"


def test_gate_respects_match_result_from_verification():
    result = run_gate(record_found=True, match_result=False, claimed_amount=50.00, dispute_type="unrecognized_charge")
    assert result.auto_lodge_decision is False
    assert result.escalation_reason == "unmatched_transaction"

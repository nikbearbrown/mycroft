"""
WHAT THIS FILE DOES: tests orchestrator.py's halt-map sequencing. Following the
blueprint's mock/spy-assertion pattern, these tests prove that downstream stages
are never called once an earlier stage halts -- not just that the final result
looks right. A clean end-to-end happy-path test proves the success path also
actually works, not just the escalation paths.
"""

import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import orchestrator


def _complete_request(client_id="CLIENT-001"):
    return {
        "client_id": client_id,
        "facility_type": "trade_finance",
        "requested_action": "expand_facility",
    }


# --- Test 1: incomplete intake halts before client lookup / draft synthesis ---

def test_incomplete_intake_halts_before_client_lookup():
    incomplete_request = {"client_id": "CLIENT-001"}  # missing two fields

    with patch("orchestrator.mock_data.get_client_record") as spy_lookup, \
         patch("orchestrator.synthesize_draft") as spy_synthesis:
        result = orchestrator.run(
            incomplete_request, decision_function=lambda d: "cleared_for_finalization"
        )

    assert result["halted"] is True
    assert result["halt_stage"] == "intake"
    spy_lookup.assert_not_called()
    spy_synthesis.assert_not_called()


# --- Test 2a: client not found halts before draft synthesis ---

def test_client_not_found_halts_before_draft_synthesis():
    request = _complete_request(client_id="CLIENT-DOES-NOT-EXIST")

    with patch("orchestrator.synthesize_draft") as spy_synthesis:
        result = orchestrator.run(
            request, decision_function=lambda d: "cleared_for_finalization"
        )

    assert result["halted"] is True
    assert result["halt_stage"] == "client_lookup"
    spy_synthesis.assert_not_called()


# --- Test 2b: draft synthesis gap halts before human review ---

def test_gap_flagged_synthesis_halts_before_human_review():
    request = _complete_request(client_id="CLIENT-003")  # incomplete mock record

    with patch("orchestrator.HumanReviewGate") as spy_gate_class:
        result = orchestrator.run(
            request, decision_function=lambda d: "cleared_for_finalization"
        )

    assert result["halted"] is True
    assert result["halt_stage"] == "draft_synthesis"
    spy_gate_class.assert_not_called()


# --- Test 3: gate returns not_cleared halts before finalize/submit ---

def test_not_cleared_outcome_halts_before_finalize():
    request = _complete_request(client_id="CLIENT-001")

    with patch("orchestrator.finalize") as spy_finalize:
        result = orchestrator.run(
            request, decision_function=lambda d: "not_cleared_for_finalization"
        )

    assert result["halted"] is True
    assert result["halt_stage"] == "human_review_gate"
    spy_finalize.assert_not_called()


# --- Test 4: gate's invalid return value propagates as an exception, not a silent pass ---

def test_invalid_gate_return_value_raises_instead_of_proceeding():
    request = _complete_request(client_id="CLIENT-001")

    with patch("orchestrator.finalize") as spy_finalize:
        try:
            orchestrator.run(request, decision_function=lambda d: "maybe")
            assert False, "Expected ValueError, none was raised"
        except ValueError:
            pass
        spy_finalize.assert_not_called()


# --- Test 5: clean, complete case runs end-to-end to a human-cleared finalize state ---

def test_happy_path_runs_end_to_end_to_finalize():
    request = _complete_request(client_id="CLIENT-001")

    result = orchestrator.run(
        request, decision_function=lambda d: "cleared_for_finalization"
    )

    assert result["halted"] is False
    assert result["halt_stage"] is None
    assert result["finalize_result"]["status"] == "handoff_attempted"
    assert result["finalize_result"]["client_id"] == "CLIENT-001"


# --- Missing decision_function still fails at gate construction, not silently ---

def test_missing_decision_function_raises_at_gate_construction():
    request = _complete_request(client_id="CLIENT-001")

    try:
        orchestrator.run(request, decision_function=None)
        assert False, "Expected TypeError, none was raised"
    except TypeError:
        pass


if __name__ == "__main__":
    test_incomplete_intake_halts_before_client_lookup()
    test_client_not_found_halts_before_draft_synthesis()
    test_gap_flagged_synthesis_halts_before_human_review()
    test_not_cleared_outcome_halts_before_finalize()
    test_invalid_gate_return_value_raises_instead_of_proceeding()
    test_happy_path_runs_end_to_end_to_finalize()
    test_missing_decision_function_raises_at_gate_construction()
    print("orchestrator.py: all tests passed")

"""
WHAT THIS FILE DOES: tests human_review_gate.py's contract — not any business
rule about what should be approved, which is deliberately untestable here since
this gate has no built-in approval logic to test.

Per the original spec's Test #4: these tests confirm the gate honors whatever
its supplied decision_function returns, and confirm the two distinct failure
modes (no function supplied at all; function returns something unrecognized).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from human_review_gate import HumanReviewGate


def test_gate_honors_cleared_outcome():
    gate = HumanReviewGate(lambda draft: "cleared_for_finalization")
    result = gate.review({"client_id": "CLIENT-001"})
    assert result == "cleared_for_finalization"


def test_gate_honors_not_cleared_outcome():
    gate = HumanReviewGate(lambda draft: "not_cleared_for_finalization")
    result = gate.review({"client_id": "CLIENT-001"})
    assert result == "not_cleared_for_finalization"


def test_gate_passes_draft_through_to_decision_function():
    received = {}

    def spy_decision_function(draft):
        received.update(draft)
        return "cleared_for_finalization"

    gate = HumanReviewGate(spy_decision_function)
    gate.review({"client_id": "CLIENT-002", "note": "check tenure"})
    assert received == {"client_id": "CLIENT-002", "note": "check tenure"}


def test_construction_without_decision_function_raises_type_error():
    try:
        HumanReviewGate(None)
        assert False, "Expected TypeError, none was raised"
    except TypeError:
        pass


def test_construction_with_non_callable_raises_type_error():
    try:
        HumanReviewGate("not_a_function")
        assert False, "Expected TypeError, none was raised"
    except TypeError:
        pass


def test_invalid_return_value_raises_value_error():
    gate = HumanReviewGate(lambda draft: "approved")  # not a recognized outcome
    try:
        gate.review({"client_id": "CLIENT-001"})
        assert False, "Expected ValueError, none was raised"
    except ValueError:
        pass


def test_none_return_value_raises_value_error():
    gate = HumanReviewGate(lambda draft: None)
    try:
        gate.review({"client_id": "CLIENT-001"})
        assert False, "Expected ValueError, none was raised"
    except ValueError:
        pass


if __name__ == "__main__":
    test_gate_honors_cleared_outcome()
    test_gate_honors_not_cleared_outcome()
    test_gate_passes_draft_through_to_decision_function()
    test_construction_without_decision_function_raises_type_error()
    test_construction_with_non_callable_raises_type_error()
    test_invalid_return_value_raises_value_error()
    test_none_return_value_raises_value_error()
    print("human_review_gate.py: all tests passed")

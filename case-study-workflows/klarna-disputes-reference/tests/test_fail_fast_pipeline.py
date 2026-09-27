"""
WHAT THIS FILE DOES: Proves the orchestrator's fail-fast sequencing actually
happens in code, not just in the diagram. Uses a mock on gate.evaluate so
each test can assert whether Gate was invoked at all — this is what actually
proves "fail-fast," not just that the right dict came back at the end.
"""

from unittest.mock import patch

from src.orchestrator import handle_query


KNOWN_CUSTOMER = "cust_001"   # exists in mock data
UNKNOWN_CUSTOMER = "cust_999"  # deliberately does not exist


def test_unclassified_message_stops_before_gate():
    with patch("src.gate.evaluate") as mock_gate:
        result = handle_query("asdkjh random gibberish text with no keywords", KNOWN_CUSTOMER)

    assert result == {"resolved": False, "escalated": True, "reason": "unclassified"}
    mock_gate.assert_not_called()


def test_unknown_customer_stops_before_gate():
    message = "I was charged a late fee but I paid on time on 2024-02-28."

    with patch("src.gate.evaluate") as mock_gate:
        result = handle_query(message, UNKNOWN_CUSTOMER)

    assert result == {"resolved": False, "escalated": True, "reason": "no_record"}
    mock_gate.assert_not_called()


def test_incomplete_claim_stops_before_gate():
    # Classifiable as late_fee_dispute, but no date anywhere in the message —
    # the relevant field for this dispute type is missing.
    message = "I was charged a late fee but I paid on time."

    with patch("src.gate.evaluate") as mock_gate:
        result = handle_query(message, KNOWN_CUSTOMER)

    assert result == {"resolved": False, "escalated": True, "reason": "incomplete_claim"}
    mock_gate.assert_not_called()


def test_complete_valid_case_does_reach_gate():
    # Positive control: proves the pipeline doesn't over-fire the fail-fast
    # checks. This message + customer combination is complete and valid, so
    # Gate should be invoked exactly once.
    message = "I was charged a late fee but I paid on time on 2024-02-28."

    with patch("src.gate.evaluate", wraps=None) as mock_gate:
        mock_gate.return_value.outcome = "resolved"
        mock_gate.return_value.reason = None
        handle_query(message, KNOWN_CUSTOMER)

    mock_gate.assert_called_once()

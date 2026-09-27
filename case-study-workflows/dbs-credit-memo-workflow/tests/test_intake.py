"""
WHAT THIS FILE DOES: tests intake.py's validation logic — complete requests,
requests missing one field, requests missing multiple fields, and requests
where a required field is present but empty (which should count as missing).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intake import validate_intake


def test_complete_request_returns_complete_status():
    request = {
        "client_id": "CLIENT-001",
        "facility_type": "trade_finance",
        "requested_action": "expand_facility",
    }
    result = validate_intake(request)
    assert result["status"] == "complete"
    assert result["missing_fields"] == []
    assert result["request"] == request


def test_missing_one_field_returns_incomplete_with_that_field_named():
    request = {
        "client_id": "CLIENT-001",
        "facility_type": "trade_finance",
        # requested_action omitted
    }
    result = validate_intake(request)
    assert result["status"] == "incomplete"
    assert result["missing_fields"] == ["requested_action"]


def test_missing_multiple_fields_returns_all_of_them():
    request = {"client_id": "CLIENT-001"}
    result = validate_intake(request)
    assert result["status"] == "incomplete"
    assert set(result["missing_fields"]) == {"facility_type", "requested_action"}


def test_empty_string_field_counts_as_missing():
    request = {
        "client_id": "CLIENT-001",
        "facility_type": "",
        "requested_action": "expand_facility",
    }
    result = validate_intake(request)
    assert result["status"] == "incomplete"
    assert result["missing_fields"] == ["facility_type"]


def test_none_value_field_counts_as_missing():
    request = {
        "client_id": "CLIENT-001",
        "facility_type": "trade_finance",
        "requested_action": None,
    }
    result = validate_intake(request)
    assert result["status"] == "incomplete"
    assert result["missing_fields"] == ["requested_action"]


if __name__ == "__main__":
    test_complete_request_returns_complete_status()
    test_missing_one_field_returns_incomplete_with_that_field_named()
    test_missing_multiple_fields_returns_all_of_them()
    test_empty_string_field_counts_as_missing()
    test_none_value_field_counts_as_missing()
    print("intake.py: all tests passed")

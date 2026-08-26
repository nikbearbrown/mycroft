"""
WHAT THIS FILE DOES: tests mock_data.py's lookup behavior — found, not-found, and
the deliberately-incomplete record used elsewhere to exercise the gap-flagged path.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mock_data import get_client_record


def test_known_client_returns_record():
    record = get_client_record("CLIENT-001")
    assert record is not None
    assert record["client_id"] == "CLIENT-001"
    assert record["client_name"] == "Aurora Freight Holdings"


def test_unknown_client_returns_none():
    record = get_client_record("CLIENT-DOES-NOT-EXIST")
    assert record is None


def test_incomplete_record_is_available_for_gap_flagged_path():
    record = get_client_record("CLIENT-003")
    assert record is not None
    assert record["credit_rating"] is None


if __name__ == "__main__":
    test_known_client_returns_record()
    test_unknown_client_returns_none()
    test_incomplete_record_is_available_for_gap_flagged_path()
    print("mock_data.py: all tests passed")

"""
WHAT THIS FILE DOES: tests draft_synthesis.py's two outcomes — a complete draft
from a fully-populated record, and a gap-flagged result from an incomplete one
(exercised via injected dicts, not via mock_data.py, per Design Decision 6).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from draft_synthesis import synthesize_draft


def _complete_record():
    return {
        "client_id": "CLIENT-001",
        "client_name": "Aurora Freight Holdings",
        "existing_facility_type": "trade_finance",
        "existing_facility_limit": 12_000_000,
        "requested_facility_limit": 18_000_000,
        "credit_rating": "BBB+",
        "relationship_tenure_years": 7,
    }


def test_complete_record_returns_complete_draft():
    result = synthesize_draft(_complete_record())
    assert result["status"] == "complete"
    assert result["gap_reason"] is None
    assert result["draft"]["client_id"] == "CLIENT-001"
    assert result["draft"]["requested_limit"] == 18_000_000
    assert "Aurora Freight Holdings" in result["draft"]["memo_summary"]


def test_missing_credit_rating_returns_gap_flagged():
    record = _complete_record()
    record["credit_rating"] = None
    result = synthesize_draft(record)
    assert result["status"] == "gap_flagged"
    assert result["draft"] is None
    assert "credit_rating" in result["gap_reason"]


def test_missing_multiple_fields_lists_all_of_them():
    record = _complete_record()
    del record["existing_facility_limit"]
    record["credit_rating"] = None
    result = synthesize_draft(record)
    assert result["status"] == "gap_flagged"
    assert "existing_facility_limit" in result["gap_reason"]
    assert "credit_rating" in result["gap_reason"]


def test_function_does_not_call_mock_data_directly():
    # Purity check: this function should work with a plain dict that never
    # touched mock_data.py, proving it has no hidden lookup of its own.
    plain_dict = {
        "client_id": "NOT-IN-MOCK-DATA-AT-ALL",
        "client_name": "Ad Hoc Test Corp",
        "existing_facility_type": "working_capital",
        "existing_facility_limit": 1,
        "requested_facility_limit": 2,
        "credit_rating": "BB",
    }
    result = synthesize_draft(plain_dict)
    assert result["status"] == "complete"


if __name__ == "__main__":
    test_complete_record_returns_complete_draft()
    test_missing_credit_rating_returns_gap_flagged()
    test_missing_multiple_fields_lists_all_of_them()
    test_function_does_not_call_mock_data_directly()
    print("draft_synthesis.py: all tests passed")

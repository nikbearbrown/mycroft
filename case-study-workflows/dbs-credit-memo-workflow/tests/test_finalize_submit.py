"""
WHAT THIS FILE DOES: tests finalize_submit.py's stub return contract — proving
it produces an observable terminal state, not that it does anything real.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from finalize_submit import finalize


def test_finalize_returns_handoff_attempted_status():
    draft = {"client_id": "CLIENT-001", "memo_summary": "some draft"}
    result = finalize(draft)
    assert result["status"] == "handoff_attempted"


def test_finalize_echoes_client_id():
    draft = {"client_id": "CLIENT-002", "memo_summary": "some other draft"}
    result = finalize(draft)
    assert result["client_id"] == "CLIENT-002"
    assert "CLIENT-002" in result["memo_reference"]


if __name__ == "__main__":
    test_finalize_returns_handoff_attempted_status()
    test_finalize_echoes_client_id()
    print("finalize_submit.py: all tests passed")

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from assistant.synthesis import synthesize


def test_synthesize_produces_draft_from_matches():
    matches = [
        {"doc_id": "DOC-001", "snippet": "Semiconductor capex is moderating."},
        {"doc_id": "DOC-002", "snippet": "Bank margins have stabilized."},
    ]
    result = synthesize(matches)
    assert "Semiconductor capex is moderating." in result.draft_answer
    assert "Bank margins have stabilized." in result.draft_answer
    assert result.sources_used == ["DOC-001", "DOC-002"]


def test_synthesize_empty_matches_returns_empty_result():
    result = synthesize([])
    assert result.draft_answer == ""
    assert result.sources_used == []


if __name__ == "__main__":
    test_synthesize_produces_draft_from_matches()
    test_synthesize_empty_matches_returns_empty_result()
    print("test_synthesis.py: all tests passed")

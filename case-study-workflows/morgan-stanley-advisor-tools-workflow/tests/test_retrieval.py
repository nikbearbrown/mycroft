import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from assistant.retrieval import retrieve
from assistant.mock_corpus import get_corpus


def test_retrieve_finds_match_for_known_sector():
    corpus = get_corpus()
    result = retrieve("What is the outlook for semiconductors?", corpus)
    assert result.match_found is True
    assert any(doc["doc_id"] == "DOC-001" for doc in result.matches)


def test_retrieve_no_match_for_unrelated_query():
    corpus = get_corpus()
    result = retrieve("What is the price of tulip bulbs in the Netherlands?", corpus)
    assert result.match_found is False
    assert result.matches == []


def test_retrieve_empty_query_returns_no_match():
    corpus = get_corpus()
    result = retrieve("", corpus)
    assert result.match_found is False


if __name__ == "__main__":
    test_retrieve_finds_match_for_known_sector()
    test_retrieve_no_match_for_unrelated_query()
    test_retrieve_empty_query_returns_no_match()
    print("test_retrieval.py: all tests passed")

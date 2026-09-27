"""
WHAT THIS FILE DOES: Searches the mock corpus for documents relevant to an
advisor's query and reports whether any relevant material was found.

CONFIRMED / CONSTRUCTED: Retrieval as a capability is CONFIRMED (case study
Section 3.1 — the Assistant "retrieves and synthesizes answers" against the
research corpus). The matching mechanism here ([DEV]: naive keyword/sector
overlap against the query string) and the no-match behavior are both
CONSTRUCTED. Morgan Stanley and OpenAI disclose that retrieval quality
improved through iterative tuning (a reported "20% to 80%" figure), but
disclose nothing about the mechanism itself, ranking logic, or how many
documents are surfaced per query. This module makes no claim to replicate
any of that.

This is the halt owner for Pipeline 1's no-match condition: if no document
in the corpus overlaps with the query, `match_found` is False, and
orchestrator_assistant.py must not call synthesis.py.
"""

from dataclasses import dataclass, field


@dataclass
class RetrievalResult:
    matches: list[dict] = field(default_factory=list)
    match_found: bool = False


def retrieve(query: str, corpus: list[dict]) -> RetrievalResult:
    """[DEV] Naive keyword-overlap match: a document matches if any word in
    its sector tag or title appears in the (lowercased) query string. This is
    a labeled stand-in, not a claim about the real Assistant's retrieval
    mechanism, which is undisclosed."""
    if not query:
        return RetrievalResult(matches=[], match_found=False)

    query_lower = query.lower()
    query_words = set(query_lower.split())
    matches = [
        doc for doc in corpus
        if doc["sector"].replace("_", " ") in query_lower
        or any(word.lower() in query_words for word in doc["title"].split())
    ]

    return RetrievalResult(matches=matches, match_found=len(matches) > 0)

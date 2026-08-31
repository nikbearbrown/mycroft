"""
WHAT THIS FILE DOES: Provides a small, entirely fabricated set of research-document
stand-ins for the Assistant pipeline's Retrieval stage to search against.

CONFIRMED / CONSTRUCTED: CONSTRUCTED in full. Morgan Stanley's confirmed record
(case study Section 3.1) states the real corpus has grown to roughly 100,000
documents, per OpenAI's own account. Nothing about the real corpus's content,
structure, or fields is disclosed. This module invents a handful of documents
with a minimal schema (title, sector, snippet, recency) sufficient to exercise
Retrieval and Synthesis in tests. No real Morgan Stanley research content
appears anywhere in this file.

One entry intentionally has no sector overlap with any query used in this
pipeline's tests, so the no-match branch in retrieval.py has something real
to fail against.
"""

MOCK_CORPUS = [
    {
        "doc_id": "DOC-001",
        "title": "Semiconductor Capital Expenditure Outlook",
        "sector": "semiconductors",
        "snippet": "Capital expenditure in the semiconductor sector is projected "
                    "to moderate over the coming quarters as fabrication capacity "
                    "additions from the prior cycle come online.",
        "recency": "2026-Q1",
    },
    {
        "doc_id": "DOC-002",
        "title": "Regional Banking Net Interest Margin Trends",
        "sector": "regional_banking",
        "snippet": "Net interest margins across regional banks have stabilized "
                    "following several quarters of compression tied to deposit "
                    "repricing.",
        "recency": "2026-Q1",
    },
    {
        "doc_id": "DOC-003",
        "title": "Renewable Energy Infrastructure Financing",
        "sector": "renewable_energy",
        "snippet": "Financing structures for utility-scale renewable projects have "
                    "shifted toward longer-duration instruments as developers seek "
                    "to lock in current rate conditions.",
        "recency": "2025-Q4",
    },
    {
        "doc_id": "DOC-004",
        "title": "Consumer Discretionary Spending Patterns",
        "sector": "consumer_discretionary",
        "snippet": "Discretionary spending has shown resilience in higher-income "
                    "cohorts while remaining more sensitive to rate conditions "
                    "among lower-income cohorts.",
        "recency": "2026-Q1",
    },
    # Deliberately no "sector" here overlaps with any test query below — this
    # entry exists to prove it is NOT retrieved for an unrelated query, not to
    # be a no-match case itself.
    {
        "doc_id": "DOC-005",
        "title": "Global Shipping Container Rates",
        "sector": "shipping_logistics",
        "snippet": "Container shipping rates on major trans-oceanic routes have "
                    "diverged by corridor over the past two quarters.",
        "recency": "2025-Q4",
    },
]


def get_corpus() -> list[dict]:
    """Returns the fabricated corpus. No filtering happens here — that is
    retrieval.py's job."""
    return MOCK_CORPUS

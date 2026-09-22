"""
Retrieval — Step 3 of the illustrated workflow (Section 4).

CONFIRMED: the assistant can answer questions "about their transactions"
(Lloyds AI hub page, describing the Bank of Scotland rollout). Lloyds
does not disclose the retrieval architecture (whether it is RAG-based
like Athena, or something else), a data source, or a matching tolerance.
Everything below is this scaffold's own [DEV] construction.
"""

from typing import Dict, List, Optional

from .models import ClassificationResult, RetrievalResult, TransactionRecord

# [DEV] Illustrative matching tolerance only — not a disclosed Lloyds figure.
AMOUNT_MATCH_TOLERANCE = 0.01


def retrieve_and_match(
    classification: ClassificationResult,
    transactions: Dict[str, List[TransactionRecord]],
) -> RetrievalResult:
    """
    Look up the claimed date in the mock transaction store and check
    whether any transaction that day agrees with the claimed amount.

    Three distinct outcomes, kept separate rather than collapsed into a
    single "not found" bucket:
      - no record for that date at all       -> "no_matching_record"
      - record(s) exist, none match the amount -> "record_mismatch"
      - a record matches                     -> "matched"
    """
    date = classification.extracted_date
    amount = classification.extracted_amount

    day_records: Optional[List[TransactionRecord]] = transactions.get(date)

    if not day_records:
        return RetrievalResult(status="no_matching_record")

    for record in day_records:
        if abs(record.amount - amount) <= AMOUNT_MATCH_TOLERANCE:
            return RetrievalResult(status="matched", record=record)

    return RetrievalResult(status="record_mismatch")

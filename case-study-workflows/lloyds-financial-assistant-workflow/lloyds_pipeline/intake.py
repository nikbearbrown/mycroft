"""
Intake — Step 2 of the illustrated workflow (Section 4).

CONFIRMED: the assistant handles two distinct query types — transaction
questions and general financial coaching (Section 3.2). Lloyds does not
disclose how it tells the two apart, or what it does with a query that is
neither. Both the keyword lists below and the decision to treat an
ambiguous or off-topic query as "unclassifiable" are this scaffold's own
[DEV] construction.

INPUT VALIDATION -- added after an adversarial testing pass found two
real defects in the original version of this file:

  1. A non-string `raw_text` (None, an int, etc.) crashed with an
     unhandled AttributeError the instant `.lower()` was called on it.
  2. A non-numeric `claimed_amount` (e.g. the string "42.50" instead of
     the float 42.50) passed straight through Intake with no complaint,
     then crashed Retrieval with an unhandled TypeError when it tried to
     do arithmetic on it.

Both are now caught here, deliberately, and turned into a new,
honestly-labeled outcome ("malformed_input") rather than either crashing
or silently guessing. A third defect -- a non-zero-padded or otherwise
malformed date silently being treated as "no transaction that day" when
in fact the transaction existed under a different date-string
representation -- is caught separately below as "malformed_date", kept
distinct from "malformed_input" and from a genuine no-record result,
because "the date format was unreadable" and "we checked and there was
truly nothing" are not the same claim and this pipeline does not conflate
them.
"""

import math
import re

from .models import Query, ClassificationResult

# [DEV] A strict YYYY-MM-DD shape check. Lloyds discloses no date format
# or parsing tolerance; this scaffold picks one shape and refuses to
# guess at any other, rather than attempting a permissive multi-format
# parser this case study has no basis for.
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# [DEV] Illustrative keyword lists only. Not a disclosed Lloyds mechanism.
TRANSACTION_KEYWORDS = (
    "transaction", "charge", "payment", "spent", "debit",
    "withdrawal", "purchase", "paid",
)
COACHING_KEYWORDS = (
    "budget", "save", "saving", "spending habit", "financial goal", "afford",
)


def classify_query(query: Query) -> ClassificationResult:
    """
    Classify a raw query into transaction_lookup / coaching / unclassifiable
    / malformed_input / malformed_date.

    A query matching both keyword sets, or neither, is treated as
    unclassifiable rather than guessed at — consistent with this series'
    practice of escalating on ambiguity rather than picking a side.

    Input validation runs before classification logic, not after: a
    malformed raw_text is caught immediately, before any keyword matching
    is even attempted.
    """
    if not isinstance(query.raw_text, str):
        return ClassificationResult(query_type="malformed_input")

    text = query.raw_text.lower()

    is_transaction = any(kw in text for kw in TRANSACTION_KEYWORDS)
    is_coaching = any(kw in text for kw in COACHING_KEYWORDS)

    if is_transaction and not is_coaching:
        amount = query.claimed_amount
        date = query.claimed_date

        if amount is not None and not _is_valid_amount(amount):
            return ClassificationResult(query_type="malformed_input")

        if date is not None and not _is_valid_date_format(date):
            return ClassificationResult(query_type="malformed_date")

        return ClassificationResult(
            query_type="transaction_lookup",
            extracted_amount=amount,
            extracted_date=date,
        )

    if is_coaching and not is_transaction:
        return ClassificationResult(query_type="coaching")

    return ClassificationResult(query_type="unclassifiable")


def _is_valid_amount(amount) -> bool:
    """
    A claimed amount must be a real, finite number. Explicitly rejects
    bool (Python treats bool as a subclass of int, which would otherwise
    let True/False silently pass arithmetic checks downstream) and NaN
    (which compares unequal to everything, including itself, and would
    otherwise silently fall through Retrieval as a "mismatch" rather than
    being recognized as nonsensical input in the first place).
    """
    if isinstance(amount, bool):
        return False
    if not isinstance(amount, (int, float)):
        return False
    if isinstance(amount, float) and math.isnan(amount):
        return False
    return True


def _is_valid_date_format(date) -> bool:
    """Strict ISO YYYY-MM-DD shape only. See _DATE_PATTERN comment above."""
    return isinstance(date, str) and bool(_DATE_PATTERN.match(date))

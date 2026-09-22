"""
Data models.

CONFIRMED (per Section 3.2 of the case study, sourced to Lloyds Banking
Group's 6 November 2025 press release and 22 June 2026 update): the
financial assistant (a) answers customer questions about their own
transactions, (b) provides general financial coaching, and (c) can "refer
to expert human support when needed."

Everything about HOW it does any of this — data structures, matching
logic, thresholds — is CONSTRUCTED for this scaffold. No Lloyds source
discloses a schema of any kind.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Query:
    """A raw customer query as it arrives at the assistant."""
    raw_text: str
    claimed_amount: Optional[float] = None
    claimed_date: Optional[str] = None  # ISO format, e.g. "2026-06-15"


@dataclass
class ClassificationResult:
    """
    Output of Intake.

    query_type is one of:
      - "transaction_lookup" : a question about a specific transaction
      - "coaching"           : a general financial-coaching question
      - "unclassifiable"     : neither, or ambiguous between both

    [DEV] The three-way split, and the keyword logic that produces it, are
    this scaffold's own construction (see intake.py). Lloyds confirms both
    the transaction-lookup and coaching functions exist (Section 3.2) but
    discloses no classification mechanism.
    """
    query_type: str
    extracted_amount: Optional[float] = None
    extracted_date: Optional[str] = None


@dataclass
class TransactionRecord:
    """A single mock transaction. Fabricated data only — see mock_data.py."""
    amount: float
    date: str
    merchant: str
    description: str


@dataclass
class RetrievalResult:
    """
    Output of Retrieval.

    status is one of:
      - "matched"            : a record was found and agrees with the claim
      - "no_matching_record" : no record exists for the claimed date at all
      - "record_mismatch"    : a record exists for that date, but its amount
                                does not agree with what the customer claimed

    [DEV] This three-way outcome and the matching tolerance in retrieval.py
    are this scaffold's own construction. Lloyds discloses that the
    assistant answers transaction questions; it does not disclose how it
    checks a claim against an account record.
    """
    status: str
    record: Optional[TransactionRecord] = None


@dataclass
class PipelineResult:
    """Final, terminal output of the orchestrator."""
    status: str            # "answered_directly" | "escalated_to_human" | "recognized_not_modeled"
    reason: Optional[str] = None
    detail: Optional[str] = None
    record: Optional[TransactionRecord] = None

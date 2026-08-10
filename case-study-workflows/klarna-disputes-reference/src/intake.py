"""
WHAT THIS FILE DOES: Takes a customer's raw message and figures out two things —
what kind of dispute it is, and what specific claim (a date or an amount) the
customer is making. Nothing downstream can run without this file's output.

Klarna's own Feb 2024 press release confirms the assistant handles refunds,
returns, payment issues, cancellations, disputes, and invoice inaccuracies —
but confirms nothing about HOW it figures out which one a message is. This file
is a constructed, honestly-labeled stand-in for that step: plain keyword
matching, not machine learning. See docs/DESIGN_DECISIONS.md DD-001, DD-006,
DD-010, DD-011.
"""

from dataclasses import dataclass
from typing import Optional
import re


# --------------------------------------------------------------------------
# [DEV] Keyword sets — illustrative only, not tuned against real customer
# language. If you adopt this repo, replace these with something derived
# from your own message data.
#
# Order matters: late_fee_dispute is checked BEFORE refund_request. If a
# message hits both sets, late_fee_dispute wins as the assigned type (DD-010).
# This is an arbitrary but deterministic tiebreak — not defended as "correct."
# --------------------------------------------------------------------------
LATE_FEE_KEYWORDS = [
    "late fee", "late charge", "charged late", "late payment",
    "before the due date", "paid on time", "on time",
]

REFUND_KEYWORDS = [
    "refund", "money back", "reimburse", "give me my money",
    "return my payment",
]

# [DEV] Confidence tiers — a discrete scheme, not a continuous score, because
# keyword matching can report actual ambiguity (two sets hit) but has no
# honest basis for graduated uncertainty the way a real model would (DD-011).
CONFIDENCE_EXACT_MATCH = 0.9
CONFIDENCE_AMBIGUOUS_MATCH = 0.5
CONFIDENCE_NO_MATCH = 0.0

# [DEV] The threshold Gate compares this confidence against lives in gate.py,
# not here — Intake only ever reports what it found, it doesn't know what
# "good enough" means downstream. Keeping that decision in one place.


@dataclass
class IntakeResult:
    """
    The single data contract this module hands to everything downstream.

    status:          "ok" or "escalate_unclassified" — the ONE field the
                      orchestrator dispatches on. Nothing downstream should
                      ever need to inspect dispute_type/confidence directly
                      to decide whether to keep going.
    dispute_type:     "late_fee_dispute" | "refund_request" | "unclassified"
    confidence:       0.9 / 0.5 / 0.0 — see CONFIDENCE_* constants above.
    claimed_date:     Whatever date the customer's message claims, or None.
                       Only meaningful for late_fee_dispute.
    claimed_amount:   Whatever amount the customer's message claims, or None.
                       Only meaningful for refund_request.
    """
    status: str
    dispute_type: str
    confidence: float
    claimed_date: Optional[str]
    claimed_amount: Optional[float]


def classify_intent(message: str) -> tuple[str, float]:
    """
    Decide which of the two in-scope dispute types (or neither) a message
    represents, using nothing but keyword matching.

    Returns (dispute_type, confidence). Does not touch claim details at all —
    that's extract_claim_details's job, kept separate so each can be tested
    independently (this mirrors the actual bug class this series has hit
    before: a gap between what one sub-function assumes and what the next
    expects, invisible until you test the seam directly).
    """
    text = message.lower()

    hits_late_fee = any(keyword in text for keyword in LATE_FEE_KEYWORDS)
    hits_refund = any(keyword in text for keyword in REFUND_KEYWORDS)

    if hits_late_fee and hits_refund:
        # Ambiguous — both sets matched. late_fee_dispute wins per the locked
        # tiebreak (DD-010), but confidence drops to signal real ambiguity,
        # not a clean read.
        return "late_fee_dispute", CONFIDENCE_AMBIGUOUS_MATCH

    if hits_late_fee:
        return "late_fee_dispute", CONFIDENCE_EXACT_MATCH

    if hits_refund:
        return "refund_request", CONFIDENCE_EXACT_MATCH

    return "unclassified", CONFIDENCE_NO_MATCH


# Simple, permissive date patterns. Illustrative only — a real system would
# need much broader natural-language date parsing. [DEV]
_DATE_PATTERNS = [
    r"\b\d{4}-\d{2}-\d{2}\b",       # 2024-03-01
    r"\b\d{1,2}/\d{1,2}/\d{4}\b",   # 03/01/2024
]

# Matches a dollar amount like "$120.50" or "$120". [DEV]
_AMOUNT_PATTERN = r"\$\s?(\d+(?:\.\d{1,2})?)"


def extract_claim_details(message: str) -> dict:
    """
    Pull a claimed date and/or claimed amount out of the message text.

    Must NOT guess. If a field genuinely isn't in the message, this returns
    None for it — a downstream function inventing a plausible-looking value
    here would be exactly the kind of silent, undetectable bug this series
    exists to avoid.
    """
    claimed_date = None
    for pattern in _DATE_PATTERNS:
        match = re.search(pattern, message)
        if match:
            claimed_date = match.group(0)
            break

    claimed_amount = None
    amount_match = re.search(_AMOUNT_PATTERN, message)
    if amount_match:
        claimed_amount = float(amount_match.group(1))

    return {"claimed_date": claimed_date, "claimed_amount": claimed_amount}


def run_intake(message: str) -> IntakeResult:
    """
    The single public entrypoint. Combines classification and extraction,
    and sets the one status field everything downstream actually reads.
    """
    dispute_type, confidence = classify_intent(message)
    claim = extract_claim_details(message)

    status = "escalate_unclassified" if dispute_type == "unclassified" else "ok"

    return IntakeResult(
        status=status,
        dispute_type=dispute_type,
        confidence=confidence,
        claimed_date=claim["claimed_date"],
        claimed_amount=claim["claimed_amount"],
    )

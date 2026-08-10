"""
Intake component — CommBank Disputes Workflow (Illustrative Reference Implementation)

WHAT THIS FILE DOES: takes the customer's raw dispute text and produces a
structured claim — dispute type, amount, merchant, date, and a confidence
score — or flags the claim for human review if it can't do that cleanly.
First step in the pipeline; see README.md for the full workflow.

CONFIRMED basis: Dan Jermyn (CBA Chief Decision Scientist), quoted in Evident
Insights, "167 ways banks use AI", 20 Feb 2025 — "understanding customer intent
in an AI-assisted channel."

CONSTRUCTED: Structured claim-detail extraction (amount, merchant, date) is
treated here as part of Intake rather than a separate, unnamed function. No
CBA source assigns extraction to a specific step — see docs/DESIGN_DECISIONS.md,
entry 001, and docs/DESIGN_SPECS.md for the full reasoning.

CONSTRUCTED (entry 006): an unclassified dispute_type is now an explicit
escalation trigger, not a silent pass-through — Gate's risk-tiered thresholds
(entry 005) depend on dispute_type, so a claim this component can't classify
is escalated rather than defaulted to a middle tier it was never evaluated
against.

Note: this classifier only ever returns one of the three named types below,
or None. There is no fourth "other" category implemented — an earlier
version of the design spec described one that the code never actually
produced; that inconsistency was corrected during code/spec reconciliation
rather than left standing (see docs/DESIGN_DECISIONS.md, entry 007).

This is a rule-based, illustrative parser — not a claim about what model or
technique CBA's actual tool uses. No source discloses that. [DEV] The
biggest lever for adapting this scaffold is right here: swap the regex-based
_extract_* and _classify_dispute_type functions below for a real NLU/LLM
call. Everything downstream (Verification, Gate) only depends on the output
shape (IntakeResult), not on how it's produced.
"""

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

# CONSTRUCTED: dispute type taxonomy — invented for this illustration.
# Exactly three types are classified; anything that matches none of them
# is dispute_type=None, which now escalates (entry 006) rather than
# defaulting through Gate's tiering.
# [DEV] Add a new dispute type here (new key + trigger phrases) if your use
# case needs one — just remember to also add a matching entry to
# AUTO_LODGE_THRESHOLDS in gate.py, or it'll silently fall back to the
# defensive-only default there.
DISPUTE_TYPES = {
    "unrecognized_charge": ["don't recognize", "do not recognize", "never made", "not mine"],
    "unauthorized_transaction": ["didn't authorize", "did not authorize", "unauthorized", "not authorised"],
    "duplicate_charge": ["charged twice", "duplicate", "double charged"],
}

# CONSTRUCTED: a tiny known-merchant list to support the illustrative parser.
# [DEV] Add merchants here, or replace this whole lookup with a real
# merchant-directory query if adapting this scaffold.
KNOWN_MERCHANTS = ["amazon", "woolworths", "coles", "jb hi-fi", "uber", "netflix", "spotify"]

# CONSTRUCTED escalation threshold — not CBA's actual criteria.
# [DEV] Raise this to escalate less often (more auto-processing, more risk of
# a bad extraction slipping through); lower it to escalate more often.
CONFIDENCE_ESCALATION_THRESHOLD = 0.6


@dataclass
class IntakeResult:
    dispute_type: Optional[str]
    claimed_amount: Optional[float]
    claimed_merchant: Optional[str]
    claimed_date: Optional[date]
    extraction_confidence: float
    escalate: bool
    escalation_reason: Optional[str]


def _extract_amount(text: str) -> Optional[float]:
    match = re.search(r"\$\s?(\d+(?:\.\d{1,2})?)", text)
    if match:
        return float(match.group(1))
    return None


def _extract_merchant(text: str) -> Optional[str]:
    lowered = text.lower()
    for merchant in KNOWN_MERCHANTS:
        if merchant in lowered:
            return merchant.title()
    return None


def _extract_date(text: str) -> Optional[date]:
    # CONSTRUCTED: accepts YYYY-MM-DD only, for illustration purposes.
    match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _classify_dispute_type(text: str) -> Optional[str]:
    lowered = text.lower()
    for dtype, phrases in DISPUTE_TYPES.items():
        if any(phrase in lowered for phrase in phrases):
            return dtype
    return None


def run_intake(raw_text: str) -> IntakeResult:
    """
    Entry point for the Intake component.

    Input: raw_text (str) — the customer's natural-language dispute description.
    Output: IntakeResult — see dataclass above; this is the contract Verification's
    input schema must match (docs/DESIGN_SPECS.md).
    """
    dispute_type = _classify_dispute_type(raw_text)
    amount = _extract_amount(raw_text)
    merchant = _extract_merchant(raw_text)
    claim_date = _extract_date(raw_text)

    fields_found = sum(x is not None for x in [dispute_type, amount, merchant, claim_date])
    extraction_confidence = fields_found / 4.0

    missing_required = amount is None or merchant is None or claim_date is None
    low_confidence = extraction_confidence < CONFIDENCE_ESCALATION_THRESHOLD
    unclassified_type = dispute_type is None

    escalate = low_confidence or missing_required or unclassified_type

    escalation_reason = None
    if escalate:
        if unclassified_type and not missing_required and not low_confidence:
            # Entry 006: amount/merchant/date all extracted cleanly, but the
            # dispute type itself couldn't be classified — Gate's risk tiers
            # depend on this field, so it escalates rather than defaults.
            escalation_reason = "unclassified_dispute_type"
        else:
            escalation_reason = "ambiguous_input_low_extraction_confidence"

    return IntakeResult(
        dispute_type=dispute_type,
        claimed_amount=amount,
        claimed_merchant=merchant,
        claimed_date=claim_date,
        extraction_confidence=round(extraction_confidence, 2),
        escalate=escalate,
        escalation_reason=escalation_reason,
    )

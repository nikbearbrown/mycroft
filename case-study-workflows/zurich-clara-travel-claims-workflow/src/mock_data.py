"""
WHAT THIS FILE DOES: Provides fabricated claim documents and policy records
for the pipeline to run against. No real Zurich, AgentricAI, or Clara data
exists anywhere in this file.

CONSTRUCTED in full. Grounded in the case study's own scenario (blueprint
Section 3 — Kwame's claim), which is itself explicitly not a Zurich
disclosure. Fixtures below exist to make every halt condition in the
locked design independently reachable and testable.
"""

from datetime import date

# ---------------------------------------------------------------------------
# Policy records
# ---------------------------------------------------------------------------
# [DEV] Schema is illustrative and revisable — no source discloses how
# Zurich/AgentricAI structure a travel policy record.

POLICY_RECORDS = {
    "POLICY-001": {
        "covered_cancellation_reasons": {"airline_operational", "weather"},
        "covered_window_start": date(2026, 3, 1),
        "covered_window_end": date(2026, 9, 30),
        "covers_dependent_sub_claims": True,
    },
    # Deliberately incomplete/ambiguous record: dependent-sub-claim coverage
    # is unspecified, so any claim resolving against this policy cannot have
    # its dependency question answered cleanly.
    "POLICY-002": {
        "covered_cancellation_reasons": {"airline_operational"},
        "covered_window_start": date(2026, 1, 1),
        "covered_window_end": date(2026, 12, 31),
        "covers_dependent_sub_claims": None,  # ambiguous on purpose
    },
}

# ---------------------------------------------------------------------------
# Claim fixtures
# ---------------------------------------------------------------------------
# Each fixture is a full claim submission: a policy_id to look up, and a list
# of tagged documents. Document "type" tags and "language" tags are a [DEV]
# taxonomy (flight_notice / medical_receipt / free_text_note) — Zurich
# discloses no such schema.

CLAIM_KWAME_HAPPY_PATH = {
    "claim_id": "CLAIM-KWAME-001",
    "policy_id": "POLICY-001",
    "documents": [
        {
            "type": "flight_notice",
            "language": "en",
            "raw_text": "Connecting flight cancelled due to airline operational disruption on 2026-06-10.",
            "extraction_confidence": 0.97,
            "translation_confidence": None,  # English source, not applicable
            "extracted_date": date(2026, 6, 10),
            "extracted_reason": "airline_operational",
        },
        {
            "type": "medical_receipt",
            "language": "th",
            "raw_text": "[non-English hospital receipt, treatment for minor injury]",
            "extraction_confidence": 0.93,
            "translation_confidence": 0.95,
            "extracted_date": date(2026, 6, 10),
            "extracted_amount": 120.00,
            "extracted_currency": "USD",
        },
        {
            "type": "free_text_note",
            "language": "en",
            "raw_text": "Requesting reimbursement for missed tour booked 2026-05-01, cost $200.",
            "extraction_confidence": 0.90,
            "translation_confidence": None,
            "extracted_amount": 200.00,
            "extracted_currency": "USD",
            "tour_booking_date": date(2026, 5, 1),
            "claims_dependent_on": "flight_notice",
        },
    ],
}

CLAIM_MISSING_DOCUMENT = {
    "claim_id": "CLAIM-MISSING-DOC-001",
    "policy_id": "POLICY-001",
    "documents": [
        {
            "type": "free_text_note",
            "language": "en",
            "raw_text": "Requesting reimbursement for hospital treatment, no receipt attached.",
            "extraction_confidence": 0.92,
            "translation_confidence": None,
            "claims_medical_expense": True,
            # No corresponding medical_receipt document exists in this claim —
            # this is what should trip the missing_document halt in intake.py.
        },
    ],
}

CLAIM_LOW_EXTRACTION_CONFIDENCE = {
    "claim_id": "CLAIM-LOW-EXTRACTION-001",
    "policy_id": "POLICY-001",
    "documents": [
        {
            "type": "flight_notice",
            "language": "en",
            "raw_text": "Flight cancelled, reason illegible in scan.",
            "extraction_confidence": 0.40,  # below threshold
            "translation_confidence": None,
            "extracted_date": date(2026, 6, 10),
            "extracted_reason": "airline_operational",
        },
        {
            "type": "medical_receipt",
            "language": "th",
            "raw_text": "[hospital receipt]",
            "extraction_confidence": 0.90,
            "translation_confidence": 0.92,
            "extracted_date": date(2026, 6, 10),
            "extracted_amount": 80.00,
            "extracted_currency": "USD",
        },
    ],
}

CLAIM_LOW_TRANSLATION_CONFIDENCE = {
    "claim_id": "CLAIM-LOW-TRANSLATION-001",
    "policy_id": "POLICY-001",
    "documents": [
        {
            "type": "flight_notice",
            "language": "en",
            "raw_text": "Flight cancelled due to airline operational disruption.",
            "extraction_confidence": 0.95,
            "translation_confidence": None,
            "extracted_date": date(2026, 6, 10),
            "extracted_reason": "airline_operational",
        },
        {
            "type": "medical_receipt",
            "language": "th",
            "raw_text": "[ambiguous handwritten hospital receipt]",
            "extraction_confidence": 0.91,  # high extraction confidence
            "translation_confidence": 0.35,  # but low translation confidence
            "extracted_date": date(2026, 6, 10),
            "extracted_amount": 80.00,
            "extracted_currency": "USD",
        },
    ],
}

CLAIM_CROSS_DOCUMENT_CONTRADICTION = {
    "claim_id": "CLAIM-CONTRADICTION-001",
    "policy_id": "POLICY-001",
    "documents": [
        {
            "type": "flight_notice",
            "language": "en",
            "raw_text": "Flight cancelled 2026-06-10 due to airline operational disruption.",
            "extraction_confidence": 0.96,
            "translation_confidence": None,
            "extracted_date": date(2026, 6, 10),
            "extracted_reason": "airline_operational",
        },
        {
            "type": "medical_receipt",
            "language": "th",
            "raw_text": "[hospital receipt dated well before the claimed disruption]",
            "extraction_confidence": 0.94,
            "translation_confidence": 0.93,
            "extracted_date": date(2026, 3, 1),  # contradicts flight notice date
            "extracted_amount": 80.00,
            "extracted_currency": "USD",
        },
    ],
}

CLAIM_NO_MATCHING_POLICY = {
    "claim_id": "CLAIM-NO-POLICY-001",
    "policy_id": "POLICY-DOES-NOT-EXIST",
    "documents": [
        {
            "type": "flight_notice",
            "language": "en",
            "raw_text": "Flight cancelled due to airline operational disruption.",
            "extraction_confidence": 0.95,
            "translation_confidence": None,
            "extracted_date": date(2026, 6, 10),
            "extracted_reason": "airline_operational",
        },
    ],
}

CLAIM_UNRESOLVABLE_DEPENDENCY = {
    "claim_id": "CLAIM-DEPENDENCY-001",
    "policy_id": "POLICY-002",  # covers_dependent_sub_claims is ambiguous (None)
    "documents": [
        {
            "type": "flight_notice",
            "language": "en",
            "raw_text": "Flight cancelled for a reason POLICY-002 does not cover.",
            "extraction_confidence": 0.95,
            "translation_confidence": None,
            "extracted_date": date(2026, 6, 15),
            # Deliberately NOT a covered reason under POLICY-002, so
            # flight_cancellation_covered evaluates False -- which is what
            # makes the dependent tour sub-claim's outcome hinge on the
            # policy's ambiguous covers_dependent_sub_claims stance.
            "extracted_reason": "voluntary_change",
        },
        {
            "type": "free_text_note",
            "language": "en",
            "raw_text": "Requesting reimbursement for missed tour.",
            "extraction_confidence": 0.90,
            "translation_confidence": None,
            "extracted_amount": 200.00,
            "extracted_currency": "USD",
            "tour_booking_date": date(2026, 5, 1),
            "claims_dependent_on": "flight_notice",
        },
    ],
}


def get_policy_record(policy_id):
    """Returns the policy record for a given ID, or None if not found."""
    return POLICY_RECORDS.get(policy_id)

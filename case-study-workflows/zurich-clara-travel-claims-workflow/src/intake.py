"""
WHAT THIS FILE DOES: Validates a bundled claim submission before anything
downstream runs. Owns two distinct checks: (1) structural completeness —
every document is tagged with a type and language — and (2) document-
completeness — a required document type isn't missing entirely, given what
the claim itself asserts (e.g., a claimed medical expense with no receipt).

Document-completeness ownership was moved here from Extraction during
/review (Decision B): detecting an absent document is resolvable from
tags alone and does not require the confidence scoring Extraction exists
to do.

[DEV]-labeled construction: the document-type taxonomy (flight_notice /
medical_receipt / free_text_note) and the language-tagging schema.
Zurich/AgentricAI disclose no intake schema at all.
"""

REQUIRED_TAGS = {"type", "language"}


def validate_intake(claim):
    """
    Returns a status object:
      {"status": "ok"}
      {"status": "halted", "reason": None}  -- structural incompleteness
      {"status": "halted", "reason": "missing_document"}
    """
    documents = claim.get("documents")
    if not documents:
        return {"status": "halted", "reason": None, "detail": "no documents present"}

    for doc in documents:
        if not REQUIRED_TAGS.issubset(doc.keys()):
            return {
                "status": "halted",
                "reason": None,
                "detail": f"document missing required tag(s): {REQUIRED_TAGS - doc.keys()}",
            }

    missing = _check_document_completeness(documents)
    if missing:
        return {"status": "halted", "reason": "missing_document", "detail": missing}

    return {"status": "ok"}


def _check_document_completeness(documents):
    """
    Tag-level cross-reference only — no extraction/NLP involved. If any
    document asserts a medical expense claim (claims_medical_expense=True)
    but no document of type 'medical_receipt' exists in the submission,
    flag it as missing.
    """
    claims_medical_expense = any(
        doc.get("claims_medical_expense") for doc in documents
    )
    has_medical_receipt = any(doc.get("type") == "medical_receipt" for doc in documents)

    if claims_medical_expense and not has_medical_receipt:
        return "claim references a medical expense but no medical_receipt document is present"

    return None

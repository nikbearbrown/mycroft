"""
WHAT THIS FILE DOES: Validates per-document extraction and translation
confidence against thresholds. Pure function — receives already-tagged
documents (post-Intake), does not fetch anything itself, does not touch
mock_data.py.

Extraction/translation-confidence separation is this build's own design
requirement (not a Zurich disclosure) — a document can be translated with
high linguistic confidence but still yield low-confidence structured
extraction, or vice versa. Collapsing these into one score would hide
exactly the failure mode this build exists to surface. This is one of the
three non-negotiable structural guarantees locked at /v1.

[DEV]-labeled construction: the specific confidence thresholds below.
No source discloses what threshold, if any, Zurich/AgentricAI use.

This module is a deterministic stand-in for real extraction/translation.
It does not call an LLM or any real NLP system — mock fixtures already
carry their extracted facts and confidence scores, matching this series'
established pattern of deterministic stand-ins for AI calls.
"""

EXTRACTION_CONFIDENCE_THRESHOLD = 0.70  # [DEV]
TRANSLATION_CONFIDENCE_THRESHOLD = 0.70  # [DEV]


def extract(documents):
    """
    Returns a status object:
      {"status": "ok", "documents": documents}
      {"status": "halted", "reason": "low_extraction_confidence", "detail": ...}
      {"status": "halted", "reason": "low_translation_confidence", "detail": ...}

    Extraction-confidence is checked for every document. Translation-
    confidence is checked only for documents where it is not None (i.e.,
    non-English documents per the [DEV] language-tagging schema).
    """
    for doc in documents:
        extraction_confidence = doc.get("extraction_confidence")
        if extraction_confidence is None or extraction_confidence < EXTRACTION_CONFIDENCE_THRESHOLD:
            return {
                "status": "halted",
                "reason": "low_extraction_confidence",
                "detail": f"document type={doc.get('type')} extraction_confidence={extraction_confidence}",
            }

        translation_confidence = doc.get("translation_confidence")
        if translation_confidence is not None and translation_confidence < TRANSLATION_CONFIDENCE_THRESHOLD:
            return {
                "status": "halted",
                "reason": "low_translation_confidence",
                "detail": f"document type={doc.get('type')} translation_confidence={translation_confidence}",
            }

    return {"status": "ok", "documents": documents}

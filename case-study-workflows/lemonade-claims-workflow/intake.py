"""
WHAT THIS FILE DOES: Sends a customer's free-text claim to the configured
language model, parses the result into the diagnosis/amount/date fields
Verification needs, and escalates before anything else runs if the model
can't classify the claim or isn't confident about it.
"""
import json
from dataclasses import dataclass
from typing import Optional

# [DEV] Illustrative placeholder instruction. Not a reverse-engineered or
# disclosed version of any real system's prompt (blueprint SS3.2). Rewrite
# this for your own claim types and your own chosen model's response
# tendencies.
EXTRACTION_INSTRUCTION = (
    "You are processing a pet insurance claim. Given the customer's free-text "
    "description, classify the claim and extract: diagnosis or treatment, "
    "amount billed, and date of service. Respond ONLY with JSON in the form "
    '{"claim_type": ..., "diagnosis": ..., "amount": ..., "date": ..., '
    '"confidence": ...}. If you cannot classify the claim at all, respond '
    'with {"claim_type": "unclassified", "confidence": 0.0}.'
)


@dataclass
class ExtractedFields:
    claim_type: str
    diagnosis: Optional[str]
    amount: Optional[float]
    date: Optional[str]
    confidence: float


@dataclass
class IntakeEscalation:
    reason: str


class Intake:
    """
    llm_client (a swappable, injected dependency - see Orchestrator's
    Dependency-Provision Rule) and confidence_threshold (a scalar tunable,
    read from Configuration by whatever constructs this Intake instance) are
    both supplied at construction time.
    """

    def __init__(self, llm_client, confidence_threshold: float):
        self._llm_client = llm_client
        self._confidence_threshold = confidence_threshold

    def process(self, raw_claim_text: str):
        """Returns ExtractedFields on success, or IntakeEscalation on failure."""
        raw_response = self._llm_client.call(EXTRACTION_INSTRUCTION, raw_claim_text)

        try:
            parsed = json.loads(raw_response)
        except (json.JSONDecodeError, TypeError):
            # Malformed/unparseable model output is treated identically to an
            # "unclassified" response - a model response Intake can't use is
            # functionally no different from a model that said it didn't
            # know. This is the exact class of bug that broke Verification
            # during CommBank's code review pass; tested explicitly here.
            return IntakeEscalation(reason="unclassified")

        claim_type = parsed.get("claim_type")
        confidence = parsed.get("confidence", 0.0)

        if not claim_type or claim_type == "unclassified":
            return IntakeEscalation(reason="unclassified")

        if confidence < self._confidence_threshold:
            return IntakeEscalation(reason="low_confidence")

        return ExtractedFields(
            claim_type=claim_type,
            diagnosis=parsed.get("diagnosis"),
            amount=parsed.get("amount"),
            date=parsed.get("date"),
            confidence=confidence,
        )

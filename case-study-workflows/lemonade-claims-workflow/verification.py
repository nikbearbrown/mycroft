"""
WHAT THIS FILE DOES: Confirms Intake's extracted claim details are complete,
looks up the insurer's own record and fraud signal independently, and checks
for a match - escalating with a specific named reason the moment any check
fails, before any later check runs.

Policy-coverage checking (does this treatment type fall under what the
policy covers) is deliberately NOT wired into the comparison below - per
blueprint SS3.3, this is an explicit [DEV] extension point, not an oversight.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class VerifiedClaim:
    diagnosis: str
    amount: float
    date: str


@dataclass
class VerificationEscalation:
    reason: str


class Verification:
    """
    policy_visit_lookup and fraud_signal_lookup are swappable, injected
    dependencies (see Orchestrator's Dependency-Provision Rule) - never
    imported directly, so a real database and a real fraud system can be
    substituted without touching this file. matching_tolerance is a scalar
    tunable, read from Configuration by whatever constructs this instance.
    """

    def __init__(self, policy_visit_lookup, fraud_signal_lookup, matching_tolerance: float):
        self._policy_visit_lookup = policy_visit_lookup
        self._fraud_signal_lookup = fraud_signal_lookup
        self._matching_tolerance = matching_tolerance

    def process(self, extracted, customer_id: str, policy_id: str):
        # Step 1: completeness check. No lookup of any kind runs before this
        # passes - there's nothing meaningful to look up yet.
        if extracted.diagnosis is None or extracted.amount is None or extracted.date is None:
            return VerificationEscalation(reason="incomplete_extraction")

        # Step 2: record lookup.
        record = self._policy_visit_lookup(customer_id, policy_id)
        if record is None:
            return VerificationEscalation(reason="no_record_found")

        # Step 3: fraud signal check - independent of the record lookup
        # above. This is the direct implementation of the /v2 fix: fraud
        # detection is a separate mock source, never folded into the record.
        if self._fraud_signal_lookup(
            customer_id, policy_id,
            {"diagnosis": extracted.diagnosis, "amount": extracted.amount, "date": extracted.date},
        ):
            return VerificationEscalation(reason="fraud_flag")

        # Step 4: comparison.
        amount_diff = abs(extracted.amount - record["amount"])
        within_tolerance = amount_diff <= (record["amount"] * self._matching_tolerance)
        diagnosis_matches = extracted.diagnosis == record["diagnosis"]
        date_matches = extracted.date == record["date"]

        if not (within_tolerance and diagnosis_matches and date_matches):
            return VerificationEscalation(reason="mismatch")

        return VerifiedClaim(
            diagnosis=extracted.diagnosis, amount=extracted.amount, date=extracted.date,
        )

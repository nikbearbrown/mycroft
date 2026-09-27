"""
WHAT THIS FILE DOES: Wires Intake, Verification, and the Authorization Gate
together in a fixed order, refuses to run at all if it isn't configured
correctly, and stops a claim the moment any stage rejects it - it contains no
classification, comparison, or authorization logic of its own.

Dependency-Provision Rule (locked in /review pass 3, Finding 9): scalar
tunables are read directly from Configuration by the component that needs
them; swappable behavior (llm_client, the mock lookups, policy_fn) is always
constructor-injected. The Orchestrator itself accepts four already-built
components and constructs none of them - see demo/run_sample_claims.py for
the reference wiring sequence that builds those four components.
"""
from dataclasses import dataclass
from typing import Optional

from intake import IntakeEscalation
from verification import VerificationEscalation
from exceptions import MissingPolicyError


@dataclass
class ClaimResult:
    status: str  # "SETTLED" or "ESCALATED"
    reason: Optional[str] = None


class Orchestrator:
    def __init__(self, intake, verification, gate, policy_fn):
        # Construction-time validation - the /v2 fix, formally owned here.
        # This fires once, at construction, never per-claim, and is a
        # caller/wiring error, never a claim outcome.
        if policy_fn is None or not callable(policy_fn):
            raise MissingPolicyError(
                "Orchestrator requires a callable authorization policy_fn. "
                "This pipeline ships no default authorization criteria - "
                "Lemonade has not disclosed what makes a claim eligible for "
                "automatic settlement, and this design does not invent one "
                "on their behalf. Supply your own policy_fn: "
                "(verified_claim) -> bool."
            )
        self._intake = intake
        self._verification = verification
        self._gate = gate
        self._policy_fn = policy_fn

    def process_claim(self, raw_claim_text: str, customer_id: str, policy_id: str) -> ClaimResult:
        intake_result = self._intake.process(raw_claim_text)
        if isinstance(intake_result, IntakeEscalation):
            return ClaimResult(status="ESCALATED", reason=intake_result.reason)

        verification_result = self._verification.process(intake_result, customer_id, policy_id)
        if isinstance(verification_result, VerificationEscalation):
            return ClaimResult(status="ESCALATED", reason=verification_result.reason)

        gate_outcome = self._gate.decide(verification_result, self._policy_fn)
        return ClaimResult(status=gate_outcome.status, reason=gate_outcome.reason)

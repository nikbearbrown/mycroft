"""
agents/payout.py

Payout Agent — calculates a recommended settlement amount for a covered,
fraud-cleared claim. Produces a RECOMMENDATION ONLY. This agent has no
write access to any payout or settlement system — see workflow/payout_gate.py
for the code that actually enforces that a human must approve before
anything executes.

This is an illustrative implementation, not a disclosure of any real
insurer's actual system. See README.md for the full design reasoning.

DEPENDENCY NOTE: Payout has hard dependencies on BOTH Coverage's and
Fraud's conclusions — a recommendation cannot be produced for a claim that
hasn't cleared both checks. This is a genuine convergence point, not a
sequencing preference.
"""

from dataclasses import dataclass

from models.claim import Claim, AgentOutput
from providers.base import LLMProvider, ProviderResponseError


PAYOUT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "recommended_amount_aud": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": ["recommended_amount_aud", "reasoning"],
}


PAYOUT_SYSTEM_PROMPT = """You are a settlement-recommendation agent for insurance claims.

Given a covered, fraud-cleared food-spoilage claim, recommend a settlement \
amount up to the claimed spoilage value, capped at the workflow's AUD \
threshold. This is a recommendation only — you have no authority to \
execute payment, and you should state your reasoning as if a claims \
professional will read it before deciding whether to approve it."""


class PayoutCalculationError(Exception):
    """Raised when Payout cannot produce a valid recommendation, or when
    the recommended amount would exceed the workflow's threshold — either
    way, this halts and escalates to human review rather than producing
    an out-of-policy recommendation."""
    pass


@dataclass
class PayoutResult:
    recommended_amount_aud: float
    reasoning: str
    agent_output: AgentOutput


class PayoutAgent:

    def __init__(self, provider: LLMProvider, threshold_aud: float):
        self.provider = provider
        self.threshold_aud = threshold_aud

    def run(
        self,
        claim: Claim,
        coverage_conclusion: str,
        fraud_conclusion: str,
    ) -> PayoutResult:
        """
        Raises PayoutCalculationError if the provider's recommendation
        exceeds the workflow's threshold. This is checked in Python, not
        left to the model to self-enforce — a capped-amount business rule
        should not depend on the LLM correctly applying it every time.
        """
        user_message = (
            f"Claim ID: {claim.claim_id}\n"
            f"Claimed amount (AUD): {claim.claimed_amount}\n"
            f"Claim description: {claim.description}\n\n"
            f"Coverage determination: {coverage_conclusion}\n"
            f"Fraud screening conclusion: {fraud_conclusion}\n\n"
            f"Workflow threshold (AUD): {self.threshold_aud}"
        )

        try:
            response = self.provider.complete_structured(
                system_prompt=PAYOUT_SYSTEM_PROMPT,
                user_message=user_message,
                output_schema=PAYOUT_OUTPUT_SCHEMA,
                max_tokens=250,
            )
        except ProviderResponseError as e:
            raise PayoutCalculationError(f"Payout agent could not get a valid response: {e.detail}") from e

        data = response.data
        recommended_amount = float(data["recommended_amount_aud"])

        # [DEV] Business rule enforced in code, not trusted to the model:
        if recommended_amount > self.threshold_aud:
            raise PayoutCalculationError(
                f"Recommended amount {recommended_amount} exceeds threshold "
                f"{self.threshold_aud} — halting rather than producing an "
                f"out-of-policy recommendation."
            )

        return PayoutResult(
            recommended_amount_aud=recommended_amount,
            reasoning=data["reasoning"],
            agent_output=AgentOutput(
                agent_name="payout",
                conclusion=f"recommended_{recommended_amount}",
                reasoning=data["reasoning"],
                provider_name=response.provider_name,
                raw_response=response.raw_text,
            ),
        )

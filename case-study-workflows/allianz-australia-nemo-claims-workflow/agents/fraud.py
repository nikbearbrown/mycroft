"""
agents/fraud.py

Fraud Agent — screens the claim for signs of fraud, weighing Coverage's and
Weather's conclusions alongside claim history.

This is an illustrative implementation, not a disclosure of any real
insurer's actual system. See README.md for the full design reasoning.

DEPENDENCY NOTE (the one hard dependency that matters most in this
pipeline): Fraud requires Weather's conclusion to run — a "not matched"
weather result is itself one of the fraud signals this agent weighs. This
is a genuine data dependency, not a sequencing preference: Fraud's
judgment is materially different depending on what Weather found.
Reading Coverage's conclusion instead of re-deriving coverage independently
is a design-efficiency choice, not a strict requirement.

[DEV] EXTENSION POINT — FLAGGED-CLAIM BRANCH NOT BUILT: when this agent
returns "flagged", the workflow halts and raises FraudFlaggedForReview
below. No further investigation logic exists in this repo — there is no
public source describing what a real fraud-investigation queue actually
does beyond "a human reviews it," so building that process out further
would be pure invention dressed up as part of the reference design. If
your use case needs an actual investigation workflow (queue, case
assignment, resolution states), build it here and route into it from the
except block in the orchestrator instead of stopping at the halt below.
"""

from dataclasses import dataclass

from models.claim import Claim, AgentOutput
from providers.base import LLMProvider, ProviderResponseError


FRAUD_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "conclusion": {"type": "string", "enum": ["clear", "flagged"]},
        "reasoning": {"type": "string"},
    },
    "required": ["conclusion", "reasoning"],
}


FRAUD_SYSTEM_PROMPT = """You are a fraud-screening agent for low-value food-spoilage insurance claims.

Weigh the weather-verification result — an unmatched weather event is a \
significant fraud signal — alongside claim-history patterns such as \
repeated similar claims from the same policyholder. Conclude explicitly: \
clear or flagged, with your reasoning stated plainly enough for a claims \
professional to act on without needing to re-derive your logic."""


class FraudCheckError(Exception):
    """Raised when Fraud cannot produce a valid response — routes to
    human review rather than defaulting to clear or flagged."""
    pass


class FraudFlaggedForReview(Exception):
    """Raised (not just returned) when Fraud concludes 'flagged'. This is
    deliberately an exception, not a normal return value — it forces the
    orchestrator to explicitly catch and route this case rather than
    letting a flagged claim silently continue toward Payout if a future
    edit forgets to check the conclusion field."""
    def __init__(self, reasoning: str, agent_output: AgentOutput):
        self.reasoning = reasoning
        self.agent_output = agent_output
        super().__init__(f"Claim flagged for fraud review: {reasoning}")


@dataclass
class FraudResult:
    conclusion: str          # "clear" (flagged claims raise FraudFlaggedForReview instead)
    reasoning: str
    agent_output: AgentOutput


class FraudAgent:

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def run(
        self,
        claim: Claim,
        coverage_conclusion: str,
        weather_match_status: str,
        weather_reasoning: str,
        claim_history_summary: str,
    ) -> FraudResult:
        """
        Raises FraudFlaggedForReview if the conclusion is "flagged" — see
        the module-level extension-point note for why nothing further
        happens automatically in that case.
        """
        user_message = (
            f"Claim ID: {claim.claim_id}\n"
            f"Claimed amount (AUD): {claim.claimed_amount}\n\n"
            f"Coverage determination: {coverage_conclusion}\n"
            f"Weather match status: {weather_match_status}\n"
            f"Weather agent's reasoning: {weather_reasoning}\n\n"
            f"Prior claim history for this policyholder: {claim_history_summary}"
        )

        try:
            response = self.provider.complete_structured(
                system_prompt=FRAUD_SYSTEM_PROMPT,
                user_message=user_message,
                output_schema=FRAUD_OUTPUT_SCHEMA,
                max_tokens=350,
            )
        except ProviderResponseError as e:
            raise FraudCheckError(f"Fraud agent could not get a valid response: {e.detail}") from e

        data = response.data
        agent_output = AgentOutput(
            agent_name="fraud",
            conclusion=data["conclusion"],
            reasoning=data["reasoning"],
            provider_name=response.provider_name,
            raw_response=response.raw_text,
        )

        if data["conclusion"] == "flagged":
            raise FraudFlaggedForReview(data["reasoning"], agent_output)

        return FraudResult(
            conclusion=data["conclusion"],
            reasoning=data["reasoning"],
            agent_output=agent_output,
        )

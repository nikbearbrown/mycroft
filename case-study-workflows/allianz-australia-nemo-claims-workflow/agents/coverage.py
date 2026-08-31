"""
agents/coverage.py

Coverage Agent — verifies whether food spoilage arising from a severe-weather
power outage is a covered peril under the policyholder's home-contents policy.

This is an illustrative implementation, not a disclosure of any real
insurer's actual system. See README.md for the full design reasoning
behind this agent's role and its position in the pipeline.

DEPENDENCY NOTE: Coverage depends only on Planner's parsed claim context —
not on Weather or Fraud. Running it before Weather is a fail-fast choice,
not a data requirement (see README.md for the full reasoning).
"""

from dataclasses import dataclass
from typing import Optional

from models.claim import Claim, PolicyRecord, AgentOutput
from providers.base import LLMProvider, ProviderResponseError


# [DEV] This JSON Schema is the exact contract Coverage's LLM call must
# satisfy, across all 3 providers (see providers/base.py). If you change
# what Coverage outputs, update this schema AND the parsing in
# CoverageAgent.run() together — they must stay in sync.
COVERAGE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "determination": {
            "type": "string",
            "enum": ["covered", "not_covered", "ambiguous"],
        },
        "policy_clause_cited": {"type": "string"},
        "exceeds_threshold": {
            "type": "boolean",
            "description": "true if claimed_amount exceeds the workflow's AUD threshold",
        },
        "reasoning": {"type": "string"},
    },
    "required": ["determination", "policy_clause_cited", "exceeds_threshold", "reasoning"],
}


# [DEV] Constructed system prompt — not disclosed material from any real
# insurer. Refine this further if your own testing shows it under- or
# over-triggers "ambiguous".
COVERAGE_SYSTEM_PROMPT = """You are a coverage-verification agent for a home-contents insurance claims workflow.

Confirm whether food spoilage arising from a severe-weather power outage is \
covered under this policy. Cite the specific policy clause that supports \
your determination. If the claimed amount exceeds the AUD threshold for \
automated handling under this workflow, flag it as out of scope regardless \
of your coverage determination — it must be routed to standard claims \
review rather than continuing through this pipeline.

Respond with your determination, the policy clause cited, whether the \
claim exceeds the threshold, and your reasoning."""


class CoverageDecisionError(Exception):
    """Raised when Coverage cannot produce a valid determination — routes
    to human review rather than defaulting to a coverage outcome."""
    pass


@dataclass
class CoverageResult:
    determination: str          # "covered" / "not_covered" / "ambiguous"
    policy_clause_cited: str
    exceeds_threshold: bool
    reasoning: str
    agent_output: AgentOutput   # wrapped for Audit's summary and the claims-audit log


class CoverageAgent:
    """
    [DEV] EXTENSION POINT: threshold value is injected via config (see
    config.py), NOT hardcoded here — the AUD$500 threshold is a policy
    fact, not an implementation detail. If you're changing threshold
    behavior, change config.py, not this file.
    """

    def __init__(self, provider: LLMProvider, threshold_aud: float):
        self.provider = provider
        self.threshold_aud = threshold_aud

    def run(self, claim: Claim, policy_record: PolicyRecord) -> CoverageResult:
        """
        Runs the Coverage check. Raises CoverageDecisionError if the
        provider cannot produce a schema-conforming response — this
        halts the pipeline and routes to human review rather than
        letting a malformed response silently pass as a determination.

        NOTE ON DATA ACCESS: Coverage reads the policy database only. It
        must not read Weather's or Fraud's output — they haven't run yet
        at this point in the sequence (see README.md for the full
        dependency reasoning).
        """
        exceeds_threshold_precheck = claim.claimed_amount > self.threshold_aud

        user_message = self._build_user_message(claim, policy_record, exceeds_threshold_precheck)

        try:
            response = self.provider.complete_structured(
                system_prompt=COVERAGE_SYSTEM_PROMPT,
                user_message=user_message,
                output_schema=COVERAGE_OUTPUT_SCHEMA,
                max_tokens=300,
            )
        except ProviderResponseError as e:
            # [DEV] EXTENSION POINT: this currently just re-raises as a
            # CoverageDecisionError for the orchestrator to catch and route
            # to human review. If you want provider-specific retry logic
            # (e.g. retry once on the same provider before giving up),
            # add it here — it does not belong in providers/base.py, since
            # retry policy is a workflow decision, not a provider-contract one.
            raise CoverageDecisionError(f"Coverage agent could not get a valid response: {e.detail}") from e

        data = response.data

        # Defensive re-check: even though the provider adapter validates
        # against COVERAGE_OUTPUT_SCHEMA, we independently confirm the
        # threshold flag here rather than trusting the model's arithmetic —
        # exceeds_threshold_precheck is computed in Python, not by the LLM.
        exceeds_threshold = exceeds_threshold_precheck or bool(data.get("exceeds_threshold", False))

        return CoverageResult(
            determination=data["determination"],
            policy_clause_cited=data["policy_clause_cited"],
            exceeds_threshold=exceeds_threshold,
            reasoning=data["reasoning"],
            agent_output=AgentOutput(
                agent_name="coverage",
                conclusion=data["determination"],
                reasoning=data["reasoning"],
                provider_name=response.provider_name,
                raw_response=response.raw_text,
            ),
        )

    @staticmethod
    def _build_user_message(claim: Claim, policy_record: PolicyRecord, exceeds_threshold: bool) -> str:
        return (
            f"Claim ID: {claim.claim_id}\n"
            f"Policy ID: {claim.policy_id}\n"
            f"Claimed amount (AUD): {claim.claimed_amount}\n"
            f"Claim description: {claim.description}\n"
            f"Incident location: {claim.location}\n"
            f"Incident timestamp: {claim.outage_timestamp.isoformat()}\n\n"
            f"Policy record:\n"
            f"  Active: {policy_record.active}\n"
            f"  Covers food spoilage: {policy_record.covers_food_spoilage}\n"
            f"  Covers severe-weather outage: {policy_record.covers_severe_weather_outage}\n"
            f"  Policy limit (AUD): {policy_record.policy_limit_aud}\n\n"
            f"Note: claimed amount {'exceeds' if exceeds_threshold else 'does not exceed'} "
            f"the workflow's automated-handling threshold (precomputed, do not recalculate)."
        )

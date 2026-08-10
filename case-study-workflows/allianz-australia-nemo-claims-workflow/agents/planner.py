"""
agents/planner.py

Planner Agent — parses the raw claim event into structured data and starts
the pipeline. Does not assess coverage, weather, or fraud itself — it
hands off structured data only.

This is an illustrative implementation, not a disclosure of any real
insurer's actual system. See README.md for the full design reasoning.

DEPENDENCY NOTE: Planner is the first agent in the pipeline — no hard
dependency on anything upstream except the raw claim intake system.
"""

from dataclasses import dataclass
from datetime import datetime

from models.claim import Claim, AgentOutput
from providers.base import LLMProvider, ProviderResponseError


PLANNER_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "claim_id": {"type": "string"},
        "policy_id": {"type": "string"},
        "claimed_amount": {"type": "number"},
        "location": {"type": "string"},
        "incident_timestamp": {"type": "string"},
        "description": {"type": "string"},
        "missing_fields": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any required field the raw claim event did not clearly provide.",
        },
    },
    "required": [
        "claim_id", "policy_id", "claimed_amount", "location",
        "incident_timestamp", "description", "missing_fields",
    ],
}


PLANNER_SYSTEM_PROMPT = """You are a claims-intake planning agent.

Parse the raw claim event into structured fields: claim ID, policy ID, \
claimed amount, incident location, incident timestamp, and a one-sentence \
description. Do not assess coverage, fraud, or weather — hand off \
structured data only. If any required field is missing or unclear from \
the raw claim event, list it in missing_fields rather than guessing a \
value."""


class PlannerParsingError(Exception):
    """Raised when the raw claim event is missing required fields, or when
    the provider cannot produce a valid response — either way, this halts
    and routes directly to human review without proceeding to Coverage."""
    pass


@dataclass
class PlannerResult:
    claim: Claim
    agent_output: AgentOutput


class PlannerAgent:

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def run(self, raw_claim_event: str) -> PlannerResult:
        try:
            response = self.provider.complete_structured(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_message=raw_claim_event,
                output_schema=PLANNER_OUTPUT_SCHEMA,
                max_tokens=250,
            )
        except ProviderResponseError as e:
            raise PlannerParsingError(f"Planner agent could not get a valid response: {e.detail}") from e

        data = response.data
        if data["missing_fields"]:
            raise PlannerParsingError(
                f"Raw claim event is missing required field(s): {data['missing_fields']} "
                f"— routing directly to human review."
            )

        claim = Claim(
            claim_id=data["claim_id"],
            policy_id=data["policy_id"],
            customer_name="",  # [DEV] EXTENSION POINT: not parsed by this schema — add if your intake system needs it
            description=data["description"],
            claimed_amount=float(data["claimed_amount"]),
            location=data["location"],
            outage_timestamp=datetime.fromisoformat(data["incident_timestamp"]),
        )

        return PlannerResult(
            claim=claim,
            agent_output=AgentOutput(
                agent_name="planner",
                conclusion="parsed",
                reasoning="Claim parsed into structured fields; no missing required data.",
                provider_name=response.provider_name,
                raw_response=response.raw_text,
            ),
        )

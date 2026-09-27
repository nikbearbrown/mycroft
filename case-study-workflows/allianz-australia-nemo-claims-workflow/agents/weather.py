"""
agents/weather.py

Weather Agent — confirms whether a severe-weather event consistent with the
claim actually occurred, checked against an external meteorological data
source.

This is an illustrative implementation, not a disclosure of any real
insurer's actual system. See README.md for the full design reasoning.

DEPENDENCY NOTE: Weather depends only on Planner's parsed claim context
(location + timestamp). It does not read Coverage's output, and nothing
downstream requires Weather to run before Coverage — running it after
Coverage here is a fail-fast choice, not a data requirement.

IMPORTANT: a "not matched" result is NOT a denial. It is passed forward
as one input to Fraud's screening — see agents/fraud.py. Do not add
auto-deny logic here.
"""

from dataclasses import dataclass

from models.claim import Claim, AgentOutput
from providers.base import LLMProvider, ProviderResponseError


# [DEV] EXTENSION POINT: this schema assumes a weather-data lookup tool has
# already retrieved raw meteorological data and it's passed in as text in
# the user message (see _build_user_message). In a production build, this
# agent would call a real weather-data API directly as a tool call rather
# than receiving pre-fetched text — swap that in here if you want a live
# integration instead of the stub source in data/stub_scenarios.py.
WEATHER_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "match_status": {"type": "string", "enum": ["matched", "not_matched"]},
        "event_description": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "data_source_cited": {"type": "string"},
        "reasoning": {"type": "string"},
    },
    "required": ["match_status", "event_description", "confidence", "data_source_cited", "reasoning"],
}


WEATHER_SYSTEM_PROMPT = """You are a weather-verification agent for an insurance claims workflow.

Given a claimed location and incident timestamp, and the meteorological \
data provided, determine whether a severe-weather event consistent with a \
power outage occurred at that location within a reasonable window of the \
claimed time. State your confidence level and cite the specific data \
source you were given. Do not deny or approve the claim yourself — your \
job is only to report whether a matching event occurred."""


class WeatherCheckError(Exception):
    """Raised when Weather cannot produce a valid response — routes to
    human review rather than defaulting to a match/no-match outcome."""
    pass


@dataclass
class WeatherResult:
    match_status: str        # "matched" / "not_matched"
    event_description: str
    confidence: str
    data_source_cited: str
    reasoning: str
    agent_output: AgentOutput


class WeatherAgent:

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def run(self, claim: Claim, meteorological_data: str) -> WeatherResult:
        """
        NOTE ON DATA ACCESS: Weather reads the external meteorological
        data source only. It must not read Coverage's determination —
        that dependency does not exist in either direction (see README.md).
        """
        user_message = (
            f"Claimed location: {claim.location}\n"
            f"Claimed incident timestamp: {claim.outage_timestamp.isoformat()}\n\n"
            f"Meteorological data:\n{meteorological_data}"
        )

        try:
            response = self.provider.complete_structured(
                system_prompt=WEATHER_SYSTEM_PROMPT,
                user_message=user_message,
                output_schema=WEATHER_OUTPUT_SCHEMA,
                max_tokens=300,
            )
        except ProviderResponseError as e:
            raise WeatherCheckError(f"Weather agent could not get a valid response: {e.detail}") from e

        data = response.data
        return WeatherResult(
            match_status=data["match_status"],
            event_description=data["event_description"],
            confidence=data["confidence"],
            data_source_cited=data["data_source_cited"],
            reasoning=data["reasoning"],
            agent_output=AgentOutput(
                agent_name="weather",
                conclusion=data["match_status"],
                reasoning=data["reasoning"],
                provider_name=response.provider_name,
                raw_response=response.raw_text,
            ),
        )

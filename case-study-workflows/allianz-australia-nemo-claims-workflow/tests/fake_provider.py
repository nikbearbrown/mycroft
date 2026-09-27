"""
tests/fake_provider.py

A test double for LLMProvider. Returns pre-scripted responses instead of
calling any real API — this is what lets tests/test_workflow.py run
without API keys or network access, and what lets it deterministically
exercise the fail-fast and no-weather-match paths without depending on
what a real model happens to decide.

[DEV] This is NOT one of the three "real" providers (Claude/OpenAI/
Gemini) — it exists purely for testing. It is not registered in
providers/__init__.py's factory and should never be selected via
NEMO_PROVIDER.
"""

from providers.base import LLMProvider, StructuredResponse

# Each agent's system prompt contains a distinctive phrase — used here to
# identify which agent is calling, without requiring any agent file to be
# modified for testability.
AGENT_PROMPT_MARKERS = {
    "planner": "claims-intake planning agent",
    "coverage": "coverage-verification agent",
    "weather": "weather-verification agent",
    "fraud": "fraud-screening agent",
    "payout": "settlement-recommendation agent",
    "audit": "claims-audit summarization agent",
}


class FakeProvider(LLMProvider):
    """
    Scripted per scenario: scripted_responses maps agent name
    ("planner", "coverage", ...) to the dict that agent's schema expects
    back. See tests/test_workflow.py for how each scenario's script is
    built.
    """

    def __init__(self, scripted_responses: dict):
        self._scripted = scripted_responses
        self.call_log = []

    def complete_structured(self, system_prompt, user_message, output_schema, max_tokens):
        agent_name = self._identify_agent(system_prompt)
        self.call_log.append(agent_name)

        if agent_name not in self._scripted:
            raise KeyError(
                f"FakeProvider has no scripted response for agent='{agent_name}'. "
                f"Scripted agents: {list(self._scripted.keys())}"
            )

        data = self._scripted[agent_name]
        return StructuredResponse(data=data, raw_text=str(data), provider_name="fake")

    @staticmethod
    def _identify_agent(system_prompt: str) -> str:
        for agent_name, marker in AGENT_PROMPT_MARKERS.items():
            if marker in system_prompt:
                return agent_name
        raise KeyError(f"Could not identify agent from system_prompt: {system_prompt[:80]!r}")

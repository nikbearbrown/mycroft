"""
WHAT THIS FILE DOES: Returns deterministic, scenario-keyed canned responses,
so the entire pipeline is runnable with zero cost and zero external
dependency out of the box.

Canned responses for known demo/test scenarios only. This is not model
behavior - replace the provider in Configuration for real classification.

This is shipped, working, intentional infrastructure - not a [DEV]
customization point. The [DEV] marker belongs on the *choice* of provider in
Configuration, not on this file.
"""
import json

from llm_provider.base import LLMProvider
from fixtures import FAKE_LLM_RESPONSES

_GENERIC_LOW_CONFIDENCE_RESPONSE = json.dumps({"claim_type": "unclassified", "confidence": 0.0})


class FakeAdapter(LLMProvider):
    def call(self, instruction: str, input_text: str) -> str:
        scenario = FAKE_LLM_RESPONSES.get(input_text)
        if scenario is None:
            # Unrecognized input degrades to a low-confidence/unclassified
            # response rather than fabricating a plausible-looking result.
            return _GENERIC_LOW_CONFIDENCE_RESPONSE
        return json.dumps(scenario)

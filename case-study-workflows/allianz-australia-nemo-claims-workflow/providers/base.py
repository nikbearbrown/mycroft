"""
providers/base.py

The single seam between every agent and whichever LLM actually answers.

Agents never import anthropic / openai / google.generativeai directly —
they only ever call an LLMProvider instance. This is what makes provider
choice a config change (see config.py) instead of a code change scattered
across 7 agent files.

[DEV] This is the file to touch if you're fixing one provider's adapter
or adding a fourth provider entirely. Every adapter (claude_provider.py,
openai_provider.py, gemini_provider.py) must implement complete_structured()
and return a StructuredResponse whose `.data` conforms to the output_schema
it was given.

PROVIDER VERIFICATION STATUS: all three adapters in this repo are
design-complete and syntax-verified. None has been exercised against live
model behavior in this build (no network access in the build environment).
Runtime-verifying at least one provider, with your own API key, is the
first thing you should do after cloning this repo — see README.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class StructuredResponse:
    """What every provider adapter returns, regardless of which provider
    actually answered."""
    data: Dict[str, Any]      # validated against the output_schema passed in
    raw_text: str             # unparsed provider response — kept for audit/debug trail
    provider_name: str        # which provider answered ("claude" / "openai" / "gemini")


class LLMProvider(ABC):
    """Every provider adapter must satisfy this contract. Agents code
    against this interface only — see agents/coverage.py for the pattern
    every other agent follows."""

    @abstractmethod
    def complete_structured(
        self,
        system_prompt: str,
        user_message: str,
        output_schema: Dict[str, Any],   # JSON Schema — the agreed convention across all 3 providers
        max_tokens: int,
    ) -> StructuredResponse:
        """Return a response whose `.data` conforms to output_schema.

        [DEV] Each adapter is responsible for:
        1. Translating output_schema into whatever structured-output
           mechanism its own provider supports:
             - Claude: a tool-use tool definition, tool_choice forcing that tool
             - OpenAI: JSON mode / structured outputs with the schema attached
             - Gemini: response_schema in GenerationConfig
        2. Validating the raw response against output_schema BEFORE
           returning. A malformed response is an adapter-level failure —
           the calling agent should never have to defensively check
           whether `.data` matches what it asked for.
        3. Raising ProviderResponseError (below) if the provider cannot
           produce a schema-conforming response after its own retry logic,
           rather than returning a partially-valid StructuredResponse.
        """
        raise NotImplementedError


class ProviderResponseError(Exception):
    """Raised by an adapter when it cannot get a schema-conforming response
    from its provider. Agents catch this and route to Cyber/human escalation
    rather than proceeding with unvalidated data — see agents/coverage.py."""
    def __init__(self, provider_name: str, detail: str):
        self.provider_name = provider_name
        self.detail = detail
        super().__init__(f"[{provider_name}] structured response failed: {detail}")

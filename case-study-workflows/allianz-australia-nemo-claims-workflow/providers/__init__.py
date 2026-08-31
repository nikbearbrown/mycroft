"""
providers/__init__.py

Factory that turns config.provider_name into a concrete LLMProvider
instance. This is the ONE place that knows about all three concrete
adapter classes — agents never import them directly (they only ever
receive an LLMProvider instance via dependency injection, see
workflow/orchestrator.py).

[DEV] EXTENSION POINT: adding a 4th provider means adding a branch here
AND a new file alongside claude_provider.py / openai_provider.py /
gemini_provider.py — nothing else in this repo needs to change.
"""

from config import WorkflowConfig, ConfigError
from providers.base import LLMProvider


def get_provider(config: WorkflowConfig) -> LLMProvider:
    if config.provider_name == "claude":
        from providers.claude_provider import ClaudeProvider
        if not config.anthropic_api_key:
            raise ConfigError("NEMO_PROVIDER=claude but ANTHROPIC_API_KEY is not set.")
        return ClaudeProvider(api_key=config.anthropic_api_key)

    if config.provider_name == "openai":
        from providers.openai_provider import OpenAIProvider
        if not config.openai_api_key:
            raise ConfigError("NEMO_PROVIDER=openai but OPENAI_API_KEY is not set.")
        return OpenAIProvider(api_key=config.openai_api_key)

    if config.provider_name == "gemini":
        from providers.gemini_provider import GeminiProvider
        if not config.gemini_api_key:
            raise ConfigError("NEMO_PROVIDER=gemini but GEMINI_API_KEY is not set.")
        return GeminiProvider(api_key=config.gemini_api_key)

    raise ConfigError(f"Unknown provider: {config.provider_name}")

"""
config.py

Single place this workflow reads its configurable values from. Nothing
downstream should read environment variables directly — they read
WorkflowConfig instead. See .env.example for the variables this expects.

[DEV] EXTENSION POINT: if you add a 4th provider, add its API-key
variable here and to .env.example, and add a branch in
providers/__init__.py's get_provider() factory.
"""

import os
from dataclasses import dataclass


SUPPORTED_PROVIDERS = ("claude", "openai", "gemini")


class ConfigError(Exception):
    pass


@dataclass
class WorkflowConfig:
    provider_name: str
    threshold_aud: float
    anthropic_api_key: str | None
    openai_api_key: str | None
    gemini_api_key: str | None

    @classmethod
    def from_env(cls) -> "WorkflowConfig":
        provider_name = os.environ.get("NEMO_PROVIDER", "claude").lower()
        if provider_name not in SUPPORTED_PROVIDERS:
            raise ConfigError(
                f"NEMO_PROVIDER='{provider_name}' is not supported. "
                f"Choose one of: {SUPPORTED_PROVIDERS}."
            )

        # [DEV] The AUD threshold is a policy fact, not a code constant —
        # it's read here from config, not hardcoded in any agent.
        threshold_raw = os.environ.get("NEMO_THRESHOLD_AUD", "500")
        try:
            threshold_aud = float(threshold_raw)
        except ValueError:
            raise ConfigError(f"NEMO_THRESHOLD_AUD='{threshold_raw}' is not a valid number.")

        return cls(
            provider_name=provider_name,
            threshold_aud=threshold_aud,
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            gemini_api_key=os.environ.get("GEMINI_API_KEY"),
        )

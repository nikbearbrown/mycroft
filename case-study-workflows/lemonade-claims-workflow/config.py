"""
WHAT THIS FILE DOES: Collects the settings an implementer actually needs to
change - provider choice, API key, confidence threshold, matching tolerance -
in one place, so no other component invents its own default internally.

Decision locked (Option 1, this session): one file. LLM_API_KEY is sourced
only from the environment, never given a default value, and kept in its own
clearly-commented section - never interleaved with the [DEV]-labeled tunables.
"""
import os

from exceptions import UnknownProviderError, MissingAPIKeyError

_KNOWN_PROVIDERS = {"fake", "claude", "gpt", "gemini"}

# [DEV] Illustrative default confidence threshold for Intake's classification
# confidence. Not a disclosed Lemonade figure - rewrite for your own claim
# types and your own chosen model's response tendencies.
CONFIDENCE_THRESHOLD_DEFAULT = 0.75

# [DEV] Illustrative default tolerance for Verification's amount-matching
# comparison (relative, e.g. 0.05 = 5%). Not a disclosed Lemonade figure.
MATCHING_TOLERANCE_DEFAULT = 0.05


class Configuration:
    def __init__(self):
        # [DEV] Provider selection. Defaults to "fake" so this pipeline is
        # runnable with zero cost and zero external dependency out of the
        # box. Set LLM_PROVIDER to "claude", "gpt", or "gemini" (plus
        # LLM_API_KEY) to use a real model. Leaving this unset is itself a
        # deliberate, known-consequence choice - not an oversight.
        self.llm_provider = os.environ.get("LLM_PROVIDER", "fake").lower()
        if self.llm_provider not in _KNOWN_PROVIDERS:
            raise UnknownProviderError(
                f"Unrecognized LLM_PROVIDER {self.llm_provider!r}. "
                f"Expected one of: {sorted(_KNOWN_PROVIDERS)}."
            )

        # --- Secret: sourced only from the environment. No default value,
        # ever. Never stored alongside, or interleaved with, the tunables
        # below. ---
        self.llm_api_key = os.environ.get("LLM_API_KEY")
        if self.llm_provider != "fake" and not self.llm_api_key:
            raise MissingAPIKeyError(
                f"LLM_PROVIDER is set to {self.llm_provider!r}, which requires "
                f"a real API key, but LLM_API_KEY is not set in the environment."
            )

        # [DEV] Tunable business defaults - illustrative, not disclosed figures.
        self.confidence_threshold = float(
            os.environ.get("CONFIDENCE_THRESHOLD", CONFIDENCE_THRESHOLD_DEFAULT)
        )
        self.matching_tolerance = float(
            os.environ.get("MATCHING_TOLERANCE", MATCHING_TOLERANCE_DEFAULT)
        )

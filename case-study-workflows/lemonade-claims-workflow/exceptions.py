"""
WHAT THIS FILE DOES: Defines the shared exception hierarchy for wiring and
configuration failures - kept categorically separate from claim-level
ESCALATED outcomes, so a try/except written against claim outcomes can never
accidentally swallow a configuration mistake.

Locked in /review, Finding 2.
"""


class PipelineConfigurationError(Exception):
    """
    Base class for every wiring/configuration error in this pipeline. Never
    represents a claim-level outcome - always a caller/programmer error that
    should fail loudly, once, before any claim is processed.
    """


class MissingPolicyError(PipelineConfigurationError):
    """
    Raised by Orchestrator construction when no valid, callable authorization
    policy_fn is supplied. This pipeline ships no default authorization
    criteria by design - see DESIGN_DECISIONS.md, "Authorization Gate - no
    shipped default."
    """


class UnknownProviderError(PipelineConfigurationError):
    """Raised by Configuration when LLM_PROVIDER is not a recognized value."""


class MissingAPIKeyError(PipelineConfigurationError):
    """
    Raised by Configuration when a real LLM provider is selected but no
    LLM_API_KEY is present in the environment.
    """

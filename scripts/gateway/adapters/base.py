"""The contract every provider adapter satisfies.

An adapter's ONE job is to make a call and report what happened in
provider-neutral terms. It does not log, does not price, does not retry,
and does not decide which model to use -- those belong to the layers above.
That separation is what lets the rest of the gateway be tested with zero
network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

# Ways a call can fail at the provider. These are a subset of the logbook's
# `outcome` vocabulary -- a test pins that relationship so the two cannot drift.
FAILURE_KINDS = frozenset({"provider_error", "timeout"})


class ProviderError(RuntimeError):
    """A call failed at the provider: refused, rate-limited, errored, timed out."""

    def __init__(self, message: str, *, provider: str, model: str,
                 kind: str = "provider_error") -> None:
        super().__init__(message)
        if kind not in FAILURE_KINDS:
            raise ValueError(f"kind {kind!r} is not one of {sorted(FAILURE_KINDS)}")
        self.provider = provider
        self.model = model
        self.kind = kind


@dataclass(frozen=True)
class LLMResponse:
    """What every adapter returns, whatever provider produced it."""

    text: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int

    def __post_init__(self) -> None:
        if self.tokens_in < 0 or self.tokens_out < 0:
            raise ValueError("token counts must be non-negative")
        if self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")


class LLMAdapter(Protocol):
    """Structural interface -- an adapter just needs these attributes."""

    provider: str

    def complete(self, *, model: str, prompt: str, max_tokens: int) -> LLMResponse:
        """Make one call. Raise ProviderError if the provider failed."""
        ...
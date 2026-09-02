"""The one door. Every model request goes through here.

There is no public method that returns a response without having written a
logbook row first. That is the whole point: if logging were something the
caller did afterwards, someone would eventually forget -- and a missing row
does not look like an error, it looks like a cheaper month.

This layer does NOT decide which tier to use. The caller names a tier, or
Sprint 3's router does. Keeping the decision out of here is what lets the
routing logic be tested as a pure function.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

from gateway.adapters.base import LLMAdapter, LLMResponse, ProviderError
from gateway.logbook import Logbook


class UnknownTier(KeyError):
    """Raised when a caller names a tier that is not configured."""


class NoAdapterForProvider(KeyError):
    """Raised when a tier names a provider with no registered adapter."""


@dataclass(frozen=True)
class CallResult:
    """What a call produced, plus the request it belongs to."""

    response: LLMResponse
    request_id: str
    record: dict[str, Any]


class GatewayClient:
    def __init__(self, *, logbook: Logbook,
                 adapters: dict[str, LLMAdapter],
                 tiers: dict[str, dict[str, str]],
                 policy_version: str,
                 clock: Callable[[], float] = time.perf_counter) -> None:
        self.logbook = logbook
        self.adapters = adapters
        self.tiers = tiers
        self.policy_version = policy_version
        # Injectable so tests can assert exact latencies instead of
        # whatever the machine happened to do.
        self.clock = clock

    def call(self, *, task_type: str, caller: str, tier: str, prompt: str,
             max_tokens: int = 1024, request_id: str | None = None,
             routing_reason: str = "policy") -> CallResult:
        """Make one attempt and record it. Failures are recorded too.

        Pass an existing `request_id` to attach this attempt to a request
        already in flight -- that is how Sprint 4's escalation keeps a
        retry inside the same logical request instead of starting a new one.
        """
        spec = self.tiers.get(tier)
        if spec is None:
            raise UnknownTier(f"tier {tier!r} is not in the tier config")

        provider, model = spec["provider"], spec["model"]

        adapter = self.adapters.get(provider)
        if adapter is None:
            raise NoAdapterForProvider(
                f"tier {tier!r} names provider {provider!r}, which has no adapter"
            )

        # Refuse before spending: a call you cannot price is a call you
        # cannot account for. This raises UnknownModelPrice *before* the
        # adapter is touched, so no money is spent on an unloggable request.
        self.logbook.prices.rates(provider, model)

        if request_id is None:
            request_id = self.logbook.begin_request(task_type=task_type, caller=caller)

        started = self.clock()
        try:
            response = adapter.complete(model=model, prompt=prompt, max_tokens=max_tokens)
        except ProviderError as exc:
            # A failed attempt still consumed time and is still evidence.
            self.logbook.record_attempt(
                request_id, provider=provider, model=model, tier=tier,
                routing_reason=routing_reason, policy_version=self.policy_version,
                tokens_in=0, tokens_out=0,
                latency_ms=self._elapsed_ms(started),
                outcome=exc.kind, notes=str(exc),
            )
            raise

        record = self.logbook.record_attempt(
            request_id, provider=provider, model=model, tier=tier,
            routing_reason=routing_reason, policy_version=self.policy_version,
            tokens_in=response.tokens_in, tokens_out=response.tokens_out,
            latency_ms=self._elapsed_ms(started),
            outcome="ok",
        )
        return CallResult(response=response, request_id=request_id, record=record)

    def _elapsed_ms(self, started: float) -> int:
        return max(0, int(round((self.clock() - started) * 1000)))
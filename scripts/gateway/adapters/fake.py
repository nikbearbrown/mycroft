"""A deterministic adapter that never touches the network.

This is the most-used adapter in the project. Every test of the client,
the router, and the escalation logic runs against it, which is what keeps
the suite fast, free, and independent of any provider's uptime.

Behaviour is scriptable so a test can stage the exact sequence it needs --
notably "cheap model fails, strong model succeeds", the case the whole
gateway exists to handle.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from gateway.adapters.base import LLMResponse, ProviderError


class FakeAdapter:
    """Returns scripted responses, or a deterministic default."""

    provider = "fake"

    def __init__(self, *, provider: str = "fake",
                 default_text: str = "fake response",
                 default_latency_ms: int = 10) -> None:
        self.provider = provider
        self.default_text = default_text
        self.default_latency_ms = default_latency_ms
        self._script: deque[dict[str, Any]] = deque()
        # Every call is recorded so tests can assert which model was used.
        self.calls: list[dict[str, Any]] = []

    # -- scripting -------------------------------------------------------

    def queue_response(self, text: str, *, latency_ms: int | None = None) -> "FakeAdapter":
        """Stage one successful response. Returns self, so calls chain."""
        self._script.append({"text": text, "latency_ms": latency_ms})
        return self

    def queue_error(self, *, kind: str = "provider_error",
                    message: str = "scripted failure") -> "FakeAdapter":
        """Stage one failure. Returns self, so calls chain."""
        self._script.append({"error": {"kind": kind, "message": message}})
        return self

    # -- the adapter contract --------------------------------------------

    def complete(self, *, model: str, prompt: str, max_tokens: int) -> LLMResponse:
        self.calls.append({"model": model, "prompt": prompt, "max_tokens": max_tokens})

        step = self._script.popleft() if self._script else {}

        if error := step.get("error"):
            raise ProviderError(
                error["message"], provider=self.provider, model=model,
                kind=error["kind"],
            )

        text = step.get("text", self.default_text)
        latency = step.get("latency_ms")
        if latency is None:
            latency = self.default_latency_ms

        # Deterministic token counts: same input always yields the same
        # numbers, so cost assertions in tests are exact rather than fuzzy.
        return LLMResponse(
            text=text,
            provider=self.provider,
            model=model,
            tokens_in=len(prompt.split()),
            tokens_out=len(text.split()),
            latency_ms=latency,
        )
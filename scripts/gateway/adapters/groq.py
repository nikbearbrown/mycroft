"""Groq adapter -- the first real provider.

Three deliberate choices:

1. The SDK import is LAZY. The gateway core has no third-party runtime
   dependency, and the whole test suite runs without `groq` installed. You
   only pay for the dependency at the moment you make a real call.

2. Errors are classified DEFENSIVELY, by inspecting the exception rather
   than importing the SDK's exception classes. Verified against a real 401
   on 2026-09-02: it landed as provider_error, correctly not timeout.
   `notes` preserves the raw error text so nothing is lost.

3. Inline reasoning is STRIPPED from the answer text. Groq's reasoning
   models do not all expose reasoning the same way: openai/gpt-oss keeps it
   out of the content field, while qwen/qwen3.6-27b returns it inline in
   <think>...</think> tags (observed 2026-09-10). Left in, every validator
   that checks the answer would fail on the strong tier -- making the
   strongest model look like the worst one. Reasoning tokens are still
   billed, so tokens_out keeps the full count and the cost stays honest.
"""

from __future__ import annotations

import re
from typing import Any

from gateway.adapters.base import LLMResponse, ProviderError

DEFAULT_TIMEOUT_S = 30.0

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def strip_reasoning(text: str) -> str:
    """Return only the answer, with any inline reasoning removed.

    A closed <think>...</think> block is removed. An opening tag with no
    close means the response was cut off mid-reasoning: everything after it
    is reasoning and there is no answer, so the result is empty -- which the
    gate's empty-response check then catches.
    """
    cleaned = _THINK_BLOCK.sub("", text)
    open_at = cleaned.lower().find("<think>")
    if open_at != -1:
        cleaned = cleaned[:open_at]
    return cleaned.strip()


class GroqAdapter:
    provider = "groq"

    def __init__(self, *, api_key: str | None = None, client: Any = None,
                 timeout_s: float = DEFAULT_TIMEOUT_S) -> None:
        """Pass `client` to inject a stub in tests; pass `api_key` for real use."""
        self.timeout_s = timeout_s
        if client is not None:
            self._client = client
            return

        if not api_key:
            raise ValueError(
                "GroqAdapter needs an api_key (from GROQ_API_KEY) or an injected client"
            )
        try:
            import groq  # noqa: PLC0415 -- lazy on purpose
        except ImportError as exc:
            raise ImportError(
                "the 'groq' package is not installed. Uncomment it in "
                "scripts/gateway/requirements.txt and pip install it."
            ) from exc
        self._client = groq.Groq(api_key=api_key, timeout=timeout_s)

    def complete(self, *, model: str, prompt: str, max_tokens: int) -> LLMResponse:
        try:
            raw = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
        except Exception as exc:
            raise self._classify(exc, model) from exc

        return self._to_response(raw, model)

    # -- helpers ----------------------------------------------------------

    def _classify(self, exc: Exception, model: str) -> ProviderError:
        name = type(exc).__name__.lower()
        text = str(exc).lower()
        status = getattr(exc, "status_code", None)

        is_timeout = "timeout" in name or "timeout" in text
        kind = "timeout" if is_timeout else "provider_error"

        # Rate limiting is the failure already documented in logs/RUN_LOG.md
        # (Groq token limit at company #33 of 50). Flag it explicitly in the
        # message so it is greppable in the logbook's `notes`.
        if status == 429 or "ratelimit" in name or "rate limit" in text:
            marker = "rate_limit: "
        else:
            marker = ""

        return ProviderError(
            f"{marker}{type(exc).__name__}: {exc}",
            provider=self.provider, model=model, kind=kind,
        )

    def _to_response(self, raw: Any, model: str) -> LLMResponse:
        usage = getattr(raw, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", None)
        tokens_out = getattr(usage, "completion_tokens", None)

        # Never invent token counts. Without them there is no honest cost,
        # and a zero would price this call at $0 -- an invented number that
        # would quietly flatter whichever tier produced it.
        if tokens_in is None or tokens_out is None:
            raise ProviderError(
                "response carried no usage token counts; cannot price this call",
                provider=self.provider, model=model, kind="provider_error",
            )

        try:
            content = raw.choices[0].message.content or ""
        except (AttributeError, IndexError) as exc:
            raise ProviderError(
                f"unexpected response shape: {exc}",
                provider=self.provider, model=model, kind="provider_error",
            ) from exc

        return LLMResponse(
            text=strip_reasoning(content),
            provider=self.provider,
            model=model,
            tokens_in=int(tokens_in),
            # Full billed count, reasoning included -- see choice 3 above.
            tokens_out=int(tokens_out),
            # The client measures wall-clock latency; the adapter does not
            # duplicate that. See client.py.
            latency_ms=0,
        )
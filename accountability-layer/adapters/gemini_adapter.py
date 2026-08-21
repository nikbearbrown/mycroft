"""
Gemini adapter — wraps Google Gemini API to satisfy the accountability layer contract.
Requires: pip install google-genai
Requires: GEMINI_API_KEY environment variable

Rate-limit strategy (free tier):
  - PerDay  (RPD): fail immediately — quota gone until midnight UTC, no point retrying.
  - PerMinute (RPM/TPM): exponential backoff, honouring the retryDelay hint from the API.
      wait = max(api_hint, BASE_BACKOFF * 2^attempt) + random jitter

Token hygiene:
  - Context is truncated to CONTEXT_CHAR_LIMIT characters before sending.
    ~4 chars ≈ 1 token; limit keeps each request well under the free-tier TPM ceiling.
  - A throttle gap of MIN_REQUEST_GAP_S seconds is enforced between consecutive
    calls to stay under the RPM ceiling even without hitting a 429.
"""

from __future__ import annotations

import os
import re
import time
import random
from parser import AgentResponse, _parse_response
from directive import DirectiveVersion


# ── Retry config ────────────────────────────────────────────────────────────────
MAX_RETRIES       = 5      # attempts on per-minute 429s before giving up
BASE_BACKOFF      = 2.0    # seconds — base for 2^attempt calculation
JITTER_RANGE      = 1.0    # ± random seconds added to every wait
MIN_REQUEST_GAP_S = 1.0    # mandatory pause between ALL API calls (RPM guard)

# ── Token hygiene ────────────────────────────────────────────────────────────────
CONTEXT_CHAR_LIMIT = 8_000   # ~2 000 tokens; keeps TPM comfortable on free tier
CONTEXT_TRUNCATION_NOTE = "\n[context truncated — original exceeded token budget]"


class RateLimitDailyError(Exception):
    """Daily quota exhausted — no point retrying until midnight UTC."""


class RateLimitMinuteError(Exception):
    """Per-minute quota exhausted — retries exhausted without success."""


# ── Helpers ───────────────────────────────────────────────────────────────────────

def _parse_retry_delay(error_str: str) -> float:
    """Extract the retryDelay hint (seconds) from the 429 error string."""
    m = re.search(r"'retryDelay':\s*'(\d+(?:\.\d+)?)s'", error_str)
    if m:
        return float(m.group(1))
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", error_str, re.IGNORECASE)
    return float(m.group(1)) if m else BASE_BACKOFF


def _is_daily_limit(error_str: str) -> bool:
    """True if the 429 includes a PerDay quota violation."""
    return "PerDay" in error_str or "per_day" in error_str.lower()


def _is_rate_limit(exc: Exception) -> bool:
    s = str(exc)
    return "429" in s or "RESOURCE_EXHAUSTED" in s


def _backoff_wait(attempt: int, api_hint: float) -> float:
    """
    Exponential backoff honouring the API's retry hint.
    wait = max(api_hint, BASE_BACKOFF * 2^attempt) + jitter
    """
    exponential = BASE_BACKOFF * (2 ** attempt)
    return max(api_hint, exponential) + random.uniform(0, JITTER_RANGE)


def _trim_context(context: str) -> str:
    """Truncate context to CONTEXT_CHAR_LIMIT to avoid burning token quota."""
    if len(context) <= CONTEXT_CHAR_LIMIT:
        return context
    return context[:CONTEXT_CHAR_LIMIT] + CONTEXT_TRUNCATION_NOTE


# ── Adapter factory ───────────────────────────────────────────────────────────────

# Tracks last call time across all adapter instances (module-level throttle)
_last_call_ts: float = 0.0


def make_gemini_adapter(
    model: str = "gemini-2.5-flash",
    temperature: float = 0.0,
    seed: int | None = None,
):
    """
    Returns a call_agent_fn compatible with run_validation_loop.

    temperature=0.0 + fixed seed → deterministic output within a model version.
    seed=None disables the determinism hint (Gemini default sampling).

    Raises:
        EnvironmentError       — GEMINI_API_KEY not set
        RateLimitDailyError    — daily quota exhausted (switch model or wait)
        RateLimitMinuteError   — per-minute retries exhausted
    """
    def adapter(subject: str, context: str, directive: DirectiveVersion) -> AgentResponse:
        global _last_call_ts

        from google import genai
        from google.genai import types

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set. "
                "Get a free key at https://aistudio.google.com"
            )

        client = genai.Client(api_key=api_key)

        # ── Token hygiene: trim context before building prompt ──
        trimmed_context = _trim_context(context) if context else ""

        prompt = f"Subject: {subject}"
        if trimmed_context.strip():
            prompt += f"\n\nContext:\n{trimmed_context}"

        # ── RPM throttle: enforce minimum gap between calls ──
        elapsed = time.monotonic() - _last_call_ts
        if elapsed < MIN_REQUEST_GAP_S:
            time.sleep(MIN_REQUEST_GAP_S - elapsed)

        last_exc: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                _last_call_ts = time.monotonic()
                gen_config = types.GenerateContentConfig(
                    system_instruction=directive.text,
                    temperature=temperature,
                    max_output_tokens=8192,
                )
                # Seed is a determinism hint — pass only when explicitly set.
                # Gemini honours seed + temperature=0 for reproducible output
                # within the same model version. Not guaranteed across versions.
                if seed is not None:
                    gen_config.seed = seed

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=gen_config,
                )
                return _parse_response(response.text)

            except Exception as exc:
                exc_str = str(exc)

                if not _is_rate_limit(exc):
                    raise  # not a rate-limit error — propagate immediately

                if _is_daily_limit(exc_str):
                    raise RateLimitDailyError(
                        f"Daily quota exhausted for '{model}'. "
                        f"Switch to a different model or wait until midnight UTC. "
                        f"Check quota: https://aistudio.google.com/rate-limit"
                    ) from exc

                # Per-minute limit — back off and retry
                last_exc = exc
                if attempt == MAX_RETRIES - 1:
                    break

                api_hint = _parse_retry_delay(exc_str)
                wait     = _backoff_wait(attempt, api_hint)
                time.sleep(wait)

        raise RateLimitMinuteError(
            f"Per-minute quota exhausted for '{model}' after "
            f"{MAX_RETRIES} attempts. Try again in a moment."
        ) from last_exc

    return adapter

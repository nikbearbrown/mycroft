"""
LangFuse wiring — Week 9 analyst-skeleton observability.

Wraps existing accountability-layer call sites from the *outside* so tool
calls and each LLM attempt show up as traced spans in a self-hosted LangFuse
instance, without changing middleware.py or the adapters' contracts.

LangFuse traces *what happened* — data flow, latency, timeline. It does not
verify correctness or catch hallucination; that job stays with
consistency.py (reproducibility), claims.py (claim extraction), and
verification.py (checking claimed numbers against the actual source).

Configuration is via environment variables (LANGFUSE_PUBLIC_KEY,
LANGFUSE_SECRET_KEY, LANGFUSE_HOST), read implicitly by the langfuse SDK.
Without them configured, @observe()-wrapped calls still execute normally
(the SDK disables itself and logs a warning) — safe for tests and for
running without a LangFuse instance up.
"""

from __future__ import annotations

from typing import Callable

from langfuse import observe


def make_traced_adapter(adapter_fn: Callable, name: str) -> Callable:
    """
    Wrap a call_agent_fn adapter — (subject, context, directive) -> AgentResponse
    (see adapters/__init__.py) — so each invocation is recorded as a LangFuse
    generation span (latency, input/output; token/cost fields are blank until
    the adapters surface usage metadata — not yet implemented, see
    financial_grader.py).

    run_validation_loop (middleware.py) may call the wrapped adapter up to
    twice (attempt 1, corrective attempt 2); each call produces its own
    generation span. Exceptions such as StructuralParseError are logged by
    LangFuse and then re-raised unchanged, so ADR-07's retry/halt logic in
    middleware.py is unaffected by this wrapping.
    """
    return observe(name=name, as_type="generation")(adapter_fn)

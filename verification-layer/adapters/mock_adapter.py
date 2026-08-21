"""
Mock adapter — no LLM required.
Used for testing guardrail behaviour (parse failures, retry loop, halt).

Three failure modes:
  none            — always succeeds on first attempt
  retry_success   — first attempt fails structurally, retry succeeds (ADR-07 happy path)
  halt            — both attempts fail, pipeline halts (ADR-07 worst case)
"""

from __future__ import annotations

from parser import AgentResponse, StructuralParseError, _parse_response
from directive import DirectiveVersion

_VALID_TEMPLATE = (
    "<thought_log>\n"
    "  Subject: {subject}\n"
    "  Context: {context}\n"
    "  {note}\n"
    "  Reasoning: evaluated all available inputs and reached a conclusion.\n"
    "</thought_log>\n"
    "<conclusion>\n"
    "  Mock response for: {subject}\n"
    "  {note}\n"
    "</conclusion>"
)

_INVALID_RESPONSE = (
    "Sure! Here is my analysis of your request. "
    "I considered several factors and think the answer is probably yes, "
    "though it depends on the context. Let me know if you need more detail."
)


def make_mock_adapter(failure_mode: str = "none"):
    """
    failure_mode:
        "none"          — succeeds on attempt 1
        "retry_success" — fails on attempt 1 (PARSE_FAILURE), succeeds on attempt 2
        "halt"          — fails on both attempts (HALT)
    """
    if failure_mode not in ("none", "retry_success", "halt"):
        raise ValueError(f"Unknown failure_mode: {failure_mode!r}")

    call_count = {"n": 0}

    def adapter(subject: str, context: str, directive: DirectiveVersion) -> AgentResponse:
        call_count["n"] += 1
        n = call_count["n"]

        if failure_mode == "none":
            return _parse_response(_VALID_TEMPLATE.format(
                subject=subject,
                context=context or "none provided",
                note="No failures simulated.",
            ))

        if failure_mode == "retry_success":
            if n == 1:
                raise StructuralParseError(
                    "Simulated structural failure on attempt 1",
                    _INVALID_RESPONSE,
                )
            return _parse_response(_VALID_TEMPLATE.format(
                subject=subject,
                context=context or "none provided",
                note="Recovered on retry with corrective directive.",
            ))

        if failure_mode == "halt":
            raise StructuralParseError(
                f"Simulated structural failure on attempt {n}",
                _INVALID_RESPONSE + f" (attempt {n})",
            )

    return adapter

"""
Fixture adapter — deterministic stand-in agent, no LLM required.

Sibling of mock_adapter.py, different purpose:
  mock_adapter    — tests the ADR-07 guardrail itself (parse failure, retry, halt).
                    You do not control what it concludes.
  fixture_adapter — tests logic that consumes a conclusion (e.g. cross-agent
                    comparison). You choose the conclusion text up front, so the
                    correct answer is known before the test runs.

Satisfies the same adapter contract as every other adapter here:
    (subject: str, context: str, directive: DirectiveVersion) -> AgentResponse

The returned text is wrapped in the two required XML blocks and routed through
the real parser, so a fixture response is structurally indistinguishable from a
live model response that happened to pass validation.
"""

from __future__ import annotations

from typing import Callable

from parser import AgentResponse, _parse_response
from directive import DirectiveVersion

_TEMPLATE = (
    "<thought_log>\n"
    "{thought_log}\n"
    "</thought_log>\n"
    "<conclusion>\n"
    "{conclusion}\n"
    "</conclusion>"
)

_DEFAULT_THOUGHT_LOG = (
    "  Fixture agent: this reasoning is not generated, it is fixed at construction time.\n"
    "  Supplied so the response satisfies the structural contract; it carries no evidence."
)

# A fixture whose text contains a closing tag would terminate its own block early
# and leave stray text outside the blocks, which the parser rejects. Catch it at
# construction with a clear message rather than at call time as a parse failure.
_FORBIDDEN = ("</thought_log>", "</conclusion>", "<thought_log>", "<conclusion>")


def make_fixture_adapter(
    conclusion: str,
    thought_log: str | None = None,
) -> Callable[[str, str, DirectiveVersion], AgentResponse]:
    """
    Build an adapter that always returns `conclusion`, regardless of input.

    conclusion  — the exact conclusion text the agent should "reach".
    thought_log — optional reasoning text; a neutral placeholder is used if omitted.

    Raises ValueError if either field is empty or contains an XML block tag
    (which would break the structural contract this adapter is meant to satisfy).
    """
    if not conclusion or not conclusion.strip():
        raise ValueError("conclusion cannot be empty — the parser requires a non-empty block")

    resolved_thought_log = _DEFAULT_THOUGHT_LOG if thought_log is None else thought_log
    if not resolved_thought_log.strip():
        raise ValueError("thought_log cannot be blank — the parser requires a non-empty block")

    for field_name, value in (("conclusion", conclusion), ("thought_log", resolved_thought_log)):
        for tag in _FORBIDDEN:
            if tag in value:
                raise ValueError(
                    f"{field_name} must not contain {tag!r} — it would break the two-block "
                    "structural contract this adapter exists to satisfy"
                )

    def adapter(subject: str, context: str, directive: DirectiveVersion) -> AgentResponse:
        # subject/context/directive are accepted to satisfy the contract and
        # deliberately ignored: a fixture is fixed, that is the whole point.
        return _parse_response(
            _TEMPLATE.format(thought_log=resolved_thought_log, conclusion=conclusion)
        )

    return adapter

"""
Accountability Layer — Phase 2: Validation Loop
Implements ADR-07: single retry on structural parse failure.

Both attempts are always written to the audit record.
Rising parse_failure_rate across runs is a drift signal for directive decay.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Callable

from parser import AgentResponse, StructuralParseError
from directive import DirectiveVersion, get_active_directive
from schemas import AgentID, DataSource, ParseStatus, ReasoningObject

# Injected as the directive on the second attempt (ADR-07)
CORRECTIVE_DIRECTIVE_TEXT = (
    "Your previous response failed structural validation. "
    "You must provide your internal reasoning in a <thought_log> block "
    "and your final output in a <conclusion> block. "
    "Adhere to the schema exactly."
)

_CORRECTIVE_DIRECTIVE = DirectiveVersion(
    version="corrective", text=CORRECTIVE_DIRECTIVE_TEXT
)


class HaltError(Exception):
    """
    Raised when the validation loop exhausts both attempts without a successful parse.
    Carries all ReasoningObjects written so the caller can persist the audit trail
    before propagating the halt upstream.
    """

    def __init__(self, message: str, reasoning_objects: list[ReasoningObject]) -> None:
        super().__init__(message)
        self.reasoning_objects = reasoning_objects


@dataclass
class ValidationLoopResult:
    reasoning_objects: list[ReasoningObject]
    final_response: AgentResponse | None  # None when halted


def _build_reasoning_object(
    *,
    run_id: uuid.UUID,
    agent_id: AgentID,
    attempt_number: int,
    parse_status: ParseStatus,
    confidence_score: float,
    thought_log: str | None = None,
    conclusion: str | None = None,
    raw_text: str | None = None,
    data_sources: tuple[DataSource, ...] = (),
) -> ReasoningObject:
    raw_output = {"text": raw_text} if raw_text is not None else None
    return ReasoningObject(
        run_id=run_id,
        agent_id=agent_id,
        attempt_number=attempt_number,
        parse_status=parse_status,
        confidence_score=confidence_score,
        thought_log=thought_log,
        conclusion=conclusion,
        raw_output=raw_output,
        data_sources=data_sources,
    )


def run_validation_loop(
    ticker: str,
    context: str,
    run_id: uuid.UUID,
    agent_id: AgentID,
    *,
    confidence_score: float = 0.7,
    data_sources: tuple[DataSource, ...] = (),
    directive: DirectiveVersion | None = None,
    call_agent_fn: Callable | None = None,
) -> ValidationLoopResult:
    """
    ADR-07 validation loop.

    call_agent_fn must be provided — the accountability layer has no default LLM.
    Signature: (subject: str, context: str, directive: DirectiveVersion) -> AgentResponse

    Attempt 1 — active directive:
      SUCCESS  → one ReasoningObject (attempt=1, SUCCESS). Done.
      FAILURE  → log attempt=1 PARSE_FAILURE, proceed to attempt 2.

    Attempt 2 — corrective directive:
      SUCCESS  → two ReasoningObjects (attempt=1 PARSE_FAILURE, attempt=2 SUCCESS). Done.
      FAILURE  → two ReasoningObjects (attempt=1 PARSE_FAILURE, attempt=2 HALT).
                 Raises HaltError carrying those objects. No grade delivered.
    """
    if call_agent_fn is None:
        raise TypeError(
            "call_agent_fn is required. "
            "Provide an adapter for your agent: "
            "f(subject, context, directive) -> AgentResponse"
        )
    if directive is None:
        directive = get_active_directive()

    objects: list[ReasoningObject] = []

    # ── Attempt 1 ──────────────────────────────────────────────────────────
    try:
        response = call_agent_fn(ticker, context, directive)
    except StructuralParseError as exc:
        objects.append(
            _build_reasoning_object(
                run_id=run_id,
                agent_id=agent_id,
                attempt_number=1,
                parse_status=ParseStatus.PARSE_FAILURE,
                confidence_score=confidence_score,
                raw_text=exc.raw_response,
                data_sources=data_sources,
            )
        )

        # ── Attempt 2 (corrective) ──────────────────────────────────────────
        try:
            response = call_agent_fn(ticker, context, _CORRECTIVE_DIRECTIVE)
        except StructuralParseError as exc2:
            objects.append(
                _build_reasoning_object(
                    run_id=run_id,
                    agent_id=agent_id,
                    attempt_number=2,
                    parse_status=ParseStatus.HALT,
                    confidence_score=confidence_score,
                    raw_text=exc2.raw_response,
                    data_sources=data_sources,
                )
            )
            raise HaltError(
                f"Agent {agent_id.value!r} failed structural validation twice for {ticker!r}. "
                "Pipeline halted — no grade delivered.",
                objects,
            ) from exc2

        objects.append(
            _build_reasoning_object(
                run_id=run_id,
                agent_id=agent_id,
                attempt_number=2,
                parse_status=ParseStatus.SUCCESS,
                confidence_score=confidence_score,
                thought_log=response.thought_log,
                conclusion=response.conclusion,
                raw_text=response.raw_text,
                data_sources=data_sources,
            )
        )
        return ValidationLoopResult(reasoning_objects=objects, final_response=response)

    # Attempt 1 succeeded
    objects.append(
        _build_reasoning_object(
            run_id=run_id,
            agent_id=agent_id,
            attempt_number=1,
            parse_status=ParseStatus.SUCCESS,
            confidence_score=confidence_score,
            thought_log=response.thought_log,
            conclusion=response.conclusion,
            raw_text=response.raw_text,
            data_sources=data_sources,
        )
    )
    return ValidationLoopResult(reasoning_objects=objects, final_response=response)

"""
Cross-Agent Validation — compare two agents' conclusions about the same subject.

Implements the design in the Cross-Agent Validation SDD v1.

What it does
    Runs two agents independently, each through the unmodified ADR-07 validation
    loop (middleware.run_validation_loop), then compares their final conclusions
    for numeric divergence. Both agents' full attempt history is returned so the
    caller can persist it as evidence.

What it does NOT do
    It does not decide which agent is right. A flagged contradiction means the two
    conclusions cite different numbers, nothing more. Resolution is a human's job.

Relationship to consistency.py
    consistency.py compares one agent against a *repeat of itself* and deliberately
    throws the probe run away (fresh UUID, never persisted) — it is a private sanity
    check on a single run. This module is the opposite on purpose: two *different*
    agents, one shared run_id, and both agents' records persisted, because here the
    comparison itself is the evidence. The scoring primitives are imported from
    consistency.py unmodified rather than reimplemented.

Scope limit worth knowing (SDD §14)
    Comparison is numeric only. Two conclusions that disagree in substance but cite
    the same figures will not be flagged. This detects number mismatches, not
    reasoning mismatches.

Known gap (deliberate, per SDD §9)
    Only HaltError is caught per agent. If an agent's adapter raises something else
    (a rate-limit error, an EDGAR fetch failure), it propagates and the whole
    comparison aborts — including the other agent's already-collected records.
    ComparisonStatus has no ERROR state in v1; adding one is a design decision, not
    something to improvise here.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from consistency import (
    ConsistencyAgreement,
    _classify,
    _compute_score,
    _extract_numbers,
)
from middleware import HaltError, run_validation_loop
from schemas import AgentID, DataSource, ReasoningObject


# ── Status ─────────────────────────────────────────────────────────────────────

class ComparisonStatus(str, Enum):
    """
    Outcome of a cross-agent comparison attempt.

    A halted agent is still evidence: its ReasoningObjects (including the
    HALT-status one) are returned and persisted. A halt means only that there was
    no conclusion on that side to compare, not that the run disappears.
    """
    COMPARED       = "COMPARED"        # both agents produced a conclusion
    AGENT_A_HALTED = "AGENT_A_HALTED"  # producer A failed structural validation twice
    AGENT_B_HALTED = "AGENT_B_HALTED"  # producer B failed structural validation twice
    BOTH_HALTED    = "BOTH_HALTED"


# ── Result ─────────────────────────────────────────────────────────────────────

@dataclass
class CrossAgentComparisonResult:
    """
    One cross-agent comparison.

    Not frozen — follows ConsistencyResult's convention in consistency.py. This is a
    computed value that gets embedded into a payload dict before persistence, not an
    audit record itself. The ReasoningObjects underneath it stay frozen and immutable.

    contradiction_flag is None (not False) when status != COMPARED. False would claim
    "checked, found no contradiction", which is a materially stronger statement than
    "no comparison was possible" — P3 forbids reporting a result that was never produced.
    """
    run_id:             uuid.UUID
    subject:            str
    agent_a_id:         AgentID
    agent_b_id:         AgentID
    status:             ComparisonStatus
    agent_a_conclusion: str | None
    agent_b_conclusion: str | None
    agent_a_numbers:    list[str]
    agent_b_numbers:    list[str]
    divergent_numbers:  list[str]                    # in one conclusion but not both
    contradiction_flag: bool | None                  # None when status != COMPARED
    word_overlap:       float | None
    number_overlap:     float | None
    score:              float | None
    agreement:          ConsistencyAgreement | None
    compared_at:        datetime

    def to_dict(self) -> dict[str, Any]:
        """Flat, JSON-serialisable dict — becomes one key inside a larger run payload."""
        return {
            "run_id":             str(self.run_id),
            "subject":            self.subject,
            "agent_a_id":         self.agent_a_id.value,
            "agent_b_id":         self.agent_b_id.value,
            "status":             self.status.value,
            "agent_a_conclusion": self.agent_a_conclusion,
            "agent_b_conclusion": self.agent_b_conclusion,
            "agent_a_numbers":    self.agent_a_numbers,
            "agent_b_numbers":    self.agent_b_numbers,
            "divergent_numbers":  self.divergent_numbers,
            "contradiction_flag": self.contradiction_flag,
            "word_overlap":       self.word_overlap,
            "number_overlap":     self.number_overlap,
            "score":              self.score,
            "agreement":          self.agreement,
            "compared_at":        self.compared_at.isoformat(),
        }


# ── Internals ──────────────────────────────────────────────────────────────────

def _run_one_agent(
    subject:          str,
    context:          str,
    run_id:           uuid.UUID,
    agent_id:         AgentID,
    call_agent_fn:    Callable,
    confidence_score: float,
    data_sources:     tuple[DataSource, ...],
) -> tuple[str | None, list[ReasoningObject], bool]:
    """
    Run one agent's ADR-07 loop, preserving its ReasoningObjects even when it halts.

    Returns (conclusion_or_None, reasoning_objects, halted).
    """
    try:
        result = run_validation_loop(
            subject,
            context,
            run_id,
            agent_id,
            confidence_score=confidence_score,
            data_sources=data_sources,
            call_agent_fn=call_agent_fn,
        )
    except HaltError as exc:
        # The halt is the evidence — carry its records forward rather than dropping them.
        return None, list(exc.reasoning_objects), True

    objects = list(result.reasoning_objects)
    conclusion = result.final_response.conclusion if result.final_response else None
    # run_validation_loop raises rather than returning final_response=None, so this
    # branch is defensive only. Treat a missing conclusion as "nothing to compare".
    return conclusion, objects, conclusion is None


# ── Public API ─────────────────────────────────────────────────────────────────

def run_cross_agent_validation(
    subject:         str,
    context_a:       str,
    context_b:       str,
    agent_a_id:      AgentID,
    agent_b_id:      AgentID,
    call_agent_a_fn: Callable,
    call_agent_b_fn: Callable,
    *,
    run_id:           uuid.UUID | None = None,
    confidence_score: float = 0.7,
    data_sources_a:   tuple[DataSource, ...] = (),
    data_sources_b:   tuple[DataSource, ...] = (),
) -> tuple[CrossAgentComparisonResult, list[ReasoningObject]]:
    """
    Run two agents independently on the same subject, then compare their conclusions.

    Each agent gets its own context (that is the point — disagreement is only
    meaningful when the agents saw different evidence) but they share one run_id, so
    their records land together in the store as a single comparable run.

    Returns the comparison result plus every ReasoningObject either agent produced,
    in order (agent A's attempts, then agent B's), including any that halted — ready
    to persist exactly as the /api/chat handler persists a single agent's records.

    confidence_score / data_sources_a / data_sources_b are keyword-only additions
    beyond the SDD signature, passed straight through to run_validation_loop so real
    provenance can be recorded per agent. Defaults match run_validation_loop's own.
    """
    if run_id is None:
        run_id = uuid.uuid4()

    a_conclusion, a_objects, a_halted = _run_one_agent(
        subject, context_a, run_id, agent_a_id,
        call_agent_a_fn, confidence_score, data_sources_a,
    )
    # Agent B runs regardless of A's outcome: there is no reason for one agent's
    # structural failure to suppress the other's evidence.
    b_conclusion, b_objects, b_halted = _run_one_agent(
        subject, context_b, run_id, agent_b_id,
        call_agent_b_fn, confidence_score, data_sources_b,
    )

    reasoning_objects = a_objects + b_objects

    if a_halted and b_halted:
        status = ComparisonStatus.BOTH_HALTED
    elif a_halted:
        status = ComparisonStatus.AGENT_A_HALTED
    elif b_halted:
        status = ComparisonStatus.AGENT_B_HALTED
    else:
        status = ComparisonStatus.COMPARED

    # Report whatever numbers each surviving conclusion carried, even when no
    # comparison was possible — that is observed evidence, not an inferred result.
    a_numbers = _extract_numbers(a_conclusion) if a_conclusion else []
    b_numbers = _extract_numbers(b_conclusion) if b_conclusion else []

    if status is ComparisonStatus.COMPARED:
        score, word_overlap, number_overlap = _compute_score(a_conclusion, b_conclusion)
        agreement: ConsistencyAgreement | None = _classify(score)
        a_set, b_set = set(a_numbers), set(b_numbers)
        # Symmetric difference: a number in exactly one conclusion. Covers both
        # "different value" and "present here, absent there" with the same rule.
        divergent = sorted(a_set.symmetric_difference(b_set))
        contradiction_flag: bool | None = len(divergent) > 0
    else:
        score = word_overlap = number_overlap = None
        agreement = None
        divergent = []
        contradiction_flag = None

    result = CrossAgentComparisonResult(
        run_id=run_id,
        subject=subject,
        agent_a_id=agent_a_id,
        agent_b_id=agent_b_id,
        status=status,
        agent_a_conclusion=a_conclusion,
        agent_b_conclusion=b_conclusion,
        agent_a_numbers=a_numbers,
        agent_b_numbers=b_numbers,
        divergent_numbers=divergent,
        contradiction_flag=contradiction_flag,
        word_overlap=word_overlap,
        number_overlap=number_overlap,
        score=score,
        agreement=agreement,
        compared_at=datetime.now(timezone.utc),
    )
    return result, reasoning_objects


# ── Persistence (integration with the accountability store) ────────────────────

def build_run_payload(
    result:            CrossAgentComparisonResult,
    reasoning_objects: list[ReasoningObject],
    *,
    scope: str = "auditor",
) -> tuple[dict[str, Any], Any]:
    """
    Assemble the (payload, RunSession) pair for a cross-agent run.

    The payload mirrors the shape /api/chat already stores, plus one new key,
    "cross_agent_comparison". No schema change is needed: the runs table holds a
    free-form JSON blob (web/db.py), so a new key costs nothing.

    Returns (payload, session) so a caller can inspect or amend either before writing.
    """
    from directive import get_active_directive          # local: keeps the import graph flat
    from schemas import RunStatus, RunSession
    from web.db import _extract_ticker                  # same normalisation server.py uses

    directive = get_active_directive()
    completed = datetime.now(timezone.utc)
    halted = result.status is not ComparisonStatus.COMPARED

    session = RunSession(
        ticker=_extract_ticker(result.subject),
        directive_version=directive.version,
        directive_text=directive.text,
        run_id=result.run_id,
        status=RunStatus.HALTED if halted else RunStatus.COMPLETE,
        reasoning_objects=tuple(reasoning_objects),
        completed_at=completed,
    )

    payload: dict[str, Any] = {
        "run_id":                 str(result.run_id),
        "subject":                result.subject,
        "scope":                  scope,
        "halted":                 halted,
        "reasoning_objects":      [ro.to_dict(investor_scope=False) for ro in reasoning_objects],
        "session":                session.to_dict(),
        "cross_agent_comparison": result.to_dict(),
    }
    return payload, session


def persist_cross_agent_run(
    result:            CrossAgentComparisonResult,
    reasoning_objects: list[ReasoningObject],
    *,
    scope: str = "auditor",
) -> dict[str, Any]:
    """
    Write a cross-agent run to the append-only store and return the stored payload.

    Read it back with web.db.get_run(run_id)["cross_agent_comparison"].

    Tradeoff (SDD §7.3): the comparison lives inside the payload JSON blob, so it is
    retrievable by run_id but not queryable in SQL — "every contradiction this month"
    needs a Python-side scan of get_runs() or SQLite's JSON1 extension. Accepted for
    v1; a dedicated column is a later schema decision.

    web.db is imported lazily so this module stays importable (and testable) without
    touching the database layer — the same deferral consistency.py uses for middleware.
    """
    from web.db import init_db, insert_run, insert_session

    payload, session = build_run_payload(result, reasoning_objects, scope=scope)

    init_db()
    insert_run(payload)
    insert_session(str(result.run_id), session.ticker, payload["session"])
    return payload

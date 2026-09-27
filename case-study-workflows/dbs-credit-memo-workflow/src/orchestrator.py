"""
WHAT THIS FILE DOES: runs the full credit-memo pipeline in strict, fail-fast
sequence — intake, data fetch, draft synthesis, human review, finalize/submit —
halting at the first point that isn't clear to proceed, and never calling a
downstream stage once that happens.

CONFIRMED / CONSTRUCTED: mirrors DBS's own stated shape (raw data in ->
review-ready draft -> human review -> finalize, per Section 3.3 and Section 4
of the case study) without adding steps DBS hasn't described. The specific halt
conditions below are CONSTRUCTED, reasoned from the design decisions logged
across this build's addenda — not a claim that DBS's actual system halts at
exactly these five points.

Halt map (final, per Addenda v2-v3):
  1. intake incomplete                          -> halt before data fetch
  2. client record not found in mock_data        -> halt before draft synthesis
  3. draft_synthesis flags a gap                 -> halt before human review
  4. human_review_gate returns not_cleared       -> halt before finalize/submit
  5. all conditions clear                        -> finalize/submit runs

Per Design Decision 8 (Addendum v3), this module constructs the HumanReviewGate
internally from a decision_function passed into run() -- callers never
construct the gate through this entry point directly, though HumanReviewGate
remains independently constructible for its own isolated tests.
"""

from typing import Callable, TypedDict, Optional

import mock_data
from intake import validate_intake
from draft_synthesis import synthesize_draft
from human_review_gate import HumanReviewGate
from finalize_submit import finalize


class HaltResult(TypedDict):
    halted: bool
    halt_stage: str
    reason: str


class PipelineResult(TypedDict):
    halted: bool
    halt_stage: Optional[str]
    reason: Optional[str]
    finalize_result: Optional[dict]


def run(request: dict, decision_function: Callable[[dict], str]) -> PipelineResult:
    """
    Runs the pipeline end-to-end for a single memo request.

    request: a raw memo request dict, checked by intake.validate_intake().
    decision_function: callable passed to HumanReviewGate at construction --
        required, or HumanReviewGate itself raises TypeError (Design Decision 8
        does not weaken this requirement; it only moves where construction
        happens).

    Returns a PipelineResult. If halted is True, halt_stage names which of the
    five halt conditions fired and finalize_result is None. If halted is False,
    the pipeline reached finalize/submit and finalize_result holds its output.
    """
    intake_result = validate_intake(request)
    if intake_result["status"] == "incomplete":
        return PipelineResult(
            halted=True,
            halt_stage="intake",
            reason=f"Missing required fields: {intake_result['missing_fields']}",
            finalize_result=None,
        )

    client_record = mock_data.get_client_record(request["client_id"])
    if client_record is None:
        return PipelineResult(
            halted=True,
            halt_stage="client_lookup",
            reason=f"No client record found for client_id={request['client_id']!r}",
            finalize_result=None,
        )

    draft_result = synthesize_draft(client_record)
    if draft_result["status"] == "gap_flagged":
        return PipelineResult(
            halted=True,
            halt_stage="draft_synthesis",
            reason=draft_result["gap_reason"],
            finalize_result=None,
        )

    gate = HumanReviewGate(decision_function)
    review_outcome = gate.review(draft_result["draft"])
    if review_outcome == "not_cleared_for_finalization":
        return PipelineResult(
            halted=True,
            halt_stage="human_review_gate",
            reason="decision_function returned not_cleared_for_finalization",
            finalize_result=None,
        )

    finalize_result = finalize(draft_result["draft"])
    return PipelineResult(
        halted=False,
        halt_stage=None,
        reason=None,
        finalize_result=dict(finalize_result),
    )

"""
Orchestrator — CommBank Disputes Workflow (Illustrative Reference Implementation)

WHAT THIS FILE DOES: runs the three components in order — Intake, then
Verification, then Gate — and stops early if any step escalates, so a
downstream step is never called with data it can't meaningfully use. This
is the single entry point for the whole pipeline; see README.md for the
full workflow.

This file IS the sequence claim made executable: the order
Intake -> Verification -> Gate is CONSTRUCTED, justified by a real data
dependency (each step needs the prior step's output — see
docs/DESIGN_SPECS.md), not by narrative convenience.

This is a single-tool, linear pipeline — not a multi-agent system. The public
record (case study, Section 3.1) supports three functions performed by what
appears to be one tool, not a coordinated multi-agent architecture.
"""

from dataclasses import dataclass, asdict
from typing import Optional

from src.components.intake import run_intake
from src.components.verification import run_verification
from src.components.gate import run_gate


@dataclass
class PipelineResult:
    stage_reached: str  # "intake" | "verification" | "gate"
    auto_lodge_decision: Optional[bool]
    escalation_reason: Optional[str]
    intake_result: dict
    verification_result: Optional[dict] = None
    gate_result: Optional[dict] = None


def run_pipeline(raw_customer_text: str) -> PipelineResult:
    """
    Runs the full Intake -> Verification -> Gate sequence.

    Each step is only called if the prior step did not escalate. This is
    the fail-fast behavior specified in docs/DESIGN_SPECS.md for Intake
    (ambiguous input) and Verification (no matching record) — the pipeline
    does not call a downstream step with data that step cannot meaningfully
    act on.
    """
    intake_result = run_intake(raw_customer_text)

    if intake_result.escalate:
        return PipelineResult(
            stage_reached="intake",
            auto_lodge_decision=False,
            escalation_reason=intake_result.escalation_reason,
            intake_result=asdict(intake_result),
        )

    verification_result = run_verification(
        claimed_amount=intake_result.claimed_amount,
        claimed_merchant=intake_result.claimed_merchant,
        claimed_date=intake_result.claimed_date,
    )

    if verification_result.escalate:
        return PipelineResult(
            stage_reached="verification",
            auto_lodge_decision=False,
            escalation_reason=verification_result.escalation_reason,
            intake_result=asdict(intake_result),
            verification_result=asdict(verification_result),
        )

    gate_result = run_gate(
        record_found=verification_result.record_found,
        match_result=verification_result.match_result,
        claimed_amount=intake_result.claimed_amount,
        dispute_type=intake_result.dispute_type,
    )

    return PipelineResult(
        stage_reached="gate",
        auto_lodge_decision=gate_result.auto_lodge_decision,
        escalation_reason=gate_result.escalation_reason,
        intake_result=asdict(intake_result),
        verification_result=asdict(verification_result),
        gate_result=asdict(gate_result),
    )

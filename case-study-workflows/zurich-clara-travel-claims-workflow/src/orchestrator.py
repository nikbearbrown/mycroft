"""
WHAT THIS FILE DOES: Runs Intake, Extraction, Coverage Check, Authorization
Gate, and Resolve/Escalate in strict sequence per the locked halt map. The
only module with dependencies on all the others.

Mirrors Zurich's disclosed shape only at the level Zurich actually
confirmed -- orchestration exists, coordinates specialized handling, keeps
a human-control point, produces an auditable trail (here: the sequence of
stage results this function naturally returns). Does not add steps, agent
counts, or handoff protocols Zurich never described.
"""

from intake import validate_intake
from extraction import extract
from coverage_check import check_coverage
from authorization_gate import AuthorizationGate
from resolve_escalate import resolve, escalate


def run_pipeline(claim, decision_fn):
    """
    claim: {"claim_id": ..., "policy_id": ..., "documents": [...]}
    decision_fn: externally supplied function for the Authorization Gate.
                 No default is provided anywhere in this pipeline.
    """
    claim_id = claim["claim_id"]

    intake_result = validate_intake(claim)
    if intake_result["status"] == "halted":
        return escalate(claim_id, intake_result.get("reason"), intake_result.get("detail"))

    extraction_result = extract(claim["documents"])
    if extraction_result["status"] == "halted":
        return escalate(claim_id, extraction_result["reason"], extraction_result.get("detail"))

    coverage_result = check_coverage(claim_id, claim["policy_id"], extraction_result["documents"])
    if coverage_result["status"] == "halted":
        return escalate(claim_id, coverage_result["reason"], coverage_result.get("detail"))

    gate = AuthorizationGate(decision_fn)
    decision = gate.decide(coverage_result["coverage_result"])

    if decision == "escalated_to_human":
        return escalate(claim_id, "authorization_gate_rejection", coverage_result["coverage_result"])

    return resolve(claim_id, coverage_result["coverage_result"])

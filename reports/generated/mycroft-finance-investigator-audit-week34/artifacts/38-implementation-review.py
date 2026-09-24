"""Human review gate for completed finance investigations.

The investigator prepares a review request. Only a human-authored decision file
can clear the gate, and accepted decisions are written once as immutable run
artifacts.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class ReviewError(RuntimeError):
    """Raised when a review request or decision violates the gate contract."""


DECISIONS = {"APPROVE", "REQUEST_CHANGES", "BLOCK"}
MATERIALITY_DECISIONS = {"APPROVE_DEMO", "REPLACE", "REJECT"}
AGENT_IDENTITIES = {
    "agent",
    "ai",
    "monthly-performance-investigator",
    "mycroft-finance-investigator",
}
REPO_ROOT = Path(__file__).resolve().parents[3]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ReviewError(f"{label} must contain one JSON object")
    return payload


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ReviewError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReviewError("reviewed_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReviewError("reviewed_at must include a timezone offset")
    return parsed


def _positive_decimal(value: Any, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ReviewError(f"{field} must be a decimal") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise ReviewError(f"{field} must be a positive finite decimal")
    return parsed


def _load_investigation(run_log_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    run_log = _load_json(run_log_path, "run log")
    if run_log.get("workflow") != "mycroft-finance-investigator":
        raise ReviewError("run log belongs to a different workflow")
    run_id = _required_string(run_log, "run_id", "run log")
    investigation = run_log.get("investigation")
    if not isinstance(investigation, dict):
        raise ReviewError("run log is missing the investigation object")
    if investigation.get("status") != "COMPLETED_PENDING_HUMAN_REVIEW":
        raise ReviewError(f"investigation {run_id} is not ready for human review")
    human_gate = investigation.get("human_gate")
    if not isinstance(human_gate, dict) or human_gate.get("status") != "OPEN":
        raise ReviewError(f"investigation {run_id} does not have an open human gate")
    return run_log, investigation


def build_review_request(run_log_path: Path) -> dict[str, Any]:
    """Create an explicitly open, human-fillable review request."""

    run_log, investigation = _load_investigation(run_log_path)
    config = run_log.get("config", {})
    return {
        "schema_version": "0.1.0",
        "workflow": "mycroft-finance-investigator",
        "run_id": run_log["run_id"],
        "source_run_log": _portable_path(run_log_path),
        "source_run_sha256": _sha256(run_log_path),
        "gate_status": "OPEN",
        "reviewer": {"name": "", "role": ""},
        "reviewed_at": "",
        "decision": "",
        "materiality": {
            "decision": "",
            "amount": str(config.get("materiality_amount", "")),
            "reasoning": "",
        },
        "causal_explanations": [],
        "tested": [],
        "did_not_test": [],
        "distribution_scope": "",
        "available_evidence": investigation.get("evidence", []),
        "instructions": [
            "A named human reviewer completes this file; the investigator cannot approve itself.",
            "Every causal explanation must cite one or more available_evidence references.",
            "APPROVE requires an approved or replaced materiality threshold and at least one evidence-backed causal explanation.",
            "The decision recorder writes a new immutable artifact and refuses to overwrite an existing decision.",
        ],
    }


def write_review_request(run_log_path: Path, output_path: Path) -> dict[str, Any]:
    request = build_review_request(run_log_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
    return request


def validate_review_decision(
    run_log_path: Path, decision_path: Path
) -> dict[str, Any]:
    """Validate a human-authored decision against the exact source run."""

    run_log, investigation = _load_investigation(run_log_path)
    decision = _load_json(decision_path, "review decision")
    run_id = _required_string(decision, "run_id", "review decision")
    if run_id != run_log["run_id"]:
        raise ReviewError(
            f"review decision run_id {run_id!r} does not match {run_log['run_id']!r}"
        )

    reviewer = decision.get("reviewer")
    if not isinstance(reviewer, dict):
        raise ReviewError("review decision.reviewer must be an object")
    reviewer_name = _required_string(reviewer, "name", "reviewer")
    reviewer_role = _required_string(reviewer, "role", "reviewer")
    if reviewer_name.casefold() in AGENT_IDENTITIES:
        raise ReviewError("the investigator or another agent cannot clear a human gate")

    reviewed_at = _required_string(decision, "reviewed_at", "review decision")
    _parse_timestamp(reviewed_at)
    final_decision = _required_string(decision, "decision", "review decision").upper()
    if final_decision not in DECISIONS:
        raise ReviewError(f"decision must be one of {sorted(DECISIONS)}")

    materiality = decision.get("materiality")
    if not isinstance(materiality, dict):
        raise ReviewError("review decision.materiality must be an object")
    materiality_decision = _required_string(
        materiality, "decision", "materiality"
    ).upper()
    if materiality_decision not in MATERIALITY_DECISIONS:
        raise ReviewError(
            f"materiality.decision must be one of {sorted(MATERIALITY_DECISIONS)}"
        )
    materiality_amount = _positive_decimal(materiality.get("amount"), "materiality.amount")
    materiality_reasoning = _required_string(
        materiality, "reasoning", "materiality"
    )

    available_evidence = set(investigation.get("evidence", []))
    explanations = decision.get("causal_explanations")
    if not isinstance(explanations, list):
        raise ReviewError("causal_explanations must be a list")
    normalized_explanations = []
    for index, explanation in enumerate(explanations):
        label = f"causal_explanations[{index}]"
        if not isinstance(explanation, dict):
            raise ReviewError(f"{label} must be an object")
        statement = _required_string(explanation, "finding_statement", label)
        text = _required_string(explanation, "explanation", label)
        evidence = explanation.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ReviewError(f"{label}.evidence must cite at least one reference")
        if any(not isinstance(item, str) or not item for item in evidence):
            raise ReviewError(f"{label}.evidence contains an invalid reference")
        unknown = sorted(set(evidence) - available_evidence)
        if unknown:
            raise ReviewError(f"{label}.evidence contains unknown references: {unknown}")
        normalized_explanations.append(
            {
                "finding_statement": statement,
                "explanation": text,
                "evidence": evidence,
            }
        )

    tested = decision.get("tested")
    did_not_test = decision.get("did_not_test")
    if not isinstance(tested, list) or not tested or any(
        not isinstance(item, str) or not item.strip() for item in tested
    ):
        raise ReviewError("tested must contain at least one reviewed item")
    if not isinstance(did_not_test, list) or any(
        not isinstance(item, str) or not item.strip() for item in did_not_test
    ):
        raise ReviewError("did_not_test must be a list of non-empty strings")

    distribution_scope = _required_string(
        decision, "distribution_scope", "review decision"
    )
    if final_decision == "APPROVE":
        if materiality_decision not in {"APPROVE_DEMO", "REPLACE"}:
            raise ReviewError("APPROVE requires an approved or replaced materiality threshold")
        if not normalized_explanations:
            raise ReviewError("APPROVE requires at least one evidence-backed causal explanation")

    return {
        "schema_version": "0.1.0",
        "workflow": "mycroft-finance-investigator",
        "run_id": run_id,
        "source_run_log": _portable_path(run_log_path),
        "source_run_sha256": _sha256(run_log_path),
        "gate_status": "CLEARED" if final_decision == "APPROVE" else "NOT_CLEARED",
        "reviewer": {"name": reviewer_name, "role": reviewer_role},
        "reviewed_at": reviewed_at,
        "decision": final_decision,
        "materiality": {
            "decision": materiality_decision,
            "amount": str(materiality_amount),
            "reasoning": materiality_reasoning,
        },
        "causal_explanations": normalized_explanations,
        "tested": [item.strip() for item in tested],
        "did_not_test": [item.strip() for item in did_not_test],
        "distribution_scope": distribution_scope,
        "decision_source": "HUMAN_SUPPLIED",
    }


def record_review_decision(
    run_log_path: Path, decision_path: Path, output_path: Path
) -> dict[str, Any]:
    """Validate and write a review decision without allowing overwrite."""

    artifact = validate_review_decision(run_log_path, decision_path)
    artifact["recorded_at"] = datetime.now(timezone.utc).isoformat()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_path.open("x", encoding="utf-8") as handle:
            json.dump(artifact, handle, indent=2)
            handle.write("\n")
    except FileExistsError as exc:
        raise ReviewError(f"review decision already exists: {output_path}") from exc
    return artifact

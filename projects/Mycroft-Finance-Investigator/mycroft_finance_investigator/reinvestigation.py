"""Review-driven replay and follow-up classification.

This module handles synthetic review exercises without pretending they are
human approvals. It binds each request to an exact orchestration artifact,
replays specialist work, and classifies follow-ups as verified evidence,
unsupported causal claims, or open evidence requests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .orchestration import run_orchestration


class ReinvestigationError(RuntimeError):
    """Raised when a follow-up cannot preserve the review contract."""


ACTIONS = {
    "VERIFY_EXISTING_EVIDENCE",
    "TEST_CAUSAL_CLAIM",
    "REQUEST_ADDITIONAL_EVIDENCE",
}
REPO_ROOT = Path(__file__).resolve().parents[3]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _portable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReinvestigationError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ReinvestigationError(f"{label} must be a JSON object")
    return payload


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ReinvestigationError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _reject_unknown(
    payload: dict[str, Any], allowed: set[str], label: str
) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ReinvestigationError(f"{label} contains unknown fields: {unknown}")


def load_follow_up_request(path: Path) -> dict[str, Any]:
    """Strictly validate a synthetic, non-approving follow-up request."""

    payload = _load_json(path, "follow-up request")
    if payload.get("schema_version") != "0.1.0":
        raise ReinvestigationError("follow-up request requires schema_version 0.1.0")
    _reject_unknown(
        payload,
        {
            "schema_version",
            "classification",
            "source_orchestration_run_id",
            "source_orchestration_sha256",
            "requests",
        },
        "follow-up request",
    )
    classification = _required_string(
        payload, "classification", "follow-up request"
    )
    if classification != "SYNTHETIC_REVIEW_FOLLOW_UP_EXERCISE":
        raise ReinvestigationError(
            "follow-up request.classification must be "
            "SYNTHETIC_REVIEW_FOLLOW_UP_EXERCISE"
        )
    source_run_id = _required_string(
        payload, "source_orchestration_run_id", "follow-up request"
    )
    source_hash = _required_string(
        payload, "source_orchestration_sha256", "follow-up request"
    )
    if len(source_hash) != 64 or any(
        character not in "0123456789abcdef" for character in source_hash
    ):
        raise ReinvestigationError(
            "follow-up request.source_orchestration_sha256 must be lowercase SHA-256"
        )
    requests = payload.get("requests")
    if not isinstance(requests, list) or not requests:
        raise ReinvestigationError("follow-up request.requests must be non-empty")
    seen_ids: set[str] = set()
    seen_tasks: set[str] = set()
    normalized = []
    for index, request in enumerate(requests):
        label = f"requests[{index}]"
        if not isinstance(request, dict):
            raise ReinvestigationError(f"{label} must be an object")
        _reject_unknown(
            request,
            {
                "request_id",
                "task_id",
                "action",
                "instruction",
                "claim",
                "cited_evidence",
            },
            label,
        )
        request_id = _required_string(request, "request_id", label)
        task_id = _required_string(request, "task_id", label)
        action = _required_string(request, "action", label)
        instruction = _required_string(request, "instruction", label)
        if request_id in seen_ids:
            raise ReinvestigationError(f"duplicate request_id: {request_id}")
        if task_id in seen_tasks:
            raise ReinvestigationError(f"duplicate task_id: {task_id}")
        if action not in ACTIONS:
            raise ReinvestigationError(f"unsupported follow-up action: {action}")
        seen_ids.add(request_id)
        seen_tasks.add(task_id)
        claim = request.get("claim")
        citations = request.get("cited_evidence")
        if not isinstance(citations, list) or not all(
            isinstance(item, str) and item.strip() for item in citations
        ):
            raise ReinvestigationError(f"{label}.cited_evidence must be strings")
        if action == "TEST_CAUSAL_CLAIM":
            if not isinstance(claim, str) or not claim.strip() or not citations:
                raise ReinvestigationError(
                    f"{label} causal test requires a claim and cited evidence"
                )
            normalized_claim: str | None = claim.strip()
        else:
            if claim is not None or citations:
                raise ReinvestigationError(
                    f"{label} permits claim and citations only for TEST_CAUSAL_CLAIM"
                )
            normalized_claim = None
        normalized.append(
            {
                "request_id": request_id,
                "task_id": task_id,
                "action": action,
                "instruction": instruction,
                "claim": normalized_claim,
                "cited_evidence": citations,
            }
        )
    return {
        "schema_version": "0.1.0",
        "classification": classification,
        "source_orchestration_run_id": source_run_id,
        "source_orchestration_sha256": source_hash,
        "requests": normalized,
    }


def _load_source_orchestration(
    path: Path, request: dict[str, Any]
) -> dict[str, Any]:
    if _sha256(path) != request["source_orchestration_sha256"]:
        raise ReinvestigationError("source orchestration hash does not match request")
    source = _load_json(path, "source orchestration")
    if source.get("workflow") != "mycroft-finance-investigator-orchestration":
        raise ReinvestigationError("source orchestration belongs to another workflow")
    if source.get("run_id") != request["source_orchestration_run_id"]:
        raise ReinvestigationError("source orchestration run does not match request")
    if (
        source.get("classification")
        != "EVIDENCE_GAP_WORK_QUEUE_NOT_CAUSAL_ANALYSIS"
        or source.get("causal_explanation") is not None
        or source.get("recommendation") is not None
        or source.get("human_gate", {}).get("status") != "OPEN"
    ):
        raise ReinvestigationError("source orchestration violates the human boundary")
    return source


def _replay_source(source: dict[str, Any]) -> dict[str, Any]:
    plan_path = _repo_path(str(source.get("routing_plan", "")))
    trend_path = _repo_path(str(source.get("trend_log", "")))
    if _sha256(plan_path) != source.get("routing_plan_sha256"):
        raise ReinvestigationError("routing plan changed after orchestration")
    if _sha256(trend_path) != source.get("trend_log_sha256"):
        raise ReinvestigationError("trend log changed after orchestration")
    replay = run_orchestration(plan_path, trend_path, "follow-up-replay")
    original_tasks = {task["task_id"]: task for task in source.get("tasks", [])}
    replay_tasks = {task["task_id"]: task for task in replay["tasks"]}
    if set(original_tasks) != set(replay_tasks):
        raise ReinvestigationError("specialist task inventory changed during replay")
    for task_id, task in original_tasks.items():
        if task.get("result_sha256") != replay_tasks[task_id].get("result_sha256"):
            raise ReinvestigationError(
                f"specialist result changed during replay: {task_id}"
            )
    return replay


def run_reinvestigation(
    request_path: Path, source_log_path: Path, run_id: str
) -> dict[str, Any]:
    """Replay specialist work and classify each requested follow-up."""

    request = load_follow_up_request(request_path)
    source = _load_source_orchestration(source_log_path, request)
    replay = _replay_source(source)
    source_tasks = {task["task_id"]: task for task in source["tasks"]}
    requested_tasks = {item["task_id"] for item in request["requests"]}
    if requested_tasks != set(source_tasks):
        raise ReinvestigationError(
            "follow-up request must address every source task exactly once"
        )

    results = []
    for item in request["requests"]:
        task = source_tasks[item["task_id"]]
        evidence = set(task["result"]["evidence"])
        unknown_citations = sorted(set(item["cited_evidence"]) - evidence)
        if unknown_citations:
            raise ReinvestigationError(
                f"request {item['request_id']} cites unknown evidence: "
                f"{unknown_citations}"
            )
        if item["action"] == "VERIFY_EXISTING_EVIDENCE":
            status = "VERIFIED"
            observation = (
                "Specialist result replayed exactly with the same evidence fingerprint."
            )
            gap = task["result"]["missing_evidence"]
        elif item["action"] == "TEST_CAUSAL_CLAIM":
            status = "UNSUPPORTED"
            observation = (
                "The cited records establish calculations or correlation only; "
                "no approved causal evidence class is present."
            )
            gap = ["APPROVED_CAUSAL_EVIDENCE", "OWNER_CAUSAL_EXPLANATION"]
        else:
            status = "OPEN"
            observation = "The requested additional evidence is not in the verified layer."
            gap = task["result"]["missing_evidence"]
        results.append(
            {
                "request_id": item["request_id"],
                "task_id": item["task_id"],
                "category": task["category"],
                "action": item["action"],
                "before_status": task["result"]["status"],
                "after_status": status,
                "instruction": item["instruction"],
                "claim_under_test": item["claim"],
                "cited_evidence": item["cited_evidence"],
                "observation": observation,
                "remaining_gap": gap,
                "causal_explanation_accepted": False,
                "source_result_sha256": task["result_sha256"],
            }
        )
    counts = {
        status: sum(result["after_status"] == status for result in results)
        for status in ("VERIFIED", "UNSUPPORTED", "OPEN")
    }
    return {
        "workflow": "mycroft-finance-investigator-reinvestigation",
        "run_id": run_id,
        "schema_version": "0.1.0",
        "classification": "REVIEW_FOLLOW_UP_EXERCISE_NOT_APPROVAL",
        "source_orchestration": _portable_path(source_log_path),
        "source_orchestration_sha256": _sha256(source_log_path),
        "source_orchestration_run_id": source["run_id"],
        "follow_up_request": _portable_path(request_path),
        "follow_up_request_sha256": _sha256(request_path),
        "replay": {
            "status": "EXACT_MATCH",
            "task_count": len(replay["tasks"]),
        },
        "results": results,
        "summary": {
            "verified_count": counts["VERIFIED"],
            "unsupported_count": counts["UNSUPPORTED"],
            "open_count": counts["OPEN"],
            "closure_status": "BLOCKED_PENDING_HUMAN_REVIEW",
        },
        "causal_explanation": None,
        "recommendation": None,
        "human_gate": {
            "status": "OPEN",
            "required": [
                "A named reviewer must inspect the replay and unresolved gaps",
                "Any causal explanation needs approved causal evidence",
                "Materiality and distribution remain human decisions",
            ],
        },
    }


def write_reinvestigation_artifacts(
    payload: dict[str, Any], log_path: Path, report_path: Path
) -> None:
    """Write append-only machine and human follow-up artifacts."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists() or report_path.exists():
        raise ReinvestigationError(
            "follow-up artifacts are append-only; choose new output paths"
        )
    lines = [
        "# Reviewer-Guided Re-investigation and Closure Pack",
        "",
        "## Boundary",
        "",
        f"- Classification: `{payload['classification']}`",
        "- The committed request is a synthetic exercise, not a human decision.",
        "- Replay status: `EXACT_MATCH`",
        "- Closure status: `BLOCKED_PENDING_HUMAN_REVIEW`",
        "- Recommendation: `NONE`",
        "",
        "## Before and After",
        "",
        "| Task | Category | Follow-up | Before | After | Remaining gap |",
        "|---|---|---|---|---|---|",
    ]
    for result in payload["results"]:
        gap = ", ".join(result["remaining_gap"])
        lines.append(
            f"| `{result['task_id']}` | {result['category']} | "
            f"`{result['action']}` | `{result['before_status']}` | "
            f"`{result['after_status']}` | {gap} |"
        )
    summary = payload["summary"]
    lines.extend(
        [
            "",
            "## Outcome Summary",
            "",
            f"- Verified evidence replays: {summary['verified_count']}",
            f"- Unsupported causal claims: {summary['unsupported_count']}",
            f"- Open evidence requests: {summary['open_count']}",
            "",
            "## Human Review",
            "",
            *[f"- [ ] {item}" for item in payload["human_gate"]["required"]],
            "",
            "_Verified means the evidence replayed exactly; it does not verify a business cause._",
            "",
        ]
    )
    try:
        with log_path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2) + "\n")
        with report_path.open("x", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
    except FileExistsError as exc:
        raise ReinvestigationError(
            "follow-up artifacts are append-only; choose new output paths"
        ) from exc

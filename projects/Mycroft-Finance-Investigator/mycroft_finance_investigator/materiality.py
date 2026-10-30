"""Named-human approval of the materiality threshold.

Every report this project has shipped carries `materiality_status:
DEMO_UNAPPROVED` and lists "approve or replace the demo materiality" as an open
issue. The threshold decides which variances are called material, so an
unapproved one means every materiality claim downstream rests on a fixture.

This module closes that gap. A named human authors an approval record; the
engine validates it, binds it to the exact finance pack it was judged against,
and writes it once as an immutable artifact. Only then may a plan claim
`APPROVED`.

What this module does NOT do: decide the threshold, judge whether the approved
amount is appropriate, or let the investigator approve its own fixture. The
amount is supplied by a human and the approval is refused if the author looks
like the agent.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class MaterialityError(RuntimeError):
    """Raised when an approval record violates the approval contract."""


# APPROVE_DEMO keeps the fixture amount but puts a name against it.
# REPLACE substitutes a different amount, which must be stated.
DECISIONS = {"APPROVE_DEMO", "REPLACE"}

# The agent may prepare the request. It may never author the decision.
AGENT_IDENTITIES = {
    "agent",
    "ai",
    "monthly-performance-investigator",
    "mycroft-finance-investigator",
}

SOURCE_FILES = {
    "account_mapping.csv",
    "actuals.csv",
    "budget.csv",
    "customers.csv",
    "headcount.csv",
    "ledger.csv",
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
        raise MaterialityError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise MaterialityError(f"{label} must contain one JSON object")
    return payload


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise MaterialityError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _parse_timestamp(value: str, field: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise MaterialityError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MaterialityError(f"{field} must include a timezone offset")
    return parsed


def _positive_decimal(value: Any, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MaterialityError(f"{field} must be a decimal") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise MaterialityError(f"{field} must be a positive finite decimal")
    return parsed


def _money(value: Decimal) -> str:
    return f"{value:.2f}"


def _repo_path(value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


# --- the request the agent may prepare -----------------------------------

def build_approval_request(verified_dir: Path, entity: str, period: str,
                           demo_amount: Decimal) -> dict[str, Any]:
    """Describe what a human is being asked to approve, and against what data.

    The source hashes are recorded here so the decision is bound to the exact
    pack the approver saw. If the data changes afterwards, the approval no
    longer applies to it.
    """
    source_hashes: dict[str, str] = {}
    for file_name in sorted(SOURCE_FILES):
        source_path = verified_dir / file_name
        if not source_path.is_file():
            raise MaterialityError(f"verified source is missing: {source_path}")
        source_hashes[file_name] = _sha256(source_path)

    return {
        "workflow": "mycroft-finance-investigator",
        "artifact": "materiality-approval-request",
        "entity": entity,
        "period": period,
        "demo_amount": _money(demo_amount),
        "demo_status": "DEMO_UNAPPROVED",
        "verified_dir": _portable_path(verified_dir),
        "source_hashes": source_hashes,
        "asks": [
            "Approve the demo amount as-is, or replace it with a reasoned amount.",
            "State the basis. An approval without reasoning is not an approval.",
            "Sign with a named human. The agent may not author this decision.",
        ],
        "prepared_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_approval_request(verified_dir: Path, entity: str, period: str,
                           demo_amount: Decimal, output_path: Path) -> dict[str, Any]:
    request = build_approval_request(verified_dir, entity, period, demo_amount)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
    return request


# --- the decision only a human may author --------------------------------

def validate_approval(decision_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    """Check a human-authored approval against the request it answers.

    Every failure here is a refusal to record, never a warning. An approval that
    cannot be tied to specific data, a specific amount and a specific person is
    not an approval.
    """
    decision = _load_json(decision_path, "materiality decision")

    if decision.get("workflow") != "mycroft-finance-investigator":
        raise MaterialityError("materiality decision belongs to another workflow")
    if decision.get("artifact") != "materiality-approval":
        raise MaterialityError("materiality decision is not a materiality-approval")

    verdict = _required_string(decision, "decision", "materiality decision")
    if verdict not in DECISIONS:
        raise MaterialityError(
            f"materiality decision.decision must be one of {sorted(DECISIONS)}"
        )

    approver = _required_string(decision, "approved_by", "materiality decision")
    if approver.strip().lower() in AGENT_IDENTITIES:
        raise MaterialityError(
            "materiality decision.approved_by must be a named human, not the agent"
        )

    reasoning = _required_string(decision, "reasoning", "materiality decision")
    if len(reasoning) < 20:
        raise MaterialityError(
            "materiality decision.reasoning must state a basis, not a placeholder"
        )

    approved_at = _parse_timestamp(
        _required_string(decision, "approved_at", "materiality decision"),
        "approved_at",
    )

    # Scope: the approval must answer THIS request.
    for field in ("entity", "period"):
        if decision.get(field) != request[field]:
            raise MaterialityError(
                f"materiality decision.{field} does not match the request"
            )

    # Integrity: the pack must not have changed since the human looked at it.
    expected = request["source_hashes"]
    observed = decision.get("source_hashes")
    if not isinstance(observed, dict) or observed != expected:
        raise MaterialityError(
            "materiality decision source hashes do not match the request; "
            "the approval does not apply to this data"
        )

    demo_amount = _positive_decimal(request["demo_amount"], "demo_amount")
    if verdict == "APPROVE_DEMO":
        approved_amount = demo_amount
        if "approved_amount" in decision:
            stated = _positive_decimal(decision["approved_amount"], "approved_amount")
            if stated != demo_amount:
                raise MaterialityError(
                    "APPROVE_DEMO cannot change the amount; use REPLACE"
                )
    else:  # REPLACE
        if "approved_amount" not in decision:
            raise MaterialityError("REPLACE requires an approved_amount")
        approved_amount = _positive_decimal(
            decision["approved_amount"], "approved_amount"
        )
        if approved_amount == demo_amount:
            raise MaterialityError(
                "REPLACE must state a different amount; use APPROVE_DEMO"
            )

    return {
        "decision": verdict,
        "approved_by": approver,
        "approved_at": approved_at.isoformat().replace("+00:00", "Z"),
        "approved_amount": _money(approved_amount),
        "demo_amount": _money(demo_amount),
        "reasoning": reasoning,
        "entity": request["entity"],
        "period": request["period"],
        "source_hashes": expected,
    }


def record_approval(decision_path: Path, request: dict[str, Any],
                    output_path: Path) -> dict[str, Any]:
    """Write the accepted approval once. Append-only: never overwrite.

    An approval that can be silently replaced is not evidence of anything, so a
    second approval for the same scope must be written to a new path.
    """
    accepted = validate_approval(decision_path, request)

    if output_path.exists():
        raise MaterialityError(
            f"materiality approval already recorded: {output_path}"
        )

    record = {
        "workflow": "mycroft-finance-investigator",
        "artifact": "materiality-approval",
        "materiality_status": "APPROVED",
        **accepted,
        "decision_source": _portable_path(decision_path),
        "decision_sha256": _sha256(decision_path),
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "scope_note": (
            "APPROVED records that a named human set this threshold against these "
            "exact source hashes. It does not assert the amount is correct, and it "
            "does not approve any variance, explanation or distribution."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def approved_threshold(approval_path: Path, entity: str, period: str,
                       verified_dir: Path) -> Decimal:
    """Read an approval back and re-prove it still applies before it is used.

    Re-hashing here is the point: an approval recorded against one pack must not
    silently authorise a different one.
    """
    record = _load_json(approval_path, "materiality approval")
    if record.get("materiality_status") != "APPROVED":
        raise MaterialityError("materiality approval is not APPROVED")
    if record.get("entity") != entity or record.get("period") != period:
        raise MaterialityError("materiality approval was recorded for another scope")

    expected = record.get("source_hashes")
    if not isinstance(expected, dict) or set(expected) != SOURCE_FILES:
        raise MaterialityError("materiality approval has no usable source hashes")
    for file_name, expected_hash in expected.items():
        source_path = verified_dir / file_name
        if not source_path.is_file():
            raise MaterialityError(f"verified source is missing: {source_path}")
        if _sha256(source_path) != expected_hash:
            raise MaterialityError(
                f"verified source changed since approval: {file_name}"
            )

    return _positive_decimal(record.get("approved_amount"), "approved_amount")

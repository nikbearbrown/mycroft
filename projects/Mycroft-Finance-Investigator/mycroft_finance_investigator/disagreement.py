"""Recording when a human disagrees with the engine, without erasing either side.

The review gate lets a human approve, request changes, or block. What it does not
capture is the interesting case: the reviewer accepts the report but rejects one
of its findings. "Revenue is flagged material; it is not, because the contract
slipped a week and landed in March."

Left untracked, that correction lives in somebody's head or an email. Worse, the
tempting fix is to let the reviewer edit the number, which destroys the only
record that the engine and the reviewer ever differed.

So this module records disagreements ALONGSIDE the engine's finding. Both
positions survive. The engine's number is never overwritten, because the
disagreement is the evidence, and a log that silently adopts one side is not a
log.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DisagreementError(RuntimeError):
    """Raised when a disagreement record violates the log contract."""


# What the reviewer is saying about the engine's finding.
POSITIONS = {
    "NOT_MATERIAL",      # engine flagged it; reviewer says it does not matter
    "MATERIAL_EXPECTED",  # it matters, but it is understood and not a finding
    "MISCLASSIFIED",     # right number, wrong category
    "INSUFFICIENT_EVIDENCE",  # the finding outruns what the evidence supports
}

AGENT_IDENTITIES = {
    "agent",
    "ai",
    "monthly-performance-investigator",
    "mycroft-finance-investigator",
}

REPO_ROOT = Path(__file__).resolve().parents[3]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DisagreementError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise DisagreementError(f"{label} must contain one JSON object")
    return payload


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DisagreementError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _parse_timestamp(value: str, field: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DisagreementError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DisagreementError(f"{field} must include a timezone offset")
    return parsed


def engine_findings(run_log_path: Path) -> dict[str, dict[str, Any]]:
    """The findings a reviewer is allowed to disagree with, keyed by category.

    Disagreement is only meaningful against something the engine actually said,
    so the claim must be found here or the record is refused.
    """
    run_log = _load_json(run_log_path, "run log")
    if run_log.get("workflow") != "mycroft-finance-investigator":
        raise DisagreementError("run log belongs to another workflow")
    investigation = run_log.get("investigation")
    if not isinstance(investigation, dict):
        raise DisagreementError("run log is missing the investigation object")

    trace = investigation.get("trace")
    if not isinstance(trace, list) or not trace:
        raise DisagreementError("run log has no trace to disagree with")

    # The engine states its category findings in the first trace step's
    # category_bridge. Keying by `key` is what makes a disagreement checkable:
    # a reviewer must name a category the engine actually reported on.
    findings: dict[str, dict[str, Any]] = {}
    for step in trace:
        observation = step.get("observation") if isinstance(step, dict) else None
        if not isinstance(observation, dict):
            continue
        bridge = observation.get("category_bridge")
        if not isinstance(bridge, list):
            continue
        for row in bridge:
            if not isinstance(row, dict):
                continue
            key = row.get("key")
            if isinstance(key, str) and key.strip():
                findings[key] = row
    if not findings:
        raise DisagreementError("run log contains no category findings")
    return findings


def validate_disagreement(record_path: Path, run_log_path: Path) -> dict[str, Any]:
    """Check a human-authored disagreement against the run it disputes."""
    record = _load_json(record_path, "disagreement")

    if record.get("workflow") != "mycroft-finance-investigator":
        raise DisagreementError("disagreement belongs to another workflow")
    if record.get("artifact") != "reviewer-disagreement":
        raise DisagreementError("artifact must be reviewer-disagreement")

    reviewer = _required_string(record, "reviewer", "disagreement")
    if reviewer.strip().lower() in AGENT_IDENTITIES:
        raise DisagreementError(
            "disagreement.reviewer must be a named human, not the agent"
        )

    position = _required_string(record, "position", "disagreement")
    if position not in POSITIONS:
        raise DisagreementError(
            f"disagreement.position must be one of {sorted(POSITIONS)}"
        )

    basis = _required_string(record, "basis", "disagreement")
    if len(basis) < 20:
        raise DisagreementError(
            "disagreement.basis must state a reason, not a placeholder"
        )

    recorded_at = _parse_timestamp(
        _required_string(record, "recorded_at", "disagreement"), "recorded_at"
    )

    claim = _required_string(record, "claim", "disagreement")
    findings = engine_findings(run_log_path)
    if claim not in findings:
        raise DisagreementError(
            f"disagreement.claim {claim!r} is not a finding in this run; "
            f"the engine said nothing about it"
        )

    # A reviewer may not restate the engine's number as their own. Both sides
    # are kept verbatim, and the engine's value is copied from the run, never
    # from the record.
    if "engine_value" in record:
        raise DisagreementError(
            "disagreement must not restate engine_value; it is read from the run"
        )

    return {
        "claim": claim,
        "engine_finding": findings[claim],
        "position": position,
        "reviewer": reviewer,
        "basis": basis,
        "recorded_at": recorded_at.isoformat().replace("+00:00", "Z"),
    }


def append_disagreement(record_path: Path, run_log_path: Path,
                        log_path: Path) -> dict[str, Any]:
    """Append to the log. Existing entries are never rewritten.

    Two reviewers may disagree with the same finding, and both entries stand.
    The log is the history of the argument, not a resolution of it.
    """
    accepted = validate_disagreement(record_path, run_log_path)

    if log_path.exists():
        log = _load_json(log_path, "disagreement log")
        entries = log.get("entries")
        if not isinstance(entries, list):
            raise DisagreementError("disagreement log is malformed")
    else:
        log = {
            "workflow": "mycroft-finance-investigator",
            "artifact": "reviewer-disagreement-log",
            "run_log": str(run_log_path),
            "run_log_sha256": _sha256_file(run_log_path),
            "entries": [],
        }
        entries = log["entries"]

    if log.get("run_log_sha256") != _sha256_file(run_log_path):
        raise DisagreementError(
            "run log changed since this disagreement log was opened; "
            "entries would no longer refer to the findings they disputed"
        )

    for existing in entries:
        if (existing.get("claim") == accepted["claim"]
                and existing.get("reviewer") == accepted["reviewer"]):
            raise DisagreementError(
                f"{accepted['reviewer']} has already recorded a position on "
                f"{accepted['claim']!r}; append a new reviewer or a new claim"
            )

    entries.append(accepted)
    log["entries"] = entries
    log["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    log["scope_note"] = (
        "Each entry records that a named human took a position against a finding "
        "the engine made. Neither side is adopted. The engine's numbers are "
        "unchanged and the disagreement does not resolve them."
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    return log

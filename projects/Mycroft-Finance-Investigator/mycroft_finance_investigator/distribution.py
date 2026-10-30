"""The last gate: may this report leave the system?

Everything upstream produces an artifact and stops. The materiality approval
says a human set the threshold. The freshness assessment says how old the
evidence is. The coverage report says whether the citations resolve. The review
decision says what the reviewer concluded. Each is checkable on its own, and
none of them stops a report being emailed to a board.

This gate is the one that answers the only question that matters at the end:
is this safe to send to someone who will act on it?

It is BLOCKED by default. Every condition must be positively demonstrated by an
artifact on disk. A missing artifact is not a pass -- it is the most common way
a bad report reaches a reader, because nobody remembers what was never produced.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DistributionError(RuntimeError):
    """Raised when the gate cannot be evaluated at all."""


# Freshness verdicts that do not by themselves block distribution. STALE is
# allowed through with the lag stated, because lateness is a fact a reader can
# weigh. EXPIRED is not: data nobody has looked at in longer than the stated
# shelf life is not evidence of the present.
FRESHNESS_ALLOWED = {"FRESH", "STALE"}


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistributionError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise DistributionError(f"{label} must contain one JSON object")
    return payload


def _check(name: str, path: Path | None, label: str,
           predicate) -> dict[str, Any]:
    """Evaluate one condition. Absent artifact fails; it never passes silently."""
    if path is None:
        return {"condition": name, "status": "BLOCKED",
                "reason": f"no {label} was supplied"}
    if not path.is_file():
        return {"condition": name, "status": "BLOCKED",
                "reason": f"{label} not found at {path}"}
    try:
        verdict, reason = predicate(_load_json(path, label))
    except DistributionError as exc:
        return {"condition": name, "status": "BLOCKED", "reason": str(exc)}
    return {"condition": name,
            "status": "CLEARED" if verdict else "BLOCKED",
            "reason": reason}


def _materiality(payload: dict[str, Any]) -> tuple[bool, str]:
    if payload.get("materiality_status") != "APPROVED":
        return False, "materiality approval is not APPROVED"
    approver = payload.get("approved_by") or "unknown"
    return True, f"threshold {payload.get('approved_amount')} approved by {approver}"


def _freshness(payload: dict[str, Any]) -> tuple[bool, str]:
    verdict = payload.get("verdict")
    if verdict not in FRESHNESS_ALLOWED:
        return False, f"evidence freshness is {verdict}"
    return True, (f"{verdict}: lag {payload.get('lag_days')}d, "
                  f"age {payload.get('age_days')}d")


def _coverage(payload: dict[str, Any]) -> tuple[bool, str]:
    if not payload.get("fully_resolved"):
        problems = payload.get("problems") or []
        return False, f"{len(problems)} evidence reference(s) did not resolve"
    return True, (f"{payload.get('references_resolved')}/"
                  f"{payload.get('references_checked')} references resolved")


def _review(payload: dict[str, Any]) -> tuple[bool, str]:
    decision = payload.get("decision") or payload.get("gate_status")
    if decision != "APPROVE":
        return False, f"human review decision is {decision}"
    reviewer = payload.get("reviewer") or "unknown"
    return True, f"approved by {reviewer}"


def _disagreements(payload: dict[str, Any]) -> tuple[bool, str]:
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise DistributionError("disagreement log is malformed")
    if entries:
        claims = sorted({entry.get("claim") for entry in entries})
        return False, (f"{len(entries)} unresolved disagreement(s) on "
                       f"{', '.join(str(c) for c in claims)}")
    return True, "no recorded disagreements"


def evaluate(materiality: Path | None = None, freshness: Path | None = None,
             coverage: Path | None = None, review: Path | None = None,
             disagreements: Path | None = None) -> dict[str, Any]:
    """Evaluate every condition and clear only if all of them clear.

    The disagreement log is the one condition that passes when the artifact is
    ABSENT, because no log means nobody disagreed. It fails when the log exists
    and holds entries, since an open disagreement is an argument in progress.
    """
    conditions = [
        _check("materiality_approved", materiality, "materiality approval",
               _materiality),
        _check("evidence_fresh", freshness, "freshness assessment", _freshness),
        _check("evidence_resolves", coverage, "coverage report", _coverage),
        _check("human_approved", review, "review decision", _review),
    ]

    if disagreements is None or not disagreements.is_file():
        conditions.append({"condition": "no_open_disagreements",
                           "status": "CLEARED",
                           "reason": "no disagreement log; nobody dissented"})
    else:
        conditions.append(_check("no_open_disagreements", disagreements,
                                 "disagreement log", _disagreements))

    blocked = [c for c in conditions if c["status"] == "BLOCKED"]
    return {
        "workflow": "mycroft-finance-investigator",
        "artifact": "distribution-gate",
        "status": "BLOCKED" if blocked else "CLEARED",
        "conditions": conditions,
        "blocking": [c["condition"] for c in blocked],
        "scope_note": (
            "CLEARED means every stated precondition was demonstrated by an "
            "artifact, not that the report is correct. It authorises sending, "
            "not believing."
        ),
        "evaluated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_evaluation(output_path: Path, **artifacts: Path | None) -> dict[str, Any]:
    result = evaluate(**artifacts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result

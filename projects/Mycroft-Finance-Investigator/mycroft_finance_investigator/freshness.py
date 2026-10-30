"""How old is the evidence, and was it even possible?

A variance report is a claim about a period. The data backing it was created at
some moment, and the report is read at another. Neither gap is visible in the
numbers, so a six-month-old pack and a same-week pack produce reports that look
identical.

This module measures both gaps and refuses two things outright: a pack with no
provenance, and a pack created BEFORE the period it claims to describe, which is
not staleness but an impossibility.

What it does NOT do: decide whether a gap matters. A five-month lag is routine
for an annual audit and disqualifying for a weekly flash report. The policy is
supplied; the judgement stays with the reviewer.
"""

from __future__ import annotations

import calendar
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


class FreshnessError(RuntimeError):
    """Raised when provenance is missing, malformed, or impossible."""


# FRESH  — inside both limits.
# STALE  — past the lag limit: the data took a long time to arrive.
# EXPIRED— past the age limit: the data has sat unused for a long time.
VERDICTS = ("FRESH", "STALE", "EXPIRED")

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FreshnessError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise FreshnessError(f"{label} must contain one JSON object")
    return payload


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise FreshnessError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise FreshnessError(f"{field} must be an ISO-8601 date (YYYY-MM-DD)") from exc


def period_end(period: str) -> date:
    """Last calendar day of a YYYY-MM period.

    The period is what the report describes, so its END is the earliest moment
    the data could honestly cover it.
    """
    try:
        year, month = (int(part) for part in period.split("-"))
        last = calendar.monthrange(year, month)[1]
        return date(year, month, last)
    except (ValueError, calendar.IllegalMonthError) as exc:
        raise FreshnessError(f"period must be YYYY-MM, got {period!r}") from exc


def read_provenance(verified_dir: Path) -> dict[str, Any]:
    """Load and check a pack's provenance.

    A pack with no provenance is refused rather than assumed fresh. Absence of
    evidence about age is not evidence of freshness.
    """
    path = verified_dir / "provenance.json"
    if not path.is_file():
        raise FreshnessError(
            f"pack has no provenance.json, so its age cannot be established: {path}"
        )
    payload = _load_json(path, "provenance")
    for field in ("classification", "created_on", "entity", "period"):
        _required_string(payload, field, "provenance")
    return payload


def assess(verified_dir: Path, as_of: date, max_lag_days: int,
           max_age_days: int) -> dict[str, Any]:
    """Measure arrival lag and shelf age against a supplied policy."""
    if max_lag_days < 0 or max_age_days < 0:
        raise FreshnessError("freshness limits must not be negative")

    provenance = read_provenance(verified_dir)
    period = provenance["period"]
    created_on = _parse_date(provenance["created_on"], "provenance.created_on")
    ends = period_end(period)

    # The impossibility check. Data cannot describe a period that had not
    # finished when the data was made. This is not staleness; it is a defect.
    if created_on < ends:
        raise FreshnessError(
            f"provenance.created_on {created_on.isoformat()} precedes the end of "
            f"period {period} ({ends.isoformat()}); the pack cannot describe a "
            "period that had not finished"
        )

    if as_of < created_on:
        raise FreshnessError(
            f"as_of {as_of.isoformat()} precedes created_on "
            f"{created_on.isoformat()}"
        )

    lag_days = (created_on - ends).days      # period end -> data created
    age_days = (as_of - created_on).days     # data created -> read today

    reasons: list[str] = []
    verdict = "FRESH"
    if lag_days > max_lag_days:
        verdict = "STALE"
        reasons.append(
            f"data arrived {lag_days} days after the period closed, over the "
            f"{max_lag_days} day limit"
        )
    if age_days > max_age_days:
        verdict = "EXPIRED"
        reasons.append(
            f"data is {age_days} days old at time of use, over the "
            f"{max_age_days} day limit"
        )

    return {
        "workflow": "mycroft-finance-investigator",
        "artifact": "evidence-freshness",
        "entity": provenance["entity"],
        "period": period,
        "classification": provenance["classification"],
        "period_ended": ends.isoformat(),
        "created_on": created_on.isoformat(),
        "as_of": as_of.isoformat(),
        "lag_days": lag_days,
        "age_days": age_days,
        "max_lag_days": max_lag_days,
        "max_age_days": max_age_days,
        "verdict": verdict,
        "reasons": reasons,
        "scope_note": (
            "Measures two gaps only. Whether a gap disqualifies a claim depends on "
            "what the report is for, which this engine does not know."
        ),
        "assessed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_assessment(verified_dir: Path, as_of: date, max_lag_days: int,
                     max_age_days: int, output_path: Path) -> dict[str, Any]:
    assessment = assess(verified_dir, as_of, max_lag_days, max_age_days)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
    return assessment

"""Does every figure actually resolve to a row in a source file?

The investigator already attaches evidence references to each finding, which
looks like proof until you ask whether anyone checked them. A citation that
points at nothing is worse than no citation: it survives review precisely
because it looks like diligence.

So this resolves them. For every category finding it reads the referenced file,
looks for the referenced row, and reports three separate failures that are
usually collapsed into one word, "unsourced":

  UNCITED   the finding carries no evidence at all
  DANGLING  the reference names a file that is not in the pack
  UNRESOLVED the file exists, but no row matches the reference

Only the first is obvious on inspection. The other two are what a citation
check is actually for.

What this does NOT do: judge whether the cited row supports the claim. It
proves the row exists. A number can resolve perfectly and still be the wrong
number, and no amount of hashing fixes that.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CoverageError(RuntimeError):
    """Raised when a run log cannot be checked at all."""


FAILURES = ("UNCITED", "DANGLING", "UNRESOLVED")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoverageError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise CoverageError(f"{label} must contain one JSON object")
    return payload


def parse_reference(reference: str) -> tuple[str, str, str]:
    """Split "budget.csv:account=4000" into file, column, value.

    A reference that does not have this shape is a defect in the finding, not
    something to be tolerated, so it raises rather than returning None.
    """
    if ":" not in reference or "=" not in reference:
        raise CoverageError(
            f"evidence reference is not file:column=value — {reference!r}"
        )
    file_name, _, predicate = reference.partition(":")
    column, _, value = predicate.partition("=")
    if not (file_name.strip() and column.strip() and value.strip()):
        raise CoverageError(f"evidence reference has an empty part — {reference!r}")
    return file_name.strip(), column.strip(), value.strip()


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def resolve(reference: str, verified_dir: Path,
            cache: dict[str, list[dict[str, str]]]) -> str | None:
    """Return a failure code, or None when the reference resolves."""
    file_name, column, value = parse_reference(reference)
    source = verified_dir / file_name
    if not source.is_file():
        return "DANGLING"
    if file_name not in cache:
        cache[file_name] = _rows(source)
    for row in cache[file_name]:
        if row.get(column, "").strip() == value:
            return None
    return "UNRESOLVED"


def check(run_log_path: Path, verified_dir: Path) -> dict[str, Any]:
    """Resolve every evidence reference on every category finding."""
    run_log = _load_json(run_log_path, "run log")
    if run_log.get("workflow") != "mycroft-finance-investigator":
        raise CoverageError("run log belongs to another workflow")
    investigation = run_log.get("investigation")
    if not isinstance(investigation, dict):
        raise CoverageError("run log is missing the investigation object")
    trace = investigation.get("trace")
    if not isinstance(trace, list) or not trace:
        raise CoverageError("run log has no trace to check")

    findings: dict[str, dict[str, Any]] = {}
    for step in trace:
        observation = step.get("observation") if isinstance(step, dict) else None
        if not isinstance(observation, dict):
            continue
        for row in observation.get("category_bridge") or []:
            if isinstance(row, dict) and isinstance(row.get("key"), str):
                findings[row["key"]] = row
    if not findings:
        raise CoverageError("run log contains no category findings to check")

    cache: dict[str, list[dict[str, str]]] = {}
    checked: list[dict[str, Any]] = []
    problems: list[dict[str, Any]] = []

    for key in sorted(findings):
        row = findings[key]
        references = row.get("evidence") or []
        if not references:
            problems.append({"claim": key, "failure": "UNCITED", "reference": None})
            checked.append({"claim": key, "references": 0, "resolved": 0})
            continue
        resolved = 0
        for reference in references:
            failure = resolve(reference, verified_dir, cache)
            if failure is None:
                resolved += 1
            else:
                problems.append(
                    {"claim": key, "failure": failure, "reference": reference}
                )
        checked.append(
            {"claim": key, "references": len(references), "resolved": resolved}
        )

    total = sum(item["references"] for item in checked)
    resolved_total = sum(item["resolved"] for item in checked)

    return {
        "workflow": "mycroft-finance-investigator",
        "artifact": "evidence-coverage",
        "run_log": str(run_log_path),
        "verified_dir": str(verified_dir),
        "claims_checked": len(checked),
        "references_checked": total,
        "references_resolved": resolved_total,
        "fully_resolved": not problems,
        "per_claim": checked,
        "problems": problems,
        "scope_note": (
            "Proves each cited row exists in the pack. Does not judge whether the "
            "row supports the claim; a figure can resolve perfectly and still be "
            "the wrong figure."
        ),
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def write_check(run_log_path: Path, verified_dir: Path,
                output_path: Path) -> dict[str, Any]:
    report = check(run_log_path, verified_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report

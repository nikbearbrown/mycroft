"""Load and check the benchmark fixture set.

Two layers, kept separate (SNICKERDOODLE verification stack):
- conformance (validate): a malformed fixture halts. Unknown task type, an
  answer outside the label set, a duplicate id -- these raise.
- audit (coverage): counts per task type and difficulty, and how many labels
  are still unreviewed. It reports; it does not pass or fail.

Labels are human judgments. A drafted fixture carries labeled_by
"UNREVIEWED" and expected_tier null; it loads and tests, but freeze()
refuses it. Nothing enters the locked set without a named person having set
its expected tier -- before any model has been run on it.

expected_tier means: the cheapest tier the labeler expects to get this right.
It is a judgment, not the router's rule applied by hand.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from gateway.policy import Policy

FIXTURES_DIR = Path(__file__).with_name("fixtures")
MANIFEST_PATH = Path(__file__).with_name("manifest.json")

UNREVIEWED = "UNREVIEWED"
DIFFICULTIES = frozenset({"easy", "hard"})
PROVENANCES = frozenset({"synthetic", "real"})
TARGET_PER_TYPE = 30  # sprint board: "at least 30 ... of each"
_REQUIRED = ("id", "task_type", "input", "expected", "difficulty",
             "provenance", "labeled_by")


class FixtureError(ValueError):
    """Raised when a fixture violates the contract. Conformance halts."""


class NotReviewed(ValueError):
    """Raised when freezing a set that still has unreviewed labels."""


def load(fixtures_dir: Path = FIXTURES_DIR) -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    for path in sorted(fixtures_dir.glob("*.jsonl")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                fx = json.loads(line)
            except json.JSONDecodeError as exc:
                raise FixtureError(f"{path.name}:{lineno} is not valid JSON: {exc}") from exc
            fx["_file"] = path.name
            fixtures.append(fx)
    return fixtures


def _check_expected(fx: dict[str, Any], rule: dict[str, Any], where: str) -> None:
    expected = fx["expected"]
    if not isinstance(expected, dict):
        raise FixtureError(f"{where}: 'expected' must be an object")

    if rule["output"] in ("label", "verdict"):
        if expected.get("label") not in rule["labels"]:
            raise FixtureError(f"{where}: expected label {expected.get('label')!r} "
                               f"is not one of {rule['labels']}")
    elif rule["output"] == "json":
        keys = expected.get("required_keys")
        if not isinstance(keys, list) or not keys or not all(
                isinstance(k, str) and k.strip() for k in keys):
            raise FixtureError(f"{where}: 'required_keys' must be a non-empty list")
    elif rule["validator"] == "cites_context":
        context = fx.get("context")
        if not isinstance(context, list) or not context:
            raise FixtureError(f"{where}: needs a non-empty 'context' list of passages")
        cite = expected.get("cite")
        if (not isinstance(cite, int) or isinstance(cite, bool)
                or not 0 <= cite < len(context)):
            raise FixtureError(f"{where}: 'cite' must index into context "
                               f"(0..{len(context) - 1}), got {cite!r}")


def _check_label(fx: dict[str, Any], policy: Policy, where: str) -> None:
    who = fx["labeled_by"]
    if not isinstance(who, str) or not who.strip():
        raise FixtureError(f"{where}: 'labeled_by' must be a non-empty string")

    tier = fx.get("expected_tier")
    if who == UNREVIEWED:
        if tier is not None:
            raise FixtureError(f"{where}: an UNREVIEWED fixture must not carry an "
                               f"expected_tier -- put your name in labeled_by "
                               f"when you label it")
        return

    if tier not in policy.tier_order:
        raise FixtureError(f"{where}: expected_tier must be one of "
                           f"{policy.tier_order}, got {tier!r}")
    try:
        date.fromisoformat(fx.get("labeled_on") or "")
    except ValueError:
        raise FixtureError(f"{where}: 'labeled_on' must be an ISO date") from None


def validate(fixtures: list[dict[str, Any]], policy: Policy) -> list[dict[str, Any]]:
    """Conformance: raise on the first fixture that breaks the contract."""
    seen: set[str] = set()
    for fx in fixtures:
        where = f"{fx.get('_file', '?')} id={fx.get('id')!r}"
        for key in _REQUIRED:
            if key not in fx:
                raise FixtureError(f"{where}: missing {key!r}")
        if not isinstance(fx["id"], str) or not fx["id"].strip():
            raise FixtureError(f"{where}: 'id' must be a non-empty string")
        if fx["id"] in seen:
            raise FixtureError(f"{where}: duplicate id")
        seen.add(fx["id"])

        rule = policy.rule_for(fx["task_type"])  # raises UnknownTaskType
        if fx.get("_file") and fx["_file"] != f"{fx['task_type']}.jsonl":
            raise FixtureError(f"{where}: task type {fx['task_type']!r} belongs "
                               f"in {fx['task_type']}.jsonl")
        if not isinstance(fx["input"], str) or not fx["input"].strip():
            raise FixtureError(f"{where}: 'input' must be a non-empty string")
        if fx["difficulty"] not in DIFFICULTIES:
            raise FixtureError(f"{where}: difficulty must be one of {sorted(DIFFICULTIES)}")
        if fx["provenance"] not in PROVENANCES:
            raise FixtureError(f"{where}: provenance must be one of {sorted(PROVENANCES)}")

        _check_expected(fx, rule, where)
        _check_label(fx, policy, where)
    return fixtures


def coverage(fixtures: list[dict[str, Any]], policy: Policy) -> dict[str, dict[str, int]]:
    """Audit: what exists, per task type. Reports; never passes or fails."""
    table = {t: {"easy": 0, "hard": 0, "total": 0, "reviewed": 0}
             for t in policy.task_types}
    for fx in fixtures:
        row = table[fx["task_type"]]
        row[fx["difficulty"]] += 1
        row["total"] += 1
        row["reviewed"] += fx["labeled_by"] != UNREVIEWED
    for row in table.values():
        row["short"] = max(0, TARGET_PER_TYPE - row["total"])
    return table


def freeze(fixtures: list[dict[str, Any]], policy: Policy,
           fixtures_dir: Path = FIXTURES_DIR) -> dict[str, Any]:
    """Lock the set: hash every file. Refuses while any label is unreviewed."""
    pending = [fx["id"] for fx in fixtures if fx["labeled_by"] == UNREVIEWED]
    if pending:
        shown = ", ".join(pending[:10]) + (" ..." if len(pending) > 10 else "")
        raise NotReviewed(f"{len(pending)} fixture(s) still UNREVIEWED: {shown}")

    files = {}
    for path in sorted(fixtures_dir.glob("*.jsonl")):
        files[path.name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "count": sum(1 for fx in fixtures if fx["_file"] == path.name),
        }
    return {
        "frozen_on": date.today().isoformat(),
        "policy_version": policy.version,
        "fixture_count": len(fixtures),
        "files": files,
    }


def check_manifest(manifest: dict[str, Any],
                   fixtures_dir: Path = FIXTURES_DIR) -> list[str]:
    """Every way the fixtures on disk differ from what was frozen."""
    problems = []
    on_disk = {p.name: p for p in fixtures_dir.glob("*.jsonl")}
    for name, entry in manifest["files"].items():
        if name not in on_disk:
            problems.append(f"{name}: frozen but missing")
        elif hashlib.sha256(on_disk[name].read_bytes()).hexdigest() != entry["sha256"]:
            problems.append(f"{name}: changed since it was frozen")
    for name in sorted(set(on_disk) - set(manifest["files"])):
        problems.append(f"{name}: added after the set was frozen")
    return problems
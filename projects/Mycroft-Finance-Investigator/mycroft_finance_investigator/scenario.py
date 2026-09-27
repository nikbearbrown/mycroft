"""Deterministic scenario sensitivities for a verified finance baseline.

The engine applies explicit exercise assumptions to verified actuals. It does
not predict, recommend, optimize, or approve a business decision.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from .finance import FinanceData, FinanceEngine


class ScenarioError(RuntimeError):
    """Raised when a scenario plan violates its deterministic contract."""


CATEGORIES = ("revenue", "cogs", "payroll", "opex")
METHODS = {"AMOUNT", "PERCENT_OF_ACTUAL"}
CENT = Decimal("0.01")
REPO_ROOT = Path(__file__).resolve().parents[3]


def _money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


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


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ScenarioError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _decimal(value: Any, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ScenarioError(f"{field} must be a decimal") from exc
    if not parsed.is_finite():
        raise ScenarioError(f"{field} must be finite")
    return parsed


def _reject_unknown(
    payload: dict[str, Any], allowed: set[str], label: str
) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ScenarioError(f"{label} contains unknown fields: {unknown}")


def load_scenario_plan(path: Path) -> dict[str, Any]:
    """Validate the scenario-plan contract without adding a runtime dependency."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScenarioError(f"scenario plan is not readable JSON: {path}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != "0.1.0":
        raise ScenarioError("scenario plan requires schema_version 0.1.0")
    _reject_unknown(
        payload,
        {"schema_version", "title", "classification", "baseline_run_id", "scenarios"},
        "scenario plan",
    )
    title = _required_string(payload, "title", "scenario plan")
    classification = _required_string(payload, "classification", "scenario plan")
    if classification != "SYNTHETIC_EXERCISE_ASSUMPTIONS":
        raise ScenarioError(
            "scenario plan.classification must be SYNTHETIC_EXERCISE_ASSUMPTIONS"
        )
    baseline_run_id = _required_string(payload, "baseline_run_id", "scenario plan")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ScenarioError("scenario plan.scenarios must be a non-empty list")

    seen_scenarios: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for scenario_index, scenario in enumerate(scenarios):
        label = f"scenarios[{scenario_index}]"
        if not isinstance(scenario, dict):
            raise ScenarioError(f"{label} must be an object")
        _reject_unknown(scenario, {"id", "name", "purpose", "assumptions"}, label)
        scenario_id = _required_string(scenario, "id", label)
        if scenario_id in seen_scenarios:
            raise ScenarioError(f"duplicate scenario id: {scenario_id}")
        seen_scenarios.add(scenario_id)
        name = _required_string(scenario, "name", label)
        purpose = _required_string(scenario, "purpose", label)
        assumptions = scenario.get("assumptions")
        if not isinstance(assumptions, list) or not assumptions:
            raise ScenarioError(f"{label}.assumptions must be a non-empty list")

        seen_categories: set[str] = set()
        normalized_assumptions = []
        for assumption_index, assumption in enumerate(assumptions):
            assumption_label = f"{label}.assumptions[{assumption_index}]"
            if not isinstance(assumption, dict):
                raise ScenarioError(f"{assumption_label} must be an object")
            _reject_unknown(
                assumption,
                {"category", "method", "value", "reasoning", "source"},
                assumption_label,
            )
            category = _required_string(assumption, "category", assumption_label)
            if category not in CATEGORIES:
                raise ScenarioError(
                    f"{assumption_label}.category must be one of {list(CATEGORIES)}"
                )
            if category in seen_categories:
                raise ScenarioError(
                    f"{label} has more than one assumption for category {category!r}"
                )
            seen_categories.add(category)
            method = _required_string(assumption, "method", assumption_label).upper()
            if method not in METHODS:
                raise ScenarioError(
                    f"{assumption_label}.method must be one of {sorted(METHODS)}"
                )
            value = _decimal(assumption.get("value"), f"{assumption_label}.value")
            reasoning = _required_string(assumption, "reasoning", assumption_label)
            source = _required_string(assumption, "source", assumption_label)
            normalized_assumptions.append(
                {
                    "category": category,
                    "method": method,
                    "value": str(value),
                    "reasoning": reasoning,
                    "source": source,
                }
            )
        normalized.append(
            {
                "id": scenario_id,
                "name": name,
                "purpose": purpose,
                "assumptions": normalized_assumptions,
            }
        )
    return {
        "schema_version": "0.1.0",
        "title": title,
        "classification": classification,
        "baseline_run_id": baseline_run_id,
        "scenarios": normalized,
    }


def _load_baseline(
    verified_dir: Path, run_log_path: Path, expected_run_id: str
) -> tuple[
    dict[str, Decimal], dict[str, list[str]], dict[str, Any], dict[str, str]
]:
    try:
        run_log = json.loads(run_log_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScenarioError(f"baseline run log is not readable JSON: {run_log_path}") from exc
    if not isinstance(run_log, dict) or run_log.get("workflow") != "mycroft-finance-investigator":
        raise ScenarioError("baseline run log belongs to a different workflow")
    if run_log.get("run_id") != expected_run_id:
        raise ScenarioError(
            f"scenario baseline_run_id {expected_run_id!r} does not match "
            f"run log {run_log.get('run_id')!r}"
        )
    investigation = run_log.get("investigation")
    if (
        not isinstance(investigation, dict)
        or investigation.get("status") != "COMPLETED_PENDING_HUMAN_REVIEW"
    ):
        raise ScenarioError("baseline investigation is not complete and reviewable")

    validation = run_log.get("validation")
    if not isinstance(validation, dict) or validation.get("status") != "CONFORMANT_SAMPLE":
        raise ScenarioError("baseline run log lacks a conformant validation result")
    expected_hashes = validation.get("source_hashes")
    if not isinstance(expected_hashes, dict) or not expected_hashes:
        raise ScenarioError("baseline run log lacks verified source hashes")
    observed_hashes: dict[str, str] = {}
    for file_name, expected_hash in expected_hashes.items():
        path = verified_dir / file_name
        if not path.is_file():
            raise ScenarioError(f"verified baseline file is missing: {path}")
        observed_hashes[file_name] = _sha256(path)
        if observed_hashes[file_name] != expected_hash:
            raise ScenarioError(
                f"verified baseline hash does not match run log for {file_name}"
            )

    engine = FinanceEngine(FinanceData(verified_dir))
    category_lines = engine.category_variances()
    actuals = {line.category: line.actual for line in category_lines}
    evidence = {line.category: list(line.evidence) for line in category_lines}
    ebitda = engine.ebitda_variance()
    trace = investigation.get("trace")
    try:
        logged_actual = Decimal(str(trace[0]["observation"]["ebitda"]["actual"]))
    except (KeyError, IndexError, InvalidOperation, TypeError) as exc:
        raise ScenarioError("baseline run log is missing its EBITDA observation") from exc
    if logged_actual != ebitda.actual:
        raise ScenarioError(
            f"verified baseline EBITDA {_money(ebitda.actual)} does not match "
            f"run log {_money(logged_actual)}"
        )
    return actuals, evidence, run_log, observed_hashes


def _scenario_result(
    scenario: dict[str, Any],
    actuals: dict[str, Decimal],
    evidence: dict[str, list[str]],
    plan_path: Path,
) -> dict[str, Any]:
    scenario_actuals = dict(actuals)
    rendered_assumptions = []
    for assumption in scenario["assumptions"]:
        category = assumption["category"]
        baseline = actuals[category]
        value = Decimal(assumption["value"])
        if assumption["method"] == "PERCENT_OF_ACTUAL":
            adjustment = (baseline * value / Decimal("100")).quantize(
                CENT, rounding=ROUND_HALF_UP
            )
        else:
            adjustment = value.quantize(CENT, rounding=ROUND_HALF_UP)
        resulting = baseline + adjustment
        if resulting < 0:
            raise ScenarioError(
                f"scenario {scenario['id']!r} makes {category} negative: {_money(resulting)}"
            )
        scenario_actuals[category] = resulting
        impact = adjustment if category == "revenue" else -adjustment
        rendered_assumptions.append(
            {
                **assumption,
                "baseline_actual": _money(baseline),
                "adjustment": _money(adjustment),
                "resulting_actual": _money(resulting),
                "ebitda_impact": _money(impact),
                "evidence": [
                    *evidence[category],
                    (
                        f"{_portable_path(plan_path)}:scenario_id={scenario['id']}:"
                        f"category={category}"
                    ),
                ],
            }
        )

    baseline_ebitda = actuals["revenue"] - sum(
        (actuals[category] for category in CATEGORIES[1:]), Decimal("0")
    )
    scenario_ebitda = scenario_actuals["revenue"] - sum(
        (scenario_actuals[category] for category in CATEGORIES[1:]), Decimal("0")
    )
    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "purpose": scenario["purpose"],
        "classification": "SIMULATION_NOT_FORECAST",
        "baseline_ebitda": _money(baseline_ebitda),
        "scenario_ebitda": _money(scenario_ebitda),
        "difference_from_baseline": _money(scenario_ebitda - baseline_ebitda),
        "category_actuals": {
            category: _money(scenario_actuals[category]) for category in CATEGORIES
        },
        "assumptions": rendered_assumptions,
        "recommendation": None,
        "decision": "HUMAN_REQUIRED",
    }


def run_scenarios(
    plan_path: Path,
    verified_dir: Path,
    run_log_path: Path,
    run_id: str,
) -> dict[str, Any]:
    """Apply explicit assumptions and return an evidence-linked decision pack."""

    plan = load_scenario_plan(plan_path)
    actuals, evidence, _, verified_hashes = _load_baseline(
        verified_dir, run_log_path, plan["baseline_run_id"]
    )
    baseline_ebitda = actuals["revenue"] - sum(
        (actuals[category] for category in CATEGORIES[1:]), Decimal("0")
    )
    scenarios = [
        _scenario_result(scenario, actuals, evidence, plan_path)
        for scenario in plan["scenarios"]
    ]
    return {
        "schema_version": "0.1.0",
        "workflow": "mycroft-finance-investigator-scenarios",
        "run_id": run_id,
        "classification": "SIMULATION_NOT_FORECAST",
        "source_plan": _portable_path(plan_path),
        "source_plan_sha256": _sha256(plan_path),
        "baseline_run": _portable_path(run_log_path),
        "baseline_run_sha256": _sha256(run_log_path),
        "baseline_run_id": plan["baseline_run_id"],
        "verified_data_sha256": verified_hashes,
        "baseline_actuals": {category: _money(actuals[category]) for category in CATEGORIES},
        "baseline_ebitda": _money(baseline_ebitda),
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "recommendation": None,
        "decision": "HUMAN_REQUIRED",
        "adequacy": "PENDING_HUMAN_REVIEW",
        "boundary": (
            "Outputs are arithmetic sensitivities to synthetic exercise assumptions; "
            "they are not forecasts, probabilities, recommendations, or approvals."
        ),
    }


def write_scenario_artifacts(
    payload: dict[str, Any], log_path: Path, report_path: Path
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Finance Investigator Scenario Decision Pack",
        "",
        f"- Run: `{payload['run_id']}`",
        f"- Baseline investigation: `{payload['baseline_run_id']}`",
        f"- Baseline actual EBITDA: {payload['baseline_ebitda']}",
        "- Classification: `SIMULATION_NOT_FORECAST`",
        "- Recommendation: `NONE`",
        "- Decision: `HUMAN_REQUIRED`",
        "- Adequacy: `PENDING_HUMAN_REVIEW`",
        "",
        payload["boundary"],
        "",
        "## Comparison",
        "",
        "| Scenario | EBITDA | Difference from baseline |",
        "|---|---:|---:|",
    ]
    for scenario in payload["scenarios"]:
        lines.append(
            f"| {scenario['name']} | {scenario['scenario_ebitda']} | "
            f"{scenario['difference_from_baseline']} |"
        )
    lines.extend(["", "## Explicit Assumptions", ""])
    for scenario in payload["scenarios"]:
        lines.extend([f"### {scenario['name']}", "", scenario["purpose"], ""])
        lines.extend(
            [
                "| Category | Method | Input | Adjustment | EBITDA impact | Source |",
                "|---|---|---:|---:|---:|---|",
            ]
        )
        for assumption in scenario["assumptions"]:
            lines.append(
                f"| {assumption['category']} | `{assumption['method']}` | "
                f"{assumption['value']} | {assumption['adjustment']} | "
                f"{assumption['ebitda_impact']} | {assumption['source']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Human Decision Required",
            "",
            (
                "A named finance owner must approve or replace each assumption, "
                "judge whether the scenarios are useful and sufficient, and make "
                "any resulting business decision. This pack makes no recommendation."
            ),
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")

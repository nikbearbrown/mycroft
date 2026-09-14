"""Constrained supervisor and specialist routing for evidence-gap triage.

The supervisor delegates deterministic evidence collection. Specialists may
verify calculations and collect correlated records, but they cannot infer a
business cause, approve materiality, recommend action, or clear a human gate.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .finance import FinanceData, FinanceEngine, money


class RoutingError(RuntimeError):
    """Raised when routing inputs or specialist results violate the contract."""


CATEGORIES = ("revenue", "cogs", "payroll", "opex")
SPECIALISTS = {
    "lineage-specialist",
    "revenue-specialist",
    "cost-specialist",
    "workforce-specialist",
}
EXPECTED_ROUTES = set(CATEGORIES)
REPO_ROOT = Path(__file__).resolve().parents[3]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _payload_hash(payload: Any) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _portable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RoutingError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _reject_unknown(
    payload: dict[str, Any], allowed: set[str], label: str
) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise RoutingError(f"{label} contains unknown fields: {unknown}")


def load_routing_plan(path: Path) -> dict[str, Any]:
    """Strictly validate a supervisor routing plan."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutingError(f"routing plan is not readable JSON: {path}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != "0.1.0":
        raise RoutingError("routing plan requires schema_version 0.1.0")
    _reject_unknown(
        payload,
        {
            "schema_version",
            "classification",
            "trend_run_id",
            "max_delegations",
            "control_specialist",
            "routes",
        },
        "routing plan",
    )
    classification = _required_string(payload, "classification", "routing plan")
    if classification != "SYNTHETIC_EVIDENCE_GAP_ROUTING":
        raise RoutingError(
            "routing plan.classification must be "
            "SYNTHETIC_EVIDENCE_GAP_ROUTING"
        )
    trend_run_id = _required_string(payload, "trend_run_id", "routing plan")
    max_delegations = payload.get("max_delegations")
    if not isinstance(max_delegations, int) or isinstance(max_delegations, bool):
        raise RoutingError("routing plan.max_delegations must be an integer")
    if max_delegations < 1:
        raise RoutingError("routing plan.max_delegations must be positive")
    control_specialist = _required_string(
        payload, "control_specialist", "routing plan"
    )
    if control_specialist != "lineage-specialist":
        raise RoutingError("control_specialist must be lineage-specialist")
    routes = payload.get("routes")
    if not isinstance(routes, dict) or set(routes) != EXPECTED_ROUTES:
        raise RoutingError(
            f"routing plan.routes must contain exactly {sorted(EXPECTED_ROUTES)}"
        )
    normalized_routes: dict[str, str] = {}
    for category in CATEGORIES:
        specialist = routes.get(category)
        if not isinstance(specialist, str) or specialist not in SPECIALISTS:
            raise RoutingError(f"unsupported specialist for {category}: {specialist}")
        normalized_routes[category] = specialist
    expected = {
        "revenue": "revenue-specialist",
        "cogs": "cost-specialist",
        "payroll": "workforce-specialist",
        "opex": "cost-specialist",
    }
    if normalized_routes != expected:
        raise RoutingError("category routes violate specialist scope")
    return {
        "schema_version": "0.1.0",
        "classification": classification,
        "trend_run_id": trend_run_id,
        "max_delegations": max_delegations,
        "control_specialist": control_specialist,
        "routes": normalized_routes,
    }


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutingError(f"{label} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RoutingError(f"{label} must be a JSON object: {path}")
    return payload


def _load_trend(path: Path, expected_run_id: str) -> dict[str, Any]:
    trend = _load_json(path, "trend log")
    if trend.get("workflow") != "mycroft-finance-investigator-trend":
        raise RoutingError("trend log belongs to a different workflow")
    if trend.get("run_id") != expected_run_id:
        raise RoutingError(
            f"trend run {trend.get('run_id')!r} does not match "
            f"routing plan {expected_run_id!r}"
        )
    if trend.get("classification") != "HISTORICAL_COMPARISON_NOT_FORECAST":
        raise RoutingError("trend log lacks the historical-only classification")
    if (
        trend.get("causal_explanation") is not None
        or trend.get("forecast") is not None
        or trend.get("recommendation") is not None
        or trend.get("human_gate", {}).get("status") != "OPEN"
    ):
        raise RoutingError("trend log does not preserve the open human boundary")
    periods = trend.get("periods")
    category_trends = trend.get("category_trends")
    if not isinstance(periods, list) or not periods:
        raise RoutingError("trend log has no source periods")
    if not isinstance(category_trends, list):
        raise RoutingError("trend log has no category trends")
    return trend


def _verified_source_runs(
    trend: dict[str, Any], threshold: Decimal
) -> tuple[dict[str, dict[str, Any]], dict[str, FinanceEngine], list[str]]:
    source_runs: dict[str, dict[str, Any]] = {}
    engines: dict[str, FinanceEngine] = {}
    lineage: list[str] = []
    for period in trend["periods"]:
        period_name = str(period.get("period", ""))
        run_log_path = _repo_path(str(period.get("run_log", "")))
        if _sha256(run_log_path) != period.get("run_log_sha256"):
            raise RoutingError(f"source run hash mismatch for {period_name}")
        source_run = _load_json(run_log_path, "source run")
        if (
            source_run.get("run_id") != period.get("source_run_id")
            or source_run.get("config", {}).get("period") != period_name
            or source_run.get("config", {}).get("entity") != trend.get("entity")
        ):
            raise RoutingError(f"source run scope mismatch for {period_name}")
        investigation = source_run.get("investigation", {})
        if (
            investigation.get("status") != "COMPLETED_PENDING_HUMAN_REVIEW"
            or investigation.get("current_explanation") is not None
            or investigation.get("human_gate", {}).get("status") != "OPEN"
        ):
            raise RoutingError(f"source run human boundary mismatch for {period_name}")
        verified_dir = _repo_path(str(period.get("verified_dir", "")))
        recorded_hashes = period.get("verified_source_hashes")
        if not isinstance(recorded_hashes, dict) or not recorded_hashes:
            raise RoutingError(f"verified source hashes missing for {period_name}")
        for file_name, expected_hash in recorded_hashes.items():
            source_path = verified_dir / file_name
            if not source_path.is_file() or _sha256(source_path) != expected_hash:
                raise RoutingError(
                    f"verified source hash mismatch for {period_name}/{file_name}"
                )
        engine = FinanceEngine(FinanceData(verified_dir))
        ebitda = engine.ebitda_variance()
        if money(ebitda.actual) != period.get("actual_ebitda"):
            raise RoutingError(f"recomputed EBITDA mismatch for {period_name}")
        source_runs[period_name] = source_run
        engines[period_name] = engine
        lineage.extend(
            [
                f"{_portable_path(run_log_path)}#run_id={source_run['run_id']}",
                *[
                    f"{_portable_path(verified_dir / file_name)}#sha256={file_hash}"
                    for file_name, file_hash in sorted(recorded_hashes.items())
                ],
            ]
        )
    return source_runs, engines, sorted(lineage)


def _category_priority(category_trend: dict[str, Any]) -> Decimal:
    total = Decimal("0")
    for period in category_trend["periods"]:
        if period.get("material_adverse"):
            try:
                impact = Decimal(str(period["performance_impact"]))
            except (KeyError, InvalidOperation) as exc:
                raise RoutingError("category trend has an invalid impact") from exc
            total += abs(impact)
    return total


def _specialist_result(
    category: str,
    specialist: str,
    category_trend: dict[str, Any],
    engines: dict[str, FinanceEngine],
    threshold: Decimal,
) -> dict[str, Any]:
    periods: list[dict[str, Any]] = []
    evidence: set[str] = set()
    evidence_kinds = {"VERIFIED_CALCULATION_SOURCE"}
    for observation in category_trend["periods"]:
        period = observation["period"]
        engine = engines[period]
        category_line = next(
            line for line in engine.category_variances() if line.category == category
        )
        if money(category_line.performance_impact) != observation["performance_impact"]:
            raise RoutingError(f"recomputed category mismatch for {period}/{category}")
        account_lines = [
            line.to_dict()
            for line in engine.account_variances()
            if line.category == category
        ]
        driver_rows = (
            engine.driver_rows(category)
            if specialist in {"revenue-specialist", "workforce-specialist"}
            else []
        )
        if driver_rows:
            evidence_kinds.add("CORRELATED_DRIVER_RECORD")
        for reference in category_line.evidence:
            evidence.add(f"{period}:{reference}")
        for line in account_lines:
            evidence.update(f"{period}:{item}" for item in line["evidence"])
        for row in driver_rows:
            evidence.add(f"{period}:{row['evidence']}")
        periods.append(
            {
                "period": period,
                "performance_impact": observation["performance_impact"],
                "material_adverse": observation["material_adverse"],
                "account_evidence": account_lines,
                "correlated_driver_records": driver_rows,
            }
        )
    missing = ["OWNER_CAUSAL_EXPLANATION"]
    if specialist == "cost-specialist":
        missing.insert(0, "OPERATIONAL_DRIVER_RECORDS")
    return {
        "status": "EVIDENCE_COLLECTED_PENDING_OWNER",
        "category": category,
        "specialist": specialist,
        "materiality_amount": money(threshold),
        "periods": periods,
        "evidence_kinds": sorted(evidence_kinds),
        "evidence": sorted(evidence),
        "missing_evidence": missing,
        "causal_explanation": None,
        "recommendation": None,
    }


def run_orchestration(
    plan_path: Path, trend_log_path: Path, run_id: str
) -> dict[str, Any]:
    """Route recurring gaps to scoped specialists and retain all handoffs."""

    plan = load_routing_plan(plan_path)
    trend = _load_trend(trend_log_path, plan["trend_run_id"])
    threshold = Decimal(str(trend["materiality_amount"]))
    _, engines, lineage = _verified_source_runs(trend, threshold)
    recurring = [
        item
        for item in trend["category_trends"]
        if item.get("recurring_material_adverse") is True
    ]
    recurring.sort(key=lambda item: (-_category_priority(item), item["category"]))
    required_delegations = 1 + len(recurring)
    if required_delegations > plan["max_delegations"]:
        raise RoutingError(
            f"routing requires {required_delegations} delegations but limit is "
            f"{plan['max_delegations']}"
        )

    handoffs: list[dict[str, Any]] = [
        {
            "sequence": 1,
            "from": "supervisor",
            "to": plan["control_specialist"],
            "task": "verify-source-chain",
            "result": {
                "status": "VERIFIED_INPUT_CHAIN",
                "evidence": lineage,
            },
        }
    ]
    tasks = []
    for rank, category_trend in enumerate(recurring, start=1):
        category = category_trend["category"]
        specialist = plan["routes"][category]
        result = _specialist_result(
            category, specialist, category_trend, engines, threshold
        )
        task = {
            "task_id": f"gap-{category}",
            "rank": rank,
            "category": category,
            "specialist": specialist,
            "cumulative_material_adverse_impact": money(
                _category_priority(category_trend)
            ),
            "adverse_period_count": category_trend["material_adverse_count"],
            "rationale": (
                f"{category} was materially adverse in "
                f"{category_trend['material_adverse_count']} included periods"
            ),
            "result": result,
            "result_sha256": _payload_hash(result),
        }
        tasks.append(task)
        handoffs.append(
            {
                "sequence": len(handoffs) + 1,
                "from": "supervisor",
                "to": specialist,
                "task": task["task_id"],
                "result": {
                    "status": result["status"],
                    "result_sha256": task["result_sha256"],
                },
            }
        )
    return {
        "workflow": "mycroft-finance-investigator-orchestration",
        "run_id": run_id,
        "schema_version": "0.1.0",
        "classification": "EVIDENCE_GAP_WORK_QUEUE_NOT_CAUSAL_ANALYSIS",
        "routing_plan": _portable_path(plan_path),
        "routing_plan_sha256": _sha256(plan_path),
        "trend_log": _portable_path(trend_log_path),
        "trend_log_sha256": _sha256(trend_log_path),
        "trend_run_id": trend["run_id"],
        "supervisor": {
            "policy": "deterministic-specialist-routing-v0.1",
            "max_delegations": plan["max_delegations"],
            "delegations_used": len(handoffs),
        },
        "tasks": tasks,
        "handoffs": handoffs,
        "causal_explanation": None,
        "recommendation": None,
        "human_gate": {
            "status": "OPEN",
            "required": [
                "Judge whether the routed evidence is adequate",
                "Supply additional operational evidence for unresolved gaps",
                "Provide and support any causal explanation",
                "Approve or block distribution",
            ],
        },
    }


def write_orchestration_artifacts(
    payload: dict[str, Any], log_path: Path, report_path: Path
) -> None:
    """Write the machine trace and human evidence-gap work queue."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Evidence-Gap Planner and Specialist Routing",
        "",
        "## Boundary",
        "",
        f"- Classification: `{payload['classification']}`",
        "- Specialists collect and verify evidence; they do not infer causation.",
        "- Recommendation: `NONE`",
        "- Human gate: `OPEN`",
        "",
        "## Supervisor Summary",
        "",
        f"- Run ID: `{payload['run_id']}`",
        f"- Trend run: `{payload['trend_run_id']}`",
        (
            f"- Delegations: {payload['supervisor']['delegations_used']} of "
            f"{payload['supervisor']['max_delegations']}"
        ),
        "",
        "## Prioritized Work Queue",
        "",
        "| Rank | Category | Specialist | Cumulative adverse impact | Missing evidence |",
        "|---:|---|---|---:|---|",
    ]
    for task in payload["tasks"]:
        missing = ", ".join(task["result"]["missing_evidence"])
        lines.append(
            f"| {task['rank']} | {task['category']} | `{task['specialist']}` | "
            f"{task['cumulative_material_adverse_impact']} | {missing} |"
        )
    lines.extend(
        [
            "",
            "## Handoff Trace",
            "",
            "| Sequence | From | To | Task | Result |",
            "|---:|---|---|---|---|",
        ]
    )
    for handoff in payload["handoffs"]:
        lines.append(
            f"| {handoff['sequence']} | `{handoff['from']}` | "
            f"`{handoff['to']}` | `{handoff['task']}` | "
            f"`{handoff['result']['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Human Review",
            "",
            *[f"- [ ] {item}" for item in payload["human_gate"]["required"]],
            "",
            "_A prioritized queue is not an approved explanation or decision._",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")

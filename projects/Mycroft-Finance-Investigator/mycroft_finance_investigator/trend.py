"""Deterministic comparison of verified monthly finance investigations.

The comparison describes historical movements and recurring material variance
categories. It does not forecast, infer business causes, or recommend action.
"""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from .finance import FinanceData, FinanceEngine


class TrendError(RuntimeError):
    """Raised when a trend plan or one of its bound runs is invalid."""


CATEGORIES = ("revenue", "cogs", "payroll", "opex")
SOURCE_FILES = {
    "account_mapping.csv",
    "budget.csv",
    "actuals.csv",
    "ledger.csv",
    "customers.csv",
    "headcount.csv",
}
CENT = Decimal("0.01")
PERIOD_PATTERN = re.compile(r"^[0-9]{4}-(?:0[1-9]|1[0-2])$")
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
        return str(path.resolve())


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise TrendError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def _reject_unknown(
    payload: dict[str, Any], allowed: set[str], label: str
) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise TrendError(f"{label} contains unknown fields: {unknown}")


def _positive_decimal(value: Any, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TrendError(f"{field} must be a decimal") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise TrendError(f"{field} must be a positive finite decimal")
    return parsed


def load_trend_plan(path: Path) -> dict[str, Any]:
    """Load and strictly validate a historical-comparison plan."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrendError(f"trend plan is not readable JSON: {path}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != "0.1.0":
        raise TrendError("trend plan requires schema_version 0.1.0")
    _reject_unknown(
        payload,
        {
            "schema_version",
            "classification",
            "entity",
            "question",
            "materiality_amount",
            "materiality_status",
            "periods",
        },
        "trend plan",
    )
    classification = _required_string(payload, "classification", "trend plan")
    if classification != "SYNTHETIC_HISTORICAL_COMPARISON":
        raise TrendError(
            "trend plan.classification must be "
            "SYNTHETIC_HISTORICAL_COMPARISON"
        )
    entity = _required_string(payload, "entity", "trend plan")
    question = _required_string(payload, "question", "trend plan")
    threshold = _positive_decimal(
        payload.get("materiality_amount"), "trend plan.materiality_amount"
    )
    materiality_status = _required_string(
        payload, "materiality_status", "trend plan"
    )
    if materiality_status != "DEMO_UNAPPROVED":
        raise TrendError(
            "trend plan.materiality_status must be DEMO_UNAPPROVED"
        )
    periods = payload.get("periods")
    if not isinstance(periods, list) or len(periods) < 2:
        raise TrendError("trend plan.periods must contain at least two periods")

    normalized_periods: list[dict[str, str]] = []
    seen_periods: set[str] = set()
    for index, period_entry in enumerate(periods):
        label = f"periods[{index}]"
        if not isinstance(period_entry, dict):
            raise TrendError(f"{label} must be an object")
        _reject_unknown(period_entry, {"period", "run_log", "verified_dir"}, label)
        period = _required_string(period_entry, "period", label)
        if not PERIOD_PATTERN.fullmatch(period):
            raise TrendError(f"{label}.period must use YYYY-MM")
        if period in seen_periods:
            raise TrendError(f"duplicate period: {period}")
        seen_periods.add(period)
        normalized_periods.append(
            {
                "period": period,
                "run_log": _required_string(period_entry, "run_log", label),
                "verified_dir": _required_string(
                    period_entry, "verified_dir", label
                ),
            }
        )
    ordered_periods = sorted(entry["period"] for entry in normalized_periods)
    if [entry["period"] for entry in normalized_periods] != ordered_periods:
        raise TrendError("trend plan periods must be in ascending order")
    return {
        "schema_version": "0.1.0",
        "classification": classification,
        "entity": entity,
        "question": question,
        "materiality_amount": _money(threshold),
        "materiality_status": materiality_status,
        "periods": normalized_periods,
    }


def _load_run(
    entry: dict[str, str], entity: str
) -> tuple[dict[str, Any], FinanceEngine, dict[str, str], Path]:
    run_log_path = _repo_path(entry["run_log"])
    verified_dir = _repo_path(entry["verified_dir"])
    try:
        run_log = json.loads(run_log_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrendError(f"run log is not readable JSON: {run_log_path}") from exc
    if (
        not isinstance(run_log, dict)
        or run_log.get("workflow") != "mycroft-finance-investigator"
    ):
        raise TrendError(f"run log belongs to another workflow: {run_log_path}")
    if run_log.get("mode") != "synthetic_sample":
        raise TrendError(f"run log is not a synthetic sample: {run_log_path}")
    config = run_log.get("config")
    if not isinstance(config, dict):
        raise TrendError(f"run log lacks config: {run_log_path}")
    if config.get("entity") != entity:
        raise TrendError(
            f"run entity {config.get('entity')!r} does not match plan {entity!r}"
        )
    if config.get("period") != entry["period"]:
        raise TrendError(
            f"run period {config.get('period')!r} does not match "
            f"plan {entry['period']!r}"
        )
    investigation = run_log.get("investigation")
    if (
        not isinstance(investigation, dict)
        or investigation.get("status") != "COMPLETED_PENDING_HUMAN_REVIEW"
        or investigation.get("current_explanation") is not None
        or investigation.get("human_gate", {}).get("status") != "OPEN"
    ):
        raise TrendError(f"run is not complete with an open human gate: {run_log_path}")
    validation = run_log.get("validation")
    if not isinstance(validation, dict) or validation.get("status") != "CONFORMANT_SAMPLE":
        raise TrendError(f"run lacks conformant validation: {run_log_path}")
    expected_hashes = validation.get("source_hashes")
    if not isinstance(expected_hashes, dict) or not expected_hashes:
        raise TrendError(f"run lacks verified source hashes: {run_log_path}")
    if set(expected_hashes) != SOURCE_FILES:
        raise TrendError(
            f"run source-hash inventory does not match the finance pack: {run_log_path}"
        )
    observed_hashes: dict[str, str] = {}
    for file_name, expected_hash in expected_hashes.items():
        source_path = verified_dir / file_name
        if not source_path.is_file():
            raise TrendError(f"verified source is missing: {source_path}")
        observed_hashes[file_name] = _sha256(source_path)
        if observed_hashes[file_name] != expected_hash:
            raise TrendError(
                f"verified source hash does not match run log for {file_name}"
            )

    engine = FinanceEngine(FinanceData(verified_dir))
    for row in [
        *engine.data.budget_rows,
        *engine.data.actual_rows,
        *engine.data.ledger_rows,
    ]:
        if row["entity"] != entity or row["period"] != entry["period"]:
            raise TrendError(
                f"verified row scope does not match {entity} {entry['period']}"
            )
    ebitda = engine.ebitda_variance()
    try:
        logged_ebitda = Decimal(
            str(investigation["trace"][0]["observation"]["ebitda"]["actual"])
        )
    except (KeyError, IndexError, InvalidOperation, TypeError) as exc:
        raise TrendError(f"run lacks its EBITDA observation: {run_log_path}") from exc
    if logged_ebitda != ebitda.actual:
        raise TrendError(
            f"verified EBITDA {_money(ebitda.actual)} does not match run log "
            f"{_money(logged_ebitda)}"
        )
    return run_log, engine, observed_hashes, run_log_path


def run_trend(plan_path: Path, run_id: str) -> dict[str, Any]:
    """Compare verified runs while retaining their evidence and review gates."""

    plan = load_trend_plan(plan_path)
    threshold = Decimal(plan["materiality_amount"])
    period_results: list[dict[str, Any]] = []
    category_periods: dict[str, list[dict[str, Any]]] = {
        category: [] for category in CATEGORIES
    }
    seen_run_ids: set[str] = set()
    previous_actual: Decimal | None = None

    for entry in plan["periods"]:
        run_log, engine, hashes, run_log_path = _load_run(entry, plan["entity"])
        source_run_id = str(run_log.get("run_id", ""))
        if not source_run_id:
            raise TrendError(f"run log lacks run_id: {run_log_path}")
        if source_run_id in seen_run_ids:
            raise TrendError(f"duplicate source run_id: {source_run_id}")
        seen_run_ids.add(source_run_id)
        ebitda = engine.ebitda_variance()
        movement = "FIRST_PERIOD"
        change: Decimal | None = None
        if previous_actual is not None:
            change = ebitda.actual - previous_actual
            movement = (
                "IMPROVED"
                if change > 0
                else "DETERIORATED"
                if change < 0
                else "UNCHANGED"
            )
        previous_actual = ebitda.actual
        period_results.append(
            {
                "period": entry["period"],
                "source_run_id": source_run_id,
                "run_log": _portable_path(run_log_path),
                "run_log_sha256": _sha256(run_log_path),
                "verified_dir": _portable_path(_repo_path(entry["verified_dir"])),
                "verified_source_hashes": hashes,
                "budget_ebitda": _money(ebitda.budget),
                "actual_ebitda": _money(ebitda.actual),
                "variance": _money(ebitda.variance),
                "actual_change_from_previous": (
                    None if change is None else _money(change)
                ),
                "movement": movement,
                "human_gate": "OPEN",
            }
        )
        for line in engine.category_variances():
            category_periods[line.category].append(
                {
                    "period": entry["period"],
                    "performance_impact": _money(line.performance_impact),
                    "material_adverse": line.performance_impact <= -threshold,
                    "material_favorable": line.performance_impact >= threshold,
                    "evidence": [
                        f"{_portable_path(run_log_path)}#run_id={source_run_id}",
                        *[
                            f"{_portable_path(_repo_path(entry['verified_dir']))}/"
                            f"{reference}"
                            for reference in line.evidence
                        ],
                    ],
                }
            )

    category_trends = []
    for category in CATEGORIES:
        observations = category_periods[category]
        adverse_count = sum(item["material_adverse"] for item in observations)
        favorable_count = sum(item["material_favorable"] for item in observations)
        category_trends.append(
            {
                "category": category,
                "periods": observations,
                "material_adverse_count": adverse_count,
                "material_favorable_count": favorable_count,
                "recurring_material_adverse": adverse_count >= 2,
            }
        )

    recurring = [
        trend["category"]
        for trend in category_trends
        if trend["recurring_material_adverse"]
    ]
    return {
        "workflow": "mycroft-finance-investigator-trend",
        "run_id": run_id,
        "schema_version": "0.1.0",
        "classification": "HISTORICAL_COMPARISON_NOT_FORECAST",
        "source_classification": plan["classification"],
        "plan": _portable_path(plan_path),
        "plan_sha256": _sha256(plan_path),
        "entity": plan["entity"],
        "question": plan["question"],
        "materiality_amount": plan["materiality_amount"],
        "materiality_status": plan["materiality_status"],
        "period_count": len(period_results),
        "periods": period_results,
        "category_trends": category_trends,
        "verified_findings": {
            "recurring_material_adverse_categories": recurring,
            "definition": "Material adverse in at least two included periods.",
        },
        "causal_explanation": None,
        "forecast": None,
        "recommendation": None,
        "human_gate": {
            "status": "OPEN",
            "required": [
                "Approve or replace the demo materiality threshold",
                "Assess causal explanations using additional business evidence",
                "Determine whether the history is adequate for a decision",
                "Approve or block distribution",
            ],
        },
    }


def write_trend_artifacts(
    payload: dict[str, Any], log_path: Path, report_path: Path
) -> None:
    """Write machine-readable and human-review historical comparisons."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Multi-Month Performance Investigation",
        "",
        "## Decision Boundary",
        "",
        "- Classification: `HISTORICAL_COMPARISON_NOT_FORECAST`",
        "- This report compares verified historical calculations only.",
        "- Causation, forecasts, recommendations, and distribution approval are not supplied.",
        "- Human gate: `OPEN`",
        "",
        "## Scope",
        "",
        f"- Run ID: `{payload['run_id']}`",
        f"- Entity: {payload['entity']}",
        f"- Periods compared: {payload['period_count']}",
        f"- Materiality: {payload['materiality_amount']} (`{payload['materiality_status']}`)",
        (
            f"- Plan: `{payload['plan']}` "
            f"(SHA-256 `{payload['plan_sha256']}`)"
        ),
        "",
        "## Historical EBITDA",
        "",
        "| Period | Budget | Actual | Variance | Change from prior | Movement | Source run |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for period in payload["periods"]:
        change = period["actual_change_from_previous"] or "—"
        lines.append(
            f"| {period['period']} | {period['budget_ebitda']} | "
            f"{period['actual_ebitda']} | {period['variance']} | {change} | "
            f"`{period['movement']}` | `{period['source_run_id']}` |"
        )
    lines.extend(
        [
            "",
            "## Category Pattern",
            "",
            (
                "A recurring material adverse category meets the unapproved "
                "demo threshold in at least two included periods."
            ),
            "",
            (
                "| Category | Impacts by period | Adverse periods | "
                "Favorable periods | Recurring adverse |"
            ),
            "|---|---|---:|---:|---|",
        ]
    )
    for trend in payload["category_trends"]:
        impacts = "; ".join(
            f"{item['period']}: {item['performance_impact']}"
            for item in trend["periods"]
        )
        recurring = "YES" if trend["recurring_material_adverse"] else "NO"
        lines.append(
            f"| {trend['category']} | {impacts} | "
            f"{trend['material_adverse_count']} | "
            f"{trend['material_favorable_count']} | `{recurring}` |"
        )
    recurring_categories = payload["verified_findings"][
        "recurring_material_adverse_categories"
    ]
    lines.extend(
        [
            "",
            "## Verified Pattern",
            "",
            (
                "- Recurring material adverse categories: "
                + (", ".join(f"`{item}`" for item in recurring_categories) or "none")
            ),
            "- This is a mathematical pattern, not a causal explanation.",
            "",
            "## Source Runs",
            "",
        ]
    )
    for period in payload["periods"]:
        lines.append(
            f"- {period['period']}: `{period['run_log']}` "
            f"(SHA-256 `{period['run_log_sha256']}`)"
        )
    lines.extend(
        [
            "",
            "## Current Explanation — Owner Required",
            "",
            "_Intentionally blank. Recurrence does not establish why a variance occurred._",
            "",
            "## Human Review",
            "",
        ]
    )
    for requirement in payload["human_gate"]["required"]:
        lines.append(f"- [ ] {requirement}")
    lines.extend(["", "- Reviewer:", "- Review date:", "- Decision:", ""])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")

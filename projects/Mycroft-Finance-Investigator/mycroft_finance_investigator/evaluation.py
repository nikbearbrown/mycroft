"""Deterministic adversarial evaluation for the Finance Investigator.

Each case runs in an isolated temporary copy. The evaluator reports whether the
observed behavior matches an explicit expectation; it never converts those
observations into a model-confidence claim.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from .agent import InvestigationAgent
from .finance import FinanceData, FinanceEngine
from .review import ReviewError, validate_review_decision
from .validation import ValidationError, validate_finance_pack


class EvaluationError(RuntimeError):
    """Raised when the evaluation specification itself is invalid."""


ALLOWED_STAGES = {"validation", "investigation", "review"}
ALLOWED_OPERATIONS = {
    "baseline",
    "ledger_mismatch",
    "unmapped_account",
    "customer_revenue_mismatch",
    "headcount_payroll_mismatch",
    "step_limit",
    "agent_self_approval",
}
STAGE_OPERATIONS = {
    "validation": {
        "baseline",
        "ledger_mismatch",
        "unmapped_account",
        "customer_revenue_mismatch",
        "headcount_payroll_mismatch",
    },
    "investigation": {"baseline", "step_limit"},
    "review": {"agent_self_approval"},
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


def _required_string(payload: dict[str, Any], field: str, label: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise EvaluationError(f"{label}.{field} must be a non-empty string")
    return value.strip()


def load_evaluation_cases(path: Path) -> list[dict[str, Any]]:
    """Load and validate the small, dependency-free evaluation contract."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"evaluation cases are not readable JSON: {path}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != "0.1.0":
        raise EvaluationError("evaluation cases require schema_version 0.1.0")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise EvaluationError("evaluation cases must contain a non-empty cases list")

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            raise EvaluationError(f"{label} must be an object")
        case_id = _required_string(case, "id", label)
        if case_id in seen:
            raise EvaluationError(f"duplicate evaluation case id: {case_id}")
        seen.add(case_id)
        stage = _required_string(case, "stage", label)
        operation = _required_string(case, "operation", label)
        if stage not in ALLOWED_STAGES:
            raise EvaluationError(f"{label}.stage must be one of {sorted(ALLOWED_STAGES)}")
        if operation not in ALLOWED_OPERATIONS:
            raise EvaluationError(
                f"{label}.operation must be one of {sorted(ALLOWED_OPERATIONS)}"
            )
        if operation not in STAGE_OPERATIONS[stage]:
            raise EvaluationError(
                f"{label}.operation {operation!r} is not valid for stage {stage!r}"
            )
        expected = case.get("expected")
        if not isinstance(expected, dict) or not expected:
            raise EvaluationError(f"{label}.expected must be a non-empty object")
        normalized.append(
            {"id": case_id, "stage": stage, "operation": operation, "expected": expected}
        )
    return normalized


def _rewrite_csv(
    path: Path, mutate: Callable[[list[dict[str, str]]], None]
) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)
    mutate(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _apply_mutation(raw_dir: Path, operation: str) -> None:
    if operation == "baseline":
        return
    if operation == "ledger_mismatch":
        _rewrite_csv(
            raw_dir / "actuals.csv",
            lambda rows: rows[0].update(amount=str(Decimal(rows[0]["amount"]) - 1)),
        )
        return
    if operation == "unmapped_account":
        _rewrite_csv(raw_dir / "account_mapping.csv", lambda rows: rows.pop())
        return
    if operation == "customer_revenue_mismatch":
        _rewrite_csv(
            raw_dir / "customers.csv",
            lambda rows: rows[0].update(
                actual_revenue=str(Decimal(rows[0]["actual_revenue"]) + 1)
            ),
        )
        return
    if operation == "headcount_payroll_mismatch":
        _rewrite_csv(
            raw_dir / "headcount.csv",
            lambda rows: rows[0].update(
                actual_cost=str(Decimal(rows[0]["actual_cost"]) + 1)
            ),
        )
        return
    if operation not in {"step_limit", "agent_self_approval"}:
        raise EvaluationError(f"mutation is not implemented: {operation}")


def _observed_validation(
    raw_dir: Path, verified_dir: Path, schema_path: Path
) -> dict[str, Any]:
    try:
        result = validate_finance_pack(raw_dir, verified_dir, schema_path)
    except ValidationError as exc:
        return {"outcome": "REJECTED", "error": str(exc)}
    return {
        "outcome": "ACCEPTED",
        "row_count": sum(result.row_counts.values()),
        "dataset_count": len(result.row_counts),
    }


def _observed_investigation(
    raw_dir: Path,
    verified_dir: Path,
    schema_path: Path,
    operation: str,
) -> dict[str, Any]:
    validate_finance_pack(raw_dir, verified_dir, schema_path)
    engine = FinanceEngine(FinanceData(verified_dir))
    max_steps = 1 if operation == "step_limit" else 20
    agent = InvestigationAgent(engine, max_steps=max_steps)
    try:
        investigation = agent.run(
            "Why did actual EBITDA differ from budget?", Decimal("10000.00")
        )
    except RuntimeError as exc:
        return {"outcome": "REJECTED", "error": str(exc)}
    ebitda = engine.ebitda_variance()
    return {
        "outcome": investigation["status"],
        "ebitda_variance": str(ebitda.variance),
        "tool_sequence": [step["tool"] for step in investigation["trace"]],
        "step_count": investigation["agent"]["steps"],
        "evidence_count": len(investigation["evidence"]),
        "human_gate": investigation["human_gate"]["status"],
    }


def _observed_review(run_log_path: Path, temporary_dir: Path) -> dict[str, Any]:
    run_log = json.loads(run_log_path.read_text(encoding="utf-8"))
    evidence = run_log["investigation"]["evidence"]
    decision = {
        "run_id": run_log["run_id"],
        "reviewer": {"name": "monthly-performance-investigator", "role": "agent"},
        "reviewed_at": "2026-08-07T17:00:00-04:00",
        "decision": "APPROVE",
        "materiality": {
            "decision": "APPROVE_DEMO",
            "amount": "10000.00",
            "reasoning": "Automated attempt used only to test the boundary.",
        },
        "causal_explanations": [
            {
                "finding_statement": "Synthetic boundary test",
                "explanation": "This must not be accepted as human judgment.",
                "evidence": evidence[:1],
            }
        ],
        "tested": ["agent self-approval control"],
        "did_not_test": [],
        "distribution_scope": "None; adversarial evaluation only.",
    }
    decision_path = temporary_dir / "agent-decision.json"
    decision_path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    try:
        validate_review_decision(run_log_path, decision_path)
    except ReviewError as exc:
        return {"outcome": "REJECTED", "error": str(exc)}
    return {"outcome": "ACCEPTED"}


def _matches(expected: dict[str, Any], observed: dict[str, Any]) -> tuple[bool, list[str]]:
    differences: list[str] = []
    for field, expected_value in expected.items():
        if field == "error_contains":
            if str(expected_value) not in str(observed.get("error", "")):
                differences.append(
                    f"error did not contain {expected_value!r}: {observed.get('error', '')!r}"
                )
        elif observed.get(field) != expected_value:
            differences.append(
                f"{field}: expected {expected_value!r}, observed {observed.get(field)!r}"
            )
    return not differences, differences


def run_evaluation(
    cases_path: Path,
    raw_dir: Path,
    schema_path: Path,
    run_log_path: Path,
    run_id: str,
) -> dict[str, Any]:
    """Run all explicit cases and return a machine-readable scorecard."""

    cases = load_evaluation_cases(cases_path)
    results: list[dict[str, Any]] = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix="mycroft-finance-eval-") as temporary:
            temporary_dir = Path(temporary)
            case_raw = temporary_dir / "raw"
            verified = temporary_dir / "verified"
            shutil.copytree(raw_dir, case_raw)
            _apply_mutation(case_raw, case["operation"])
            if case["stage"] == "validation":
                observed = _observed_validation(case_raw, verified, schema_path)
            elif case["stage"] == "investigation":
                observed = _observed_investigation(
                    case_raw, verified, schema_path, case["operation"]
                )
            else:
                observed = _observed_review(run_log_path, temporary_dir)
            matched, differences = _matches(case["expected"], observed)
            results.append(
                {
                    "id": case["id"],
                    "stage": case["stage"],
                    "operation": case["operation"],
                    "status": "MATCHED_EXPECTATION" if matched else "UNEXPECTED_RESULT",
                    "expected": case["expected"],
                    "observed": observed,
                    "differences": differences,
                }
            )

    matched_count = sum(item["status"] == "MATCHED_EXPECTATION" for item in results)
    return {
        "schema_version": "0.1.0",
        "workflow": "mycroft-finance-investigator-evaluation",
        "run_id": run_id,
        "classification": "SYNTHETIC_ADVERSARIAL_EVALUATION",
        "source_cases": _portable_path(cases_path),
        "source_cases_sha256": _sha256(cases_path),
        "source_data_sha256": {
            path.name: _sha256(path)
            for path in sorted(raw_dir.iterdir())
            if path.is_file()
        },
        "summary": {
            "case_count": len(results),
            "matched_count": matched_count,
            "unexpected_count": len(results) - matched_count,
            "status": "PASS" if matched_count == len(results) else "FAIL",
        },
        "cases": results,
        "adequacy": "PENDING_HUMAN_REVIEW",
    }


def write_evaluation_artifacts(
    payload: dict[str, Any], log_path: Path, report_path: Path
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Finance Investigator Evaluation Scorecard",
        "",
        f"- Run: `{payload['run_id']}`",
        f"- Classification: `{payload['classification']}`",
        f"- Result: `{payload['summary']['status']}`",
        (
            f"- Matched expectations: {payload['summary']['matched_count']} / "
            f"{payload['summary']['case_count']}"
        ),
        "- Human adequacy: `PENDING_HUMAN_REVIEW`",
        "",
        (
            "These are deterministic synthetic control checks, not a "
            "model-confidence score or production certification."
        ),
        "",
        "| Case | Stage | Expected | Observed | Result |",
        "|---|---|---|---|---|",
    ]
    for case in payload["cases"]:
        lines.append(
            f"| `{case['id']}` | {case['stage']} | "
            f"`{case['expected'].get('outcome', '')}` | "
            f"`{case['observed'].get('outcome', '')}` | `{case['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            (
                "A passing scorecard proves only that these named cases behaved as "
                "specified. A named human still decides whether the case set is "
                "adequate for its intended use."
            ),
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")

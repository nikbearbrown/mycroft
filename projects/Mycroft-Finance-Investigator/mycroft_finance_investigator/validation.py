"""Raw-to-verified validation for the sample monthly finance pack."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class ValidationError(RuntimeError):
    """Raised when an input violates the finance data contract."""


@dataclass
class ValidationResult:
    source_directory: str
    verified_directory: str
    source_hashes: dict[str, str] = field(default_factory=dict)
    row_counts: dict[str, int] = field(default_factory=dict)
    checks: list[dict[str, str]] = field(default_factory=list)

    def add_check(self, name: str, observed: str) -> None:
        self.checks.append({"name": name, "observed": observed})

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "CONFORMANT_SAMPLE",
            "source_directory": self.source_directory,
            "verified_directory": self.verified_directory,
            "source_hashes": self.source_hashes,
            "row_counts": self.row_counts,
            "checks": self.checks,
            "adequacy": "PENDING_HUMAN_REVIEW",
        }


def _decimal(value: str, field_name: str, file_name: str, row_number: int) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValidationError(
            f"{file_name} row {row_number}: {field_name} is not a decimal"
        ) from exc
    if not parsed.is_finite():
        raise ValidationError(
            f"{file_name} row {row_number}: {field_name} must be finite"
        )
    if parsed < 0:
        raise ValidationError(
            f"{file_name} row {row_number}: {field_name} must be non-negative"
        )
    return parsed


def _read_csv(
    path: Path, spec: dict[str, Any]
) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise ValidationError(f"required source file is missing: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        required = spec["required_columns"]
        if columns != required:
            raise ValidationError(
                f"{path.name}: expected columns {required}, received {columns}"
            )
        rows = []
        for row_number, row in enumerate(reader, start=2):
            normalized = {key: (value or "").strip() for key, value in row.items()}
            missing = [key for key in required if not normalized[key]]
            if missing:
                raise ValidationError(
                    f"{path.name} row {row_number}: blank fields {missing}"
                )
            for field_name in spec.get("decimal_columns", []):
                _decimal(normalized[field_name], field_name, path.name, row_number)
            for field_name, allowed in spec.get("allowed_values", {}).items():
                if normalized[field_name] not in allowed:
                    raise ValidationError(
                        f"{path.name} row {row_number}: {field_name} must be one of {allowed}"
                    )
            rows.append(normalized)
    if not rows:
        raise ValidationError(f"{path.name}: dataset must contain at least one row")
    unique_key = spec.get("unique_key", [])
    seen: set[tuple[str, ...]] = set()
    for row_number, row in enumerate(rows, start=2):
        key = tuple(row[field_name] for field_name in unique_key)
        if key in seen:
            raise ValidationError(
                f"{path.name} row {row_number}: duplicate key {key}"
            )
        seen.add(key)
    return columns, rows


def _sum_by(rows: list[dict[str, str]], key: str, amount: str) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for row in rows:
        totals[row[key]] = totals.get(row[key], Decimal("0")) + Decimal(row[amount])
    return totals


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_verified_csv(
    path: Path, columns: list[str], rows: list[dict[str, str]]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_audit(path: Path, result: ValidationResult) -> None:
    lines = [
        "# Finance Pack Validation Audit",
        "",
        "This audit reports deterministic observations. Human adequacy review is still required.",
        "",
        "## Row Counts",
        "",
        "| Dataset | Rows | SHA-256 |",
        "|---|---:|---|",
    ]
    for name, count in sorted(result.row_counts.items()):
        lines.append(f"| `{name}` | {count} | `{result.source_hashes[name]}` |")
    lines.extend(
        [
            "",
            "## Reconciliation Observations",
            "",
            "| Check | Observed |",
            "|---|---|",
        ]
    )
    for check in result.checks:
        lines.append(f"| {check['name']} | {check['observed']} |")
    lines.extend(
        [
            "",
            "## Adequacy",
            "",
            "`PENDING_HUMAN_REVIEW` — the sample is structurally conformant; this audit does not approve materiality, causation, or distribution.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def validate_finance_pack(
    raw_dir: Path, verified_dir: Path, schema_path: Path
) -> ValidationResult:
    """Validate, reconcile, and normalize a raw finance pack."""

    if not raw_dir.is_dir():
        raise ValidationError(f"raw source directory does not exist: {raw_dir}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    datasets: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    result = ValidationResult(str(raw_dir), str(verified_dir))

    provenance_path = raw_dir / "provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    required_provenance = {"classification", "origin", "created_on", "permitted_use"}
    missing_provenance = sorted(required_provenance - provenance.keys())
    if missing_provenance:
        raise ValidationError(f"provenance.json missing fields: {missing_provenance}")
    if provenance["classification"] != "synthetic_sample":
        raise ValidationError("only explicitly classified synthetic samples are accepted")

    for file_name, spec in schema["datasets"].items():
        source_path = raw_dir / file_name
        columns, rows = _read_csv(source_path, spec)
        datasets[file_name] = (columns, rows)
        result.source_hashes[file_name] = _sha256(source_path)
        result.row_counts[file_name] = len(rows)

    mappings = {
        row["account"]: row["category"]
        for row in datasets["account_mapping.csv"][1]
    }
    for file_name in ("budget.csv", "actuals.csv", "ledger.csv"):
        unknown = sorted(
            {row["account"] for row in datasets[file_name][1]} - mappings.keys()
        )
        if unknown:
            raise ValidationError(f"{file_name}: unmapped accounts {unknown}")
    result.add_check("Account mapping coverage", "All budget, actual, and ledger accounts mapped")

    periods = {
        row["period"]
        for file_name in ("budget.csv", "actuals.csv", "ledger.csv")
        for row in datasets[file_name][1]
    }
    entities = {
        row["entity"]
        for file_name in ("budget.csv", "actuals.csv", "ledger.csv")
        for row in datasets[file_name][1]
    }
    if len(periods) != 1 or len(entities) != 1:
        raise ValidationError(
            f"finance pack must contain one period and entity; periods={periods}, entities={entities}"
        )
    result.add_check("Scope", f"One period ({next(iter(periods))}) and one entity ({next(iter(entities))})")

    actual_by_account = _sum_by(datasets["actuals.csv"][1], "account", "amount")
    ledger_by_account = _sum_by(datasets["ledger.csv"][1], "account", "amount")
    if actual_by_account != ledger_by_account:
        raise ValidationError(
            f"actuals do not reconcile to ledger: actuals={actual_by_account}, ledger={ledger_by_account}"
        )
    result.add_check(
        "Actuals-to-ledger control total",
        f"Reconciled at {sum(actual_by_account.values(), Decimal('0'))}",
    )

    budget_by_category: dict[str, Decimal] = {}
    actual_by_category: dict[str, Decimal] = {}
    for row in datasets["budget.csv"][1]:
        category = mappings[row["account"]]
        budget_by_category[category] = budget_by_category.get(category, Decimal("0")) + Decimal(row["amount"])
    for row in datasets["actuals.csv"][1]:
        category = mappings[row["account"]]
        actual_by_category[category] = actual_by_category.get(category, Decimal("0")) + Decimal(row["amount"])

    customer_budget = sum(
        (Decimal(row["budget_revenue"]) for row in datasets["customers.csv"][1]),
        Decimal("0"),
    )
    customer_actual = sum(
        (Decimal(row["actual_revenue"]) for row in datasets["customers.csv"][1]),
        Decimal("0"),
    )
    if (
        customer_budget != budget_by_category.get("revenue", Decimal("0"))
        or customer_actual != actual_by_category.get("revenue", Decimal("0"))
    ):
        raise ValidationError("customer revenue drivers do not reconcile to revenue totals")
    result.add_check(
        "Customer revenue drivers",
        f"Budget {customer_budget}; actual {customer_actual}; reconciled",
    )

    headcount_budget = sum(
        (Decimal(row["budget_cost"]) for row in datasets["headcount.csv"][1]),
        Decimal("0"),
    )
    headcount_actual = sum(
        (Decimal(row["actual_cost"]) for row in datasets["headcount.csv"][1]),
        Decimal("0"),
    )
    if (
        headcount_budget != budget_by_category.get("payroll", Decimal("0"))
        or headcount_actual != actual_by_category.get("payroll", Decimal("0"))
    ):
        raise ValidationError("headcount cost drivers do not reconcile to payroll totals")
    result.add_check(
        "Headcount cost drivers",
        f"Budget {headcount_budget}; actual {headcount_actual}; reconciled",
    )

    verified_dir.mkdir(parents=True, exist_ok=True)
    for file_name, (columns, rows) in datasets.items():
        _write_verified_csv(verified_dir / file_name, columns, rows)
    (verified_dir / "provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )
    (verified_dir / "validation-result.json").write_text(
        json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    _write_audit(verified_dir / "validation-audit.md", result)
    return result

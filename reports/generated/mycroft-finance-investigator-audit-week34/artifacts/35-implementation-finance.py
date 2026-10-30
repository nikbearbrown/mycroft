"""Deterministic monthly performance calculations."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable


EXPENSE_CATEGORIES = {"cogs", "payroll", "opex"}


def money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"


@dataclass(frozen=True)
class VarianceLine:
    level: str
    key: str
    label: str
    category: str
    budget: Decimal
    actual: Decimal
    variance: Decimal
    performance_impact: Decimal
    favorable: bool | None
    evidence: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        for field_name in ("budget", "actual", "variance", "performance_impact"):
            result[field_name] = money(result[field_name])
        result["evidence"] = list(self.evidence)
        return result


class FinanceData:
    """Loads only structurally verified local records."""

    REQUIRED = (
        "account_mapping.csv",
        "budget.csv",
        "actuals.csv",
        "ledger.csv",
        "customers.csv",
        "headcount.csv",
        "validation-result.json",
    )

    def __init__(self, verified_dir: Path):
        missing = [name for name in self.REQUIRED if not (verified_dir / name).is_file()]
        if missing:
            raise FileNotFoundError(
                f"verified finance pack is incomplete; missing {missing}. Run validation first."
            )
        self.verified_dir = verified_dir
        self.mapping_rows = self._read("account_mapping.csv")
        self.budget_rows = self._read("budget.csv")
        self.actual_rows = self._read("actuals.csv")
        self.ledger_rows = self._read("ledger.csv")
        self.customer_rows = self._read("customers.csv")
        self.headcount_rows = self._read("headcount.csv")
        self.mapping = {
            row["account"]: {
                "account_name": row["account_name"],
                "category": row["category"],
            }
            for row in self.mapping_rows
        }

    def _read(self, name: str) -> list[dict[str, str]]:
        with (self.verified_dir / name).open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))


def _totals(rows: Iterable[dict[str, str]]) -> dict[str, Decimal]:
    result: dict[str, Decimal] = {}
    for row in rows:
        result[row["account"]] = result.get(row["account"], Decimal("0")) + Decimal(row["amount"])
    return result


class FinanceEngine:
    """Produces a reproducible budget-versus-actual work surface."""

    def __init__(self, data: FinanceData):
        self.data = data

    def account_variances(self) -> list[VarianceLine]:
        budget = _totals(self.data.budget_rows)
        actual = _totals(self.data.actual_rows)
        lines = []
        for account in sorted(set(budget) | set(actual)):
            metadata = self.data.mapping[account]
            category = metadata["category"]
            budget_amount = budget.get(account, Decimal("0"))
            actual_amount = actual.get(account, Decimal("0"))
            variance = actual_amount - budget_amount
            impact = variance if category == "revenue" else -variance
            ledger_ids = tuple(
                f"ledger.csv:transaction_id={row['transaction_id']}"
                for row in self.data.ledger_rows
                if row["account"] == account
            )
            evidence = (
                f"budget.csv:account={account}",
                f"actuals.csv:account={account}",
                f"account_mapping.csv:account={account}",
                *ledger_ids,
            )
            lines.append(
                VarianceLine(
                    level="account",
                    key=account,
                    label=metadata["account_name"],
                    category=category,
                    budget=budget_amount,
                    actual=actual_amount,
                    variance=variance,
                    performance_impact=impact,
                    favorable=None if impact == 0 else impact > 0,
                    evidence=evidence,
                )
            )
        return lines

    def category_variances(self) -> list[VarianceLine]:
        grouped: dict[str, list[VarianceLine]] = {}
        for line in self.account_variances():
            grouped.setdefault(line.category, []).append(line)
        lines = []
        for category in ("revenue", "cogs", "payroll", "opex"):
            members = grouped.get(category, [])
            budget = sum((line.budget for line in members), Decimal("0"))
            actual = sum((line.actual for line in members), Decimal("0"))
            variance = actual - budget
            impact = variance if category == "revenue" else -variance
            evidence = tuple(
                reference
                for line in members
                for reference in line.evidence[:3]
            )
            lines.append(
                VarianceLine(
                    level="category",
                    key=category,
                    label=category.replace("_", " ").title(),
                    category=category,
                    budget=budget,
                    actual=actual,
                    variance=variance,
                    performance_impact=impact,
                    favorable=None if impact == 0 else impact > 0,
                    evidence=evidence,
                )
            )
        return lines

    def ebitda_variance(self) -> VarianceLine:
        categories = {line.category: line for line in self.category_variances()}
        budget_revenue = categories["revenue"].budget
        actual_revenue = categories["revenue"].actual
        budget_costs = sum(
            (categories[name].budget for name in EXPENSE_CATEGORIES), Decimal("0")
        )
        actual_costs = sum(
            (categories[name].actual for name in EXPENSE_CATEGORIES), Decimal("0")
        )
        budget = budget_revenue - budget_costs
        actual = actual_revenue - actual_costs
        variance = actual - budget
        evidence = tuple(
            f"{line.level}:{line.key}" for line in categories.values()
        )
        return VarianceLine(
            level="metric",
            key="ebitda",
            label="EBITDA",
            category="ebitda",
            budget=budget,
            actual=actual,
            variance=variance,
            performance_impact=variance,
            favorable=None if variance == 0 else variance > 0,
            evidence=evidence,
        )

    def material_categories(self, threshold: Decimal) -> list[VarianceLine]:
        return sorted(
            (
                line
                for line in self.category_variances()
                if abs(line.performance_impact) >= threshold
            ),
            key=lambda line: abs(line.performance_impact),
            reverse=True,
        )

    def accounts_for_category(
        self, category: str, threshold: Decimal
    ) -> list[VarianceLine]:
        return sorted(
            (
                line
                for line in self.account_variances()
                if line.category == category
                and abs(line.performance_impact) >= threshold
            ),
            key=lambda line: abs(line.performance_impact),
            reverse=True,
        )

    def driver_rows(self, category: str) -> list[dict[str, str]]:
        if category == "revenue":
            return [
                {
                    **row,
                    "variance": money(
                        Decimal(row["actual_revenue"]) - Decimal(row["budget_revenue"])
                    ),
                    "evidence": f"customers.csv:customer_id={row['customer_id']}",
                }
                for row in self.data.customer_rows
            ]
        if category == "payroll":
            return [
                {
                    **row,
                    "cost_variance": money(
                        Decimal(row["actual_cost"]) - Decimal(row["budget_cost"])
                    ),
                    "fte_variance": money(
                        Decimal(row["actual_fte"]) - Decimal(row["budget_fte"])
                    ),
                    "evidence": f"headcount.csv:department={row['department']}",
                }
                for row in self.data.headcount_rows
            ]
        return []

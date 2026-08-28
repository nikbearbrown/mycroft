from __future__ import annotations

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from mycroft_finance_investigator.finance import FinanceData, FinanceEngine
from mycroft_finance_investigator.validation import validate_finance_pack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
RAW_SAMPLE = REPO_ROOT / "data/raw/mycroft-finance-investigator"
SCHEMA = PROJECT_ROOT / "schemas/finance-pack.schema.json"


class FinanceEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        verified = Path(self.temporary.name) / "verified"
        validate_finance_pack(RAW_SAMPLE, verified, SCHEMA)
        self.engine = FinanceEngine(FinanceData(verified))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_ebitda_bridge_reconciles(self) -> None:
        ebitda = self.engine.ebitda_variance()

        self.assertEqual(ebitda.budget, Decimal("350000.00"))
        self.assertEqual(ebitda.actual, Decimal("230000.00"))
        self.assertEqual(ebitda.variance, Decimal("-120000.00"))

    def test_category_impacts_sum_to_ebitda_variance(self) -> None:
        categories = self.engine.category_variances()
        total_impact = sum(
            (line.performance_impact for line in categories), Decimal("0")
        )

        self.assertEqual(total_impact, self.engine.ebitda_variance().variance)
        by_category = {line.category: line for line in categories}
        self.assertEqual(by_category["revenue"].performance_impact, Decimal("-90000.00"))
        self.assertEqual(by_category["cogs"].performance_impact, Decimal("-35000.00"))
        self.assertEqual(by_category["payroll"].performance_impact, Decimal("20000.00"))
        self.assertEqual(by_category["opex"].performance_impact, Decimal("-15000.00"))

    def test_materiality_is_applied_to_absolute_performance_impact(self) -> None:
        material = self.engine.material_categories(Decimal("10000.00"))

        self.assertEqual(
            [line.category for line in material],
            ["revenue", "cogs", "payroll", "opex"],
        )

    def test_every_account_variance_has_source_lineage(self) -> None:
        for line in self.engine.account_variances():
            self.assertTrue(any(item.startswith("budget.csv:") for item in line.evidence))
            self.assertTrue(any(item.startswith("actuals.csv:") for item in line.evidence))
            self.assertTrue(any(item.startswith("ledger.csv:") for item in line.evidence))


if __name__ == "__main__":
    unittest.main()

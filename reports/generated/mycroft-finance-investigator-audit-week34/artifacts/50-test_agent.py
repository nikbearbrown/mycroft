from __future__ import annotations

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from mycroft_finance_investigator.agent import InvestigationAgent
from mycroft_finance_investigator.finance import FinanceData, FinanceEngine
from mycroft_finance_investigator.validation import validate_finance_pack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
RAW_SAMPLE = REPO_ROOT / "data/raw/mycroft-finance-investigator"
SCHEMA = PROJECT_ROOT / "schemas/finance-pack.schema.json"


class InvestigationAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        verified = Path(self.temporary.name) / "verified"
        validate_finance_pack(RAW_SAMPLE, verified, SCHEMA)
        engine = FinanceEngine(FinanceData(verified))
        self.agent = InvestigationAgent(engine)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_agent_selects_tools_from_material_observations(self) -> None:
        result = self.agent.run(
            "Why did actual EBITDA differ from budget?",
            Decimal("10000.00"),
        )

        tools = [step["tool"] for step in result["trace"]]
        self.assertEqual(tools[0], "scan_material_variances")
        self.assertEqual(tools.count("analyze_category"), 4)
        self.assertEqual(tools.count("inspect_driver_records"), 2)
        self.assertEqual(result["agent"]["steps"], 7)

    def test_agent_keeps_causal_explanation_open(self) -> None:
        result = self.agent.run(
            "Why did actual EBITDA differ from budget?",
            Decimal("10000.00"),
        )

        self.assertIsNone(result["current_explanation"])
        self.assertEqual(result["human_gate"]["status"], "OPEN")
        self.assertEqual(result["status"], "COMPLETED_PENDING_HUMAN_REVIEW")

    def test_agent_reports_a_complete_reconciled_category_bridge(self) -> None:
        result = self.agent.run(
            "Why did actual EBITDA differ from budget?",
            Decimal("10000.00"),
        )
        bridge_impacts = [
            Decimal(finding["performance_impact"])
            for finding in result["findings"][1:5]
        ]

        self.assertEqual(sum(bridge_impacts), Decimal("-120000.00"))

    def test_all_findings_retain_evidence(self) -> None:
        result = self.agent.run(
            "Why did actual EBITDA differ from budget?",
            Decimal("10000.00"),
        )

        self.assertGreater(len(result["findings"]), 0)
        for finding in result["findings"]:
            self.assertGreater(len(finding["evidence"]), 0)

    def test_step_limit_is_a_hard_stop(self) -> None:
        limited = InvestigationAgent(self.agent.engine, max_steps=1)

        with self.assertRaisesRegex(RuntimeError, "exceeded"):
            limited.run(
                "Why did actual EBITDA differ from budget?",
                Decimal("10000.00"),
            )


if __name__ == "__main__":
    unittest.main()

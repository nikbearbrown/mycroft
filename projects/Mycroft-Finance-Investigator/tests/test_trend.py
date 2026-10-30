from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.trend import (
    TrendError,
    load_trend_plan,
    run_trend,
    write_trend_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
PLAN = PROJECT_ROOT / "config/sample-trend.json"


class TrendTests(unittest.TestCase):
    def test_sample_has_exact_ebitda_history_and_movements(self) -> None:
        result = run_trend(PLAN, "exact-results")
        periods = result["periods"]

        self.assertEqual(
            [period["actual_ebitda"] for period in periods],
            ["261000.00", "230000.00", "265000.00"],
        )
        self.assertEqual(
            [period["actual_change_from_previous"] for period in periods],
            [None, "-31000.00", "35000.00"],
        )
        self.assertEqual(
            [period["movement"] for period in periods],
            ["FIRST_PERIOD", "DETERIORATED", "IMPROVED"],
        )

    def test_recurring_adverse_categories_are_deterministic(self) -> None:
        result = run_trend(PLAN, "recurrence")

        self.assertEqual(
            result["verified_findings"][
                "recurring_material_adverse_categories"
            ],
            ["revenue", "cogs", "opex"],
        )
        trends = {item["category"]: item for item in result["category_trends"]}
        self.assertFalse(trends["payroll"]["recurring_material_adverse"])
        self.assertEqual(trends["payroll"]["material_favorable_count"], 2)

    def test_output_preserves_human_judgment_boundary(self) -> None:
        result = run_trend(PLAN, "boundary")

        self.assertEqual(
            result["classification"], "HISTORICAL_COMPARISON_NOT_FORECAST"
        )
        self.assertIsNone(result["causal_explanation"])
        self.assertIsNone(result["forecast"])
        self.assertIsNone(result["recommendation"])
        self.assertEqual(result["human_gate"]["status"], "OPEN")

    def test_duplicate_period_is_rejected(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["periods"].append(payload["periods"][0])
        with tempfile.TemporaryDirectory() as temporary:
            plan_path = Path(temporary) / "duplicate.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(TrendError, "duplicate period"):
                load_trend_plan(plan_path)

    def test_verified_source_tampering_is_rejected(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            verified_copy = temporary_path / "verified"
            shutil.copytree(
                REPO_ROOT
                / "data/verified/mycroft-finance-investigator-history/2026-01",
                verified_copy,
            )
            with (verified_copy / "actuals.csv").open("a", encoding="utf-8") as handle:
                handle.write("tampered\n")
            payload["periods"][0]["verified_dir"] = str(verified_copy)
            plan_path = temporary_path / "tampered.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(TrendError, "hash does not match"):
                run_trend(plan_path, "tampered")

    def test_entity_mismatch_is_rejected(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["entity"] = "Another Entity"
        with tempfile.TemporaryDirectory() as temporary:
            plan_path = Path(temporary) / "entity.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(TrendError, "does not match plan"):
                run_trend(plan_path, "entity")

    def test_period_mismatch_is_rejected(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["periods"][0]["period"] = "2025-12"
        with tempfile.TemporaryDirectory() as temporary:
            plan_path = Path(temporary) / "period.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(TrendError, "run period"):
                run_trend(plan_path, "period")

    def test_human_report_states_the_comparison_boundary(self) -> None:
        result = run_trend(PLAN, "report")
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "trend.json"
            report_path = Path(temporary) / "trend.md"
            write_trend_artifacts(result, log_path, report_path)
            report = report_path.read_text(encoding="utf-8")

        self.assertIn("HISTORICAL_COMPARISON_NOT_FORECAST", report)
        self.assertIn("Recurrence does not establish why", report)
        self.assertIn("Human gate: `OPEN`", report)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.scenario import (
    ScenarioError,
    load_scenario_plan,
    run_scenarios,
    write_scenario_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
VERIFIED = REPO_ROOT / "data/verified/mycroft-finance-investigator"
RUN_LOG = REPO_ROOT / "logs/mycroft-finance-investigator-sample-2026-02.json"
PLAN = PROJECT_ROOT / "config/sample-scenarios.json"


class ScenarioTests(unittest.TestCase):
    def test_sample_scenarios_have_exact_reproducible_results(self) -> None:
        result = run_scenarios(PLAN, VERIFIED, RUN_LOG, "week33")
        by_id = {scenario["id"]: scenario for scenario in result["scenarios"]}

        self.assertEqual(result["baseline_ebitda"], "230000.00")
        self.assertEqual(by_id["revenue-recovery-5pct"]["scenario_ebitda"], "275500.00")
        self.assertEqual(by_id["cogs-reduction-20000"]["scenario_ebitda"], "250000.00")
        self.assertEqual(by_id["balanced-operating-exercise"]["scenario_ebitda"], "252300.00")

    def test_outputs_are_not_forecasts_or_recommendations(self) -> None:
        result = run_scenarios(PLAN, VERIFIED, RUN_LOG, "boundary")

        self.assertEqual(result["classification"], "SIMULATION_NOT_FORECAST")
        self.assertIsNone(result["recommendation"])
        self.assertEqual(result["decision"], "HUMAN_REQUIRED")
        self.assertTrue(
            all(scenario["recommendation"] is None for scenario in result["scenarios"])
        )

    def test_every_assumption_retains_baseline_and_plan_evidence(self) -> None:
        result = run_scenarios(PLAN, VERIFIED, RUN_LOG, "lineage")

        for scenario in result["scenarios"]:
            for assumption in scenario["assumptions"]:
                self.assertGreaterEqual(len(assumption["evidence"]), 2)
                self.assertIn("scenario_id=", assumption["evidence"][-1])

    def test_duplicate_category_in_one_scenario_is_rejected(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["scenarios"][0]["assumptions"].append(
            payload["scenarios"][0]["assumptions"][0]
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ScenarioError, "more than one assumption"):
                load_scenario_plan(path)

    def test_scenario_cannot_make_a_category_negative(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["scenarios"] = [payload["scenarios"][0]]
        assumption = payload["scenarios"][0]["assumptions"][0]
        assumption["method"] = "AMOUNT"
        assumption["value"] = "-1000000.00"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "negative.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ScenarioError, "makes revenue negative"):
                run_scenarios(path, VERIFIED, RUN_LOG, "negative")

    def test_plan_must_bind_to_exact_baseline_run(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["baseline_run_id"] = "another-run"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "wrong-run.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ScenarioError, "does not match"):
                run_scenarios(path, VERIFIED, RUN_LOG, "wrong-run")

    def test_unknown_plan_fields_are_rejected(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["prediction"] = "not allowed"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "unknown.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ScenarioError, "unknown fields"):
                load_scenario_plan(path)

    def test_human_report_preserves_decision_boundary(self) -> None:
        result = run_scenarios(PLAN, VERIFIED, RUN_LOG, "report")
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "scenarios.json"
            report_path = Path(temporary) / "scenarios.md"
            write_scenario_artifacts(result, log_path, report_path)
            report = report_path.read_text(encoding="utf-8")

        self.assertIn("SIMULATION_NOT_FORECAST", report)
        self.assertIn("Recommendation: `NONE`", report)
        self.assertIn("Human Decision Required", report)


if __name__ == "__main__":
    unittest.main()

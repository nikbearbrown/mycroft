from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.orchestration import (
    RoutingError,
    load_routing_plan,
    run_orchestration,
    write_orchestration_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
PLAN = PROJECT_ROOT / "config/sample-routing.json"
TREND = REPO_ROOT / "logs/mycroft-finance-investigator-trend-week35.json"


class OrchestrationTests(unittest.TestCase):
    def test_supervisor_prioritizes_and_routes_recurring_gaps(self) -> None:
        result = run_orchestration(PLAN, TREND, "routing")

        self.assertEqual(
            [task["category"] for task in result["tasks"]],
            ["revenue", "cogs", "opex"],
        )
        self.assertEqual(
            [task["specialist"] for task in result["tasks"]],
            ["revenue-specialist", "cost-specialist", "cost-specialist"],
        )
        self.assertEqual(
            [task["cumulative_material_adverse_impact"] for task in result["tasks"]],
            ["200000.00", "100000.00", "36000.00"],
        )

    def test_lineage_check_precedes_category_delegations(self) -> None:
        result = run_orchestration(PLAN, TREND, "lineage")

        self.assertEqual(result["handoffs"][0]["to"], "lineage-specialist")
        self.assertEqual(
            result["handoffs"][0]["result"]["status"], "VERIFIED_INPUT_CHAIN"
        )
        self.assertEqual(result["supervisor"]["delegations_used"], 4)

    def test_specialists_preserve_evidence_gaps(self) -> None:
        result = run_orchestration(PLAN, TREND, "gaps")
        by_category = {task["category"]: task for task in result["tasks"]}

        self.assertIn(
            "CORRELATED_DRIVER_RECORD",
            by_category["revenue"]["result"]["evidence_kinds"],
        )
        self.assertIn(
            "OPERATIONAL_DRIVER_RECORDS",
            by_category["cogs"]["result"]["missing_evidence"],
        )
        for task in result["tasks"]:
            self.assertIsNone(task["result"]["causal_explanation"])
            self.assertIsNone(task["result"]["recommendation"])
            self.assertTrue(task["result"]["evidence"])
            self.assertEqual(len(task["result_sha256"]), 64)

    def test_delegation_limit_is_a_hard_stop(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["max_delegations"] = 3
        with tempfile.TemporaryDirectory() as temporary:
            plan_path = Path(temporary) / "limited.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(RoutingError, "limit is 3"):
                run_orchestration(plan_path, TREND, "limited")

    def test_specialist_scope_cannot_be_reassigned(self) -> None:
        payload = json.loads(PLAN.read_text(encoding="utf-8"))
        payload["routes"]["revenue"] = "cost-specialist"
        with tempfile.TemporaryDirectory() as temporary:
            plan_path = Path(temporary) / "route.json"
            plan_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(RoutingError, "specialist scope"):
                load_routing_plan(plan_path)

    def test_source_run_tampering_is_rejected(self) -> None:
        trend = json.loads(TREND.read_text(encoding="utf-8"))
        source = REPO_ROOT / trend["periods"][0]["run_log"]
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            source_copy = temporary_path / "source.json"
            source_copy.write_text(source.read_text(encoding="utf-8") + " ", encoding="utf-8")
            trend["periods"][0]["run_log"] = str(source_copy)
            trend_path = temporary_path / "trend.json"
            trend_path.write_text(json.dumps(trend), encoding="utf-8")

            with self.assertRaisesRegex(RoutingError, "source run hash mismatch"):
                run_orchestration(PLAN, trend_path, "tampered")

    def test_recomputed_category_mismatch_is_rejected(self) -> None:
        trend = json.loads(TREND.read_text(encoding="utf-8"))
        trend["category_trends"][0]["periods"][0]["performance_impact"] = "-1.00"
        with tempfile.TemporaryDirectory() as temporary:
            trend_path = Path(temporary) / "trend.json"
            trend_path.write_text(json.dumps(trend), encoding="utf-8")

            with self.assertRaisesRegex(RoutingError, "recomputed category mismatch"):
                run_orchestration(PLAN, trend_path, "mismatch")

    def test_report_exposes_handoffs_and_human_boundary(self) -> None:
        result = run_orchestration(PLAN, TREND, "report")
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "routing.json"
            report_path = Path(temporary) / "routing.md"
            write_orchestration_artifacts(result, log_path, report_path)
            report = report_path.read_text(encoding="utf-8")

        self.assertIn("Prioritized Work Queue", report)
        self.assertIn("Handoff Trace", report)
        self.assertIn("Recommendation: `NONE`", report)
        self.assertIn("Human gate: `OPEN`", report)


if __name__ == "__main__":
    unittest.main()

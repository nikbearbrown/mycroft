from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.coverage import (
    CoverageError,
    check,
    parse_reference,
    resolve,
)


class CoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.verified = self.root / "verified"
        self.verified.mkdir()
        (self.verified / "budget.csv").write_text(
            "period,entity,account,amount\n"
            "2026-02,Sample,4000,800000.00\n"
            "2026-02,Sample,5000,300000.00\n",
            encoding="utf-8",
        )
        self.run_log = self.root / "run.json"
        self._write_run(["budget.csv:account=4000"])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_run(self, evidence: list[str]) -> None:
        self.run_log.write_text(json.dumps({
            "workflow": "mycroft-finance-investigator",
            "investigation": {"trace": [{"observation": {"category_bridge": [
                {"key": "revenue", "variance": "-90000.00", "evidence": evidence}
            ]}}]},
        }), encoding="utf-8")

    # --- reference parsing ------------------------------------------------

    def test_parse_splits_file_column_value(self) -> None:
        self.assertEqual(parse_reference("budget.csv:account=4000"),
                         ("budget.csv", "account", "4000"))

    def test_malformed_reference_raises(self) -> None:
        for bad in ("budget.csv", "budget.csv:account", "account=4000", ":="):
            with self.subTest(reference=bad):
                with self.assertRaises(CoverageError):
                    parse_reference(bad)

    # --- the three failures -----------------------------------------------

    def test_resolved_reference_returns_none(self) -> None:
        self.assertIsNone(resolve("budget.csv:account=4000", self.verified, {}))

    def test_dangling_when_the_file_is_absent(self) -> None:
        self.assertEqual(resolve("ledger.csv:account=4000", self.verified, {}),
                         "DANGLING")

    def test_unresolved_when_the_row_is_absent(self) -> None:
        # The file exists and the column exists; the value does not.
        self.assertEqual(resolve("budget.csv:account=9999", self.verified, {}),
                         "UNRESOLVED")

    def test_unresolved_when_the_column_is_absent(self) -> None:
        self.assertEqual(resolve("budget.csv:nonsense=4000", self.verified, {}),
                         "UNRESOLVED")

    def test_uncited_finding_is_its_own_failure(self) -> None:
        self._write_run([])
        report = check(self.run_log, self.verified)
        self.assertEqual(report["problems"][0]["failure"], "UNCITED")
        self.assertFalse(report["fully_resolved"])

    # --- the report -------------------------------------------------------

    def test_clean_run_is_fully_resolved(self) -> None:
        report = check(self.run_log, self.verified)
        self.assertTrue(report["fully_resolved"])
        self.assertEqual(report["references_resolved"], 1)
        self.assertEqual(report["problems"], [])

    def test_failures_are_reported_per_reference_not_collapsed(self) -> None:
        self._write_run([
            "budget.csv:account=4000",   # resolves
            "ledger.csv:account=4000",   # DANGLING
            "budget.csv:account=9999",   # UNRESOLVED
        ])
        report = check(self.run_log, self.verified)
        self.assertEqual(report["references_checked"], 3)
        self.assertEqual(report["references_resolved"], 1)
        self.assertEqual({p["failure"] for p in report["problems"]},
                         {"DANGLING", "UNRESOLVED"})

    def test_run_with_no_findings_is_refused(self) -> None:
        self.run_log.write_text(json.dumps({
            "workflow": "mycroft-finance-investigator",
            "investigation": {"trace": [{"observation": {}}]},
        }), encoding="utf-8")
        with self.assertRaises(CoverageError):
            check(self.run_log, self.verified)

    def test_foreign_workflow_is_refused(self) -> None:
        self.run_log.write_text(json.dumps({"workflow": "something-else"}),
                                encoding="utf-8")
        with self.assertRaises(CoverageError):
            check(self.run_log, self.verified)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.disagreement import (
    DisagreementError,
    append_disagreement,
    engine_findings,
    validate_disagreement,
)


def _run_log(path: Path) -> None:
    path.write_text(json.dumps({
        "workflow": "mycroft-finance-investigator",
        "run_id": "sample",
        "investigation": {
            "trace": [{
                "observation": {
                    "category_bridge": [
                        {"key": "revenue", "variance": "-90000.00", "favorable": False},
                        {"key": "payroll", "variance": "20000.00", "favorable": True},
                    ]
                }
            }]
        },
    }), encoding="utf-8")


class DisagreementLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_log = self.root / "run.json"
        _run_log(self.run_log)
        self.record = self.root / "record.json"
        self.log = self.root / "log.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _record(self, **overrides: object) -> Path:
        payload = {
            "workflow": "mycroft-finance-investigator",
            "artifact": "reviewer-disagreement",
            "claim": "revenue",
            "position": "NOT_MATERIAL",
            "reviewer": "Dana Whitfield, Controller",
            "recorded_at": "2026-10-02T09:30:00Z",
            "basis": "The contract slipped one week and settled in March; the shortfall reverses next period.",
        }
        payload.update(overrides)
        self.record.write_text(json.dumps(payload), encoding="utf-8")
        return self.record

    # --- what may be disagreed with --------------------------------------

    def test_findings_are_keyed_by_category(self) -> None:
        self.assertEqual(set(engine_findings(self.run_log)), {"revenue", "payroll"})

    def test_claim_must_be_something_the_engine_said(self) -> None:
        with self.assertRaises(DisagreementError) as caught:
            validate_disagreement(self._record(claim="marketing"), self.run_log)
        self.assertIn("the engine said nothing about it", str(caught.exception))

    # --- acceptance -------------------------------------------------------

    def test_valid_disagreement_keeps_both_sides(self) -> None:
        accepted = validate_disagreement(self._record(), self.run_log)
        self.assertEqual(accepted["position"], "NOT_MATERIAL")
        # the engine's number is copied from the run, not from the record
        self.assertEqual(accepted["engine_finding"]["variance"], "-90000.00")

    # --- the refusals -----------------------------------------------------

    def test_agent_may_not_record_a_disagreement(self) -> None:
        with self.assertRaises(DisagreementError):
            validate_disagreement(self._record(reviewer="agent"), self.run_log)

    def test_reviewer_may_not_restate_the_engine_value(self) -> None:
        with self.assertRaises(DisagreementError) as caught:
            validate_disagreement(self._record(engine_value="-1.00"), self.run_log)
        self.assertIn("must not restate engine_value", str(caught.exception))

    def test_placeholder_basis_is_refused(self) -> None:
        with self.assertRaises(DisagreementError):
            validate_disagreement(self._record(basis="nope"), self.run_log)

    def test_unknown_position_is_refused(self) -> None:
        with self.assertRaises(DisagreementError):
            validate_disagreement(self._record(position="DISLIKE"), self.run_log)

    def test_naive_timestamp_is_refused(self) -> None:
        with self.assertRaises(DisagreementError):
            validate_disagreement(self._record(recorded_at="2026-10-02T09:30:00"),
                                  self.run_log)

    # --- the log appends --------------------------------------------------

    def test_first_entry_opens_the_log(self) -> None:
        log = append_disagreement(self._record(), self.run_log, self.log)
        self.assertEqual(len(log["entries"]), 1)
        self.assertEqual(len(log["run_log_sha256"]), 64)

    def test_two_reviewers_may_both_disagree_with_one_finding(self) -> None:
        append_disagreement(self._record(), self.run_log, self.log)
        log = append_disagreement(
            self._record(reviewer="Priya Raman, FP&A",
                         basis="Agree it is immaterial, but for a different reason entirely."),
            self.run_log, self.log,
        )
        self.assertEqual(len(log["entries"]), 2)

    def test_same_reviewer_cannot_restate_a_position(self) -> None:
        append_disagreement(self._record(), self.run_log, self.log)
        with self.assertRaises(DisagreementError):
            append_disagreement(self._record(), self.run_log, self.log)

    def test_log_detaches_if_the_run_changes(self) -> None:
        append_disagreement(self._record(), self.run_log, self.log)
        self.run_log.write_text(
            self.run_log.read_text(encoding="utf-8").replace("-90000.00", "-91000.00"),
            encoding="utf-8",
        )
        with self.assertRaises(DisagreementError) as caught:
            append_disagreement(
                self._record(reviewer="Priya Raman, FP&A",
                             basis="A different reviewer with a separate reasoned position."),
                self.run_log, self.log,
            )
        self.assertIn("run log changed", str(caught.exception))

    def test_engine_numbers_are_never_rewritten(self) -> None:
        before = self.run_log.read_text(encoding="utf-8")
        append_disagreement(self._record(), self.run_log, self.log)
        self.assertEqual(self.run_log.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.distribution import evaluate


class DistributionGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.paths = {
            "materiality": self._write("mat.json", {
                "materiality_status": "APPROVED",
                "approved_amount": "10000.00",
                "approved_by": "Dana Whitfield, Controller"}),
            "freshness": self._write("fresh.json", {
                "verdict": "FRESH", "lag_days": 10, "age_days": 10}),
            "coverage": self._write("cov.json", {
                "fully_resolved": True,
                "references_resolved": 21, "references_checked": 21}),
            "review": self._write("rev.json", {
                "decision": "APPROVE", "reviewer": "Dana Whitfield, Controller"}),
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write(self, name: str, payload: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _status_of(self, result: dict, condition: str) -> str:
        return next(c["status"] for c in result["conditions"]
                    if c["condition"] == condition)

    # --- default deny -----------------------------------------------------

    def test_nothing_supplied_blocks(self) -> None:
        result = evaluate()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(len(result["blocking"]), 4)

    def test_missing_file_blocks_rather_than_passes(self) -> None:
        result = evaluate(**{**self.paths,
                             "coverage": self.root / "absent.json"})
        self.assertEqual(self._status_of(result, "evidence_resolves"), "BLOCKED")

    # --- the happy path ---------------------------------------------------

    def test_all_conditions_met_clears(self) -> None:
        result = evaluate(**self.paths)
        self.assertEqual(result["status"], "CLEARED")
        self.assertEqual(result["blocking"], [])

    # --- each condition can block on its own ------------------------------

    def test_unapproved_materiality_blocks(self) -> None:
        self._write("mat.json", {"materiality_status": "DEMO_UNAPPROVED"})
        self.assertEqual(evaluate(**self.paths)["status"], "BLOCKED")

    def test_expired_evidence_blocks(self) -> None:
        self._write("fresh.json", {"verdict": "EXPIRED", "lag_days": 1,
                                   "age_days": 900})
        result = evaluate(**self.paths)
        self.assertEqual(self._status_of(result, "evidence_fresh"), "BLOCKED")

    def test_stale_evidence_does_not_block(self) -> None:
        # Lateness is a fact a reader can weigh; it is stated, not suppressed.
        self._write("fresh.json", {"verdict": "STALE", "lag_days": 148,
                                   "age_days": 92})
        result = evaluate(**self.paths)
        self.assertEqual(result["status"], "CLEARED")
        reason = next(c["reason"] for c in result["conditions"]
                      if c["condition"] == "evidence_fresh")
        self.assertIn("148", reason)

    def test_unresolved_evidence_blocks(self) -> None:
        self._write("cov.json", {"fully_resolved": False,
                                 "problems": [{"failure": "DANGLING"}]})
        self.assertEqual(evaluate(**self.paths)["status"], "BLOCKED")

    def test_non_approving_review_blocks(self) -> None:
        for decision in ("REQUEST_CHANGES", "BLOCK"):
            with self.subTest(decision=decision):
                self._write("rev.json", {"decision": decision})
                self.assertEqual(evaluate(**self.paths)["status"], "BLOCKED")

    # --- disagreements ----------------------------------------------------

    def test_absent_disagreement_log_clears(self) -> None:
        result = evaluate(**self.paths, disagreements=self.root / "none.json")
        self.assertEqual(self._status_of(result, "no_open_disagreements"),
                         "CLEARED")

    def test_empty_disagreement_log_clears(self) -> None:
        log = self._write("dis.json", {"entries": []})
        self.assertEqual(evaluate(**self.paths, disagreements=log)["status"],
                         "CLEARED")

    def test_open_disagreement_blocks(self) -> None:
        log = self._write("dis.json", {"entries": [
            {"claim": "revenue", "reviewer": "Dana Whitfield, Controller"}]})
        result = evaluate(**self.paths, disagreements=log)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("no_open_disagreements", result["blocking"])

    def test_malformed_disagreement_log_blocks(self) -> None:
        log = self._write("dis.json", {"entries": "not a list"})
        self.assertEqual(evaluate(**self.paths, disagreements=log)["status"],
                         "BLOCKED")

    # --- the gate reports every reason, not just the first ----------------

    def test_all_blocking_reasons_are_listed(self) -> None:
        self._write("mat.json", {"materiality_status": "DEMO_UNAPPROVED"})
        self._write("rev.json", {"decision": "BLOCK"})
        result = evaluate(**self.paths)
        self.assertIn("materiality_approved", result["blocking"])
        self.assertIn("human_approved", result["blocking"])


if __name__ == "__main__":
    unittest.main()

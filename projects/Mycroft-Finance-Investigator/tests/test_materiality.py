from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from mycroft_finance_investigator.materiality import (
    MaterialityError,
    SOURCE_FILES,
    approved_threshold,
    build_approval_request,
    record_approval,
    validate_approval,
)

DEMO = Decimal("10000.00")


class MaterialityApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.verified = self.root / "verified"
        self.verified.mkdir()
        for name in SOURCE_FILES:
            (self.verified / name).write_text(f"column\n{name}\n", encoding="utf-8")
        self.request = build_approval_request(
            self.verified, "Northstar Software Sample", "2026-02", DEMO
        )
        self.decision_path = self.root / "decision.json"
        self.output = self.root / "approval.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _decision(self, **overrides: object) -> Path:
        payload = {
            "workflow": "mycroft-finance-investigator",
            "artifact": "materiality-approval",
            "decision": "APPROVE_DEMO",
            "approved_by": "Dana Whitfield, Controller",
            "approved_at": "2026-09-18T14:05:00Z",
            "reasoning": (
                "10,000 is below one percent of quarterly revenue for this entity, "
                "which matches the threshold used in the prior close."
            ),
            "entity": "Northstar Software Sample",
            "period": "2026-02",
            "source_hashes": dict(self.request["source_hashes"]),
        }
        payload.update(overrides)
        self.decision_path.write_text(json.dumps(payload), encoding="utf-8")
        return self.decision_path

    # --- the request ----------------------------------------------------

    def test_request_binds_every_source_file(self) -> None:
        self.assertEqual(set(self.request["source_hashes"]), SOURCE_FILES)
        self.assertEqual(self.request["demo_status"], "DEMO_UNAPPROVED")

    def test_request_refuses_an_incomplete_pack(self) -> None:
        (self.verified / "ledger.csv").unlink()
        with self.assertRaises(MaterialityError):
            build_approval_request(self.verified, "Northstar Software Sample",
                                   "2026-02", DEMO)

    # --- acceptance -----------------------------------------------------

    def test_approve_demo_keeps_the_amount(self) -> None:
        accepted = validate_approval(self._decision(), self.request)
        self.assertEqual(accepted["approved_amount"], "10000.00")
        self.assertEqual(accepted["decision"], "APPROVE_DEMO")

    def test_replace_states_a_different_amount(self) -> None:
        accepted = validate_approval(
            self._decision(decision="REPLACE", approved_amount="25000.00"),
            self.request,
        )
        self.assertEqual(accepted["approved_amount"], "25000.00")

    # --- the refusals, which are the point ------------------------------

    def test_agent_may_not_author_the_approval(self) -> None:
        for identity in ("agent", "AI", "mycroft-finance-investigator"):
            with self.subTest(identity=identity):
                with self.assertRaises(MaterialityError):
                    validate_approval(self._decision(approved_by=identity),
                                      self.request)

    def test_placeholder_reasoning_is_refused(self) -> None:
        with self.assertRaises(MaterialityError):
            validate_approval(self._decision(reasoning="ok"), self.request)

    def test_tampered_source_hash_is_refused(self) -> None:
        tampered = dict(self.request["source_hashes"])
        tampered["budget.csv"] = "0" * 64
        with self.assertRaises(MaterialityError):
            validate_approval(self._decision(source_hashes=tampered), self.request)

    def test_scope_mismatch_is_refused(self) -> None:
        with self.assertRaises(MaterialityError):
            validate_approval(self._decision(period="2026-03"), self.request)

    def test_approve_demo_cannot_change_the_amount(self) -> None:
        with self.assertRaises(MaterialityError):
            validate_approval(self._decision(approved_amount="25000.00"),
                              self.request)

    def test_replace_must_differ_from_the_demo_amount(self) -> None:
        with self.assertRaises(MaterialityError):
            validate_approval(
                self._decision(decision="REPLACE", approved_amount="10000.00"),
                self.request,
            )

    def test_replace_requires_an_amount(self) -> None:
        with self.assertRaises(MaterialityError):
            validate_approval(self._decision(decision="REPLACE"), self.request)

    def test_unknown_decision_is_refused(self) -> None:
        with self.assertRaises(MaterialityError):
            validate_approval(self._decision(decision="LOOKS_FINE"), self.request)

    def test_naive_timestamp_is_refused(self) -> None:
        with self.assertRaises(MaterialityError):
            validate_approval(self._decision(approved_at="2026-09-18T14:05:00"),
                              self.request)

    # --- recording is append-only ---------------------------------------

    def test_record_writes_an_approved_artifact(self) -> None:
        record = record_approval(self._decision(), self.request, self.output)
        self.assertEqual(record["materiality_status"], "APPROVED")
        self.assertEqual(len(record["decision_sha256"]), 64)
        self.assertTrue(self.output.is_file())

    def test_second_approval_cannot_overwrite_the_first(self) -> None:
        record_approval(self._decision(), self.request, self.output)
        with self.assertRaises(MaterialityError):
            record_approval(self._decision(), self.request, self.output)

    # --- reading it back re-proves it ------------------------------------

    def test_threshold_reads_back(self) -> None:
        record_approval(self._decision(), self.request, self.output)
        amount = approved_threshold(self.output, "Northstar Software Sample",
                                    "2026-02", self.verified)
        self.assertEqual(amount, DEMO)

    def test_threshold_refuses_after_the_data_changes(self) -> None:
        record_approval(self._decision(), self.request, self.output)
        (self.verified / "actuals.csv").write_text("column\ntampered\n",
                                                   encoding="utf-8")
        with self.assertRaises(MaterialityError):
            approved_threshold(self.output, "Northstar Software Sample",
                               "2026-02", self.verified)

    def test_threshold_refuses_another_scope(self) -> None:
        record_approval(self._decision(), self.request, self.output)
        with self.assertRaises(MaterialityError):
            approved_threshold(self.output, "Northstar Software Sample",
                               "2026-03", self.verified)


if __name__ == "__main__":
    unittest.main()

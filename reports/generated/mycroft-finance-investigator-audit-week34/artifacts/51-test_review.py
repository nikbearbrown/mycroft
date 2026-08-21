from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.review import (
    ReviewError,
    build_review_request,
    record_review_decision,
    validate_review_decision,
)


class ReviewGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_log = self.root / "run.json"
        self.run_log.write_text(
            json.dumps(
                {
                    "workflow": "mycroft-finance-investigator",
                    "run_id": "sample-run",
                    "config": {"materiality_amount": "10000.00"},
                    "investigation": {
                        "status": "COMPLETED_PENDING_HUMAN_REVIEW",
                        "evidence": [
                            "budget.csv:account=4000",
                            "actuals.csv:account=4000",
                        ],
                        "human_gate": {"status": "OPEN"},
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _decision(self, **changes: object) -> dict[str, object]:
        decision: dict[str, object] = {
            "run_id": "sample-run",
            "reviewer": {"name": "Morgan Lee", "role": "FP&A Manager"},
            "reviewed_at": "2026-07-31T17:00:00-04:00",
            "decision": "APPROVE",
            "materiality": {
                "decision": "APPROVE_DEMO",
                "amount": "10000.00",
                "reasoning": "Accepted for the bounded synthetic sample only.",
            },
            "causal_explanations": [
                {
                    "finding_statement": "Subscription revenue was below budget.",
                    "explanation": "Reviewed as a synthetic driver explanation.",
                    "evidence": ["budget.csv:account=4000"],
                }
            ],
            "tested": ["Source evidence and the EBITDA bridge"],
            "did_not_test": ["Production data or a live close"],
            "distribution_scope": "Synthetic demonstration only",
        }
        decision.update(changes)
        return decision

    def _write_decision(self, payload: dict[str, object]) -> Path:
        path = self.root / "decision.json"
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return path

    def test_review_request_is_open_and_bound_to_source_hash(self) -> None:
        request = build_review_request(self.run_log)

        self.assertEqual(request["gate_status"], "OPEN")
        self.assertEqual(request["run_id"], "sample-run")
        self.assertEqual(len(request["source_run_sha256"]), 64)
        self.assertEqual(request["reviewer"]["name"], "")

    def test_agent_cannot_clear_human_gate(self) -> None:
        payload = self._decision(
            reviewer={"name": "monthly-performance-investigator", "role": "Agent"}
        )

        with self.assertRaisesRegex(ReviewError, "cannot clear"):
            validate_review_decision(self.run_log, self._write_decision(payload))

    def test_approval_requires_causal_explanation(self) -> None:
        payload = self._decision(causal_explanations=[])

        with self.assertRaisesRegex(ReviewError, "requires at least one"):
            validate_review_decision(self.run_log, self._write_decision(payload))

    def test_unknown_evidence_is_rejected(self) -> None:
        payload = self._decision(
            causal_explanations=[
                {
                    "finding_statement": "Revenue changed.",
                    "explanation": "Owner explanation.",
                    "evidence": ["customers.csv:customer_id=UNKNOWN"],
                }
            ]
        )

        with self.assertRaisesRegex(ReviewError, "unknown references"):
            validate_review_decision(self.run_log, self._write_decision(payload))

    def test_request_changes_keeps_gate_closed_without_causal_claim(self) -> None:
        payload = self._decision(
            decision="REQUEST_CHANGES",
            materiality={
                "decision": "REJECT",
                "amount": "10000.00",
                "reasoning": "Threshold needs finance-owner review.",
            },
            causal_explanations=[],
        )
        artifact = validate_review_decision(
            self.run_log, self._write_decision(payload)
        )

        self.assertEqual(artifact["gate_status"], "NOT_CLEARED")
        self.assertEqual(artifact["decision_source"], "HUMAN_SUPPLIED")

    def test_record_is_append_only(self) -> None:
        decision_path = self._write_decision(self._decision())
        output_path = self.root / "gate-decisions" / "sample-run.json"
        artifact = record_review_decision(
            self.run_log, decision_path, output_path
        )

        self.assertEqual(artifact["gate_status"], "CLEARED")
        with self.assertRaisesRegex(ReviewError, "already exists"):
            record_review_decision(self.run_log, decision_path, output_path)

    def test_decision_must_match_run(self) -> None:
        payload = self._decision(run_id="different-run")

        with self.assertRaisesRegex(ReviewError, "does not match"):
            validate_review_decision(self.run_log, self._write_decision(payload))


if __name__ == "__main__":
    unittest.main()

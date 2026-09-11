from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.reinvestigation import (
    ReinvestigationError,
    load_follow_up_request,
    run_reinvestigation,
    write_reinvestigation_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
REQUEST = PROJECT_ROOT / "config/sample-follow-up-request.json"
SOURCE = REPO_ROOT / "logs/mycroft-finance-investigator-routing-week36.json"


class ReinvestigationTests(unittest.TestCase):
    def test_sample_classifies_verified_unsupported_and_open(self) -> None:
        result = run_reinvestigation(REQUEST, SOURCE, "follow-up")

        self.assertEqual(
            [item["after_status"] for item in result["results"]],
            ["VERIFIED", "UNSUPPORTED", "OPEN"],
        )
        self.assertEqual(result["summary"]["verified_count"], 1)
        self.assertEqual(result["summary"]["unsupported_count"], 1)
        self.assertEqual(result["summary"]["open_count"], 1)

    def test_replay_is_exact_and_does_not_clear_human_gate(self) -> None:
        result = run_reinvestigation(REQUEST, SOURCE, "replay")

        self.assertEqual(result["replay"], {"status": "EXACT_MATCH", "task_count": 3})
        self.assertEqual(
            result["summary"]["closure_status"],
            "BLOCKED_PENDING_HUMAN_REVIEW",
        )
        self.assertEqual(result["human_gate"]["status"], "OPEN")
        self.assertIsNone(result["causal_explanation"])
        self.assertIsNone(result["recommendation"])

    def test_causal_claim_remains_explicitly_unsupported(self) -> None:
        result = run_reinvestigation(REQUEST, SOURCE, "causal-boundary")
        causal_result = result["results"][1]

        self.assertEqual(causal_result["after_status"], "UNSUPPORTED")
        self.assertFalse(causal_result["causal_explanation_accepted"])
        self.assertIn("no approved causal evidence", causal_result["observation"])

    def test_source_orchestration_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_copy = Path(temporary) / "source.json"
            source_copy.write_text(
                SOURCE.read_text(encoding="utf-8") + " ", encoding="utf-8"
            )

            with self.assertRaisesRegex(ReinvestigationError, "hash does not match"):
                run_reinvestigation(REQUEST, source_copy, "tampered")

    def test_unknown_evidence_citation_is_rejected(self) -> None:
        payload = json.loads(REQUEST.read_text(encoding="utf-8"))
        payload["requests"][1]["cited_evidence"] = ["unknown.csv:row=1"]
        with tempfile.TemporaryDirectory() as temporary:
            request_path = Path(temporary) / "request.json"
            request_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ReinvestigationError, "unknown evidence"):
                run_reinvestigation(request_path, SOURCE, "unknown")

    def test_every_source_task_must_be_addressed(self) -> None:
        payload = json.loads(REQUEST.read_text(encoding="utf-8"))
        payload["requests"].pop()
        with tempfile.TemporaryDirectory() as temporary:
            request_path = Path(temporary) / "request.json"
            request_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ReinvestigationError, "every source task"):
                run_reinvestigation(request_path, SOURCE, "missing")

    def test_duplicate_task_request_is_rejected(self) -> None:
        payload = json.loads(REQUEST.read_text(encoding="utf-8"))
        payload["requests"][1]["task_id"] = "gap-revenue"
        with tempfile.TemporaryDirectory() as temporary:
            request_path = Path(temporary) / "request.json"
            request_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(ReinvestigationError, "duplicate task_id"):
                load_follow_up_request(request_path)

    def test_artifacts_are_append_only(self) -> None:
        result = run_reinvestigation(REQUEST, SOURCE, "append-only")
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "result.json"
            report_path = Path(temporary) / "result.md"
            write_reinvestigation_artifacts(result, log_path, report_path)

            with self.assertRaisesRegex(ReinvestigationError, "append-only"):
                write_reinvestigation_artifacts(result, log_path, report_path)

    def test_report_explains_what_verified_means(self) -> None:
        result = run_reinvestigation(REQUEST, SOURCE, "report")
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "result.json"
            report_path = Path(temporary) / "result.md"
            write_reinvestigation_artifacts(result, log_path, report_path)
            report = report_path.read_text(encoding="utf-8")

        self.assertIn("Before and After", report)
        self.assertIn("BLOCKED_PENDING_HUMAN_REVIEW", report)
        self.assertIn("does not verify a business cause", report)


if __name__ == "__main__":
    unittest.main()

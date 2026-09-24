from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mycroft_finance_investigator.evaluation import (
    EvaluationError,
    load_evaluation_cases,
    run_evaluation,
    write_evaluation_artifacts,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
RAW_SAMPLE = REPO_ROOT / "data/raw/mycroft-finance-investigator"
SCHEMA = PROJECT_ROOT / "schemas/finance-pack.schema.json"
CASES = PROJECT_ROOT / "evaluations/cases.json"
RUN_LOG = REPO_ROOT / "logs/mycroft-finance-investigator-sample-2026-02.json"


class EvaluationTests(unittest.TestCase):
    def test_all_planted_cases_match_expectations(self) -> None:
        result = run_evaluation(
            CASES, RAW_SAMPLE, SCHEMA, RUN_LOG, "week32-evaluation"
        )

        self.assertEqual(result["summary"]["case_count"], 7)
        self.assertEqual(result["summary"]["matched_count"], 7)
        self.assertEqual(result["summary"]["unexpected_count"], 0)
        self.assertEqual(result["summary"]["status"], "PASS")

    def test_evaluation_does_not_modify_source_data(self) -> None:
        before = {
            path.name: path.read_bytes()
            for path in RAW_SAMPLE.iterdir()
            if path.is_file()
        }
        run_evaluation(CASES, RAW_SAMPLE, SCHEMA, RUN_LOG, "source-integrity")
        after = {
            path.name: path.read_bytes()
            for path in RAW_SAMPLE.iterdir()
            if path.is_file()
        }

        self.assertEqual(after, before)

    def test_duplicate_case_identifier_is_rejected(self) -> None:
        payload = json.loads(CASES.read_text(encoding="utf-8"))
        payload["cases"].append(payload["cases"][0])
        with tempfile.TemporaryDirectory() as temporary:
            case_path = Path(temporary) / "duplicate.json"
            case_path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(EvaluationError, "duplicate"):
                load_evaluation_cases(case_path)

    def test_unexpected_result_fails_scorecard(self) -> None:
        payload = json.loads(CASES.read_text(encoding="utf-8"))
        payload["cases"] = [payload["cases"][0]]
        payload["cases"][0]["expected"]["step_count"] = 99
        with tempfile.TemporaryDirectory() as temporary:
            case_path = Path(temporary) / "wrong-expectation.json"
            case_path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_evaluation(
                case_path, RAW_SAMPLE, SCHEMA, RUN_LOG, "expected-failure"
            )

        self.assertEqual(result["summary"]["status"], "FAIL")
        self.assertEqual(result["summary"]["unexpected_count"], 1)
        self.assertIn("step_count", result["cases"][0]["differences"][0])

    def test_artifacts_disclose_the_adequacy_boundary(self) -> None:
        result = run_evaluation(CASES, RAW_SAMPLE, SCHEMA, RUN_LOG, "artifact-test")
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "evaluation.json"
            report_path = Path(temporary) / "evaluation.md"
            write_evaluation_artifacts(result, log_path, report_path)

            machine = json.loads(log_path.read_text(encoding="utf-8"))
            report = report_path.read_text(encoding="utf-8")

        self.assertEqual(machine["adequacy"], "PENDING_HUMAN_REVIEW")
        self.assertIn("not a model-confidence score", report)


if __name__ == "__main__":
    unittest.main()

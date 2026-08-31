import unittest
from unittest.mock import patch as mock_patch
from hsbc_pipeline.models import VulnerabilityReport
from hsbc_pipeline.orchestrator import VulnerabilityPatchPipeline


class TestFailFast(unittest.TestCase):
    def test_incomplete_report_escalates_before_assistant_runs(self):
        pipeline = VulnerabilityPatchPipeline(decision_fn=lambda p, r: True)
        with mock_patch("hsbc_pipeline.orchestrator.draft_patch") as mocked_assistant:
            report = VulnerabilityReport(id="", file_path="a.py", description="d")
            result = pipeline.run(report)
            self.assertEqual(result.status, "escalated")
            mocked_assistant.assert_not_called()

    def test_rejected_review_halts_before_apply_test(self):
        pipeline = VulnerabilityPatchPipeline(decision_fn=lambda p, r: False)
        with mock_patch("hsbc_pipeline.orchestrator.apply_patch_and_test") as mocked_apply:
            report = VulnerabilityReport(id="V1", file_path="a.py", description="d")
            result = pipeline.run(report)
            self.assertEqual(result.status, "rejected")
            self.assertEqual(result.reason, "not_approved")
            mocked_apply.assert_not_called()

    def test_pipeline_construction_fails_without_decision_fn(self):
        with self.assertRaises(ValueError):
            VulnerabilityPatchPipeline(decision_fn=None)


if __name__ == "__main__":
    unittest.main()

import unittest
from hsbc_pipeline.models import VulnerabilityReport
from hsbc_pipeline.orchestrator import VulnerabilityPatchPipeline


class TestEndToEnd(unittest.TestCase):
    def test_approved_patch_runs_to_completion(self):
        pipeline = VulnerabilityPatchPipeline(decision_fn=lambda p, r: True)
        report = VulnerabilityReport(id="V1", file_path="app/legacy.py", description="Unvalidated input")
        result = pipeline.run(report)
        self.assertEqual(result.status, "applied")
        self.assertEqual(result.patch.vulnerability_id, "V1")

    def test_rejected_patch_is_not_applied(self):
        pipeline = VulnerabilityPatchPipeline(decision_fn=lambda p, r: False)
        report = VulnerabilityReport(id="V2", file_path="app/legacy.py", description="Weak crypto")
        result = pipeline.run(report)
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.reason, "not_approved")
        # The draft patch is retained on the result for audit purposes even
        # though it was never applied.
        self.assertIsNotNone(result.patch)


if __name__ == "__main__":
    unittest.main()

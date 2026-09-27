import unittest
from hsbc_pipeline.review_gate import HumanReviewGate
from hsbc_pipeline.models import VulnerabilityReport, DraftPatch


class TestReviewGate(unittest.TestCase):
    def test_gate_requires_decision_fn(self):
        # Central design decision: no default policy ships with this Gate at all.
        with self.assertRaises(ValueError):
            HumanReviewGate(None)

    def test_gate_approves_when_fn_returns_true(self):
        gate = HumanReviewGate(lambda patch, report: True)
        report = VulnerabilityReport(id="V1", file_path="a.py", description="d")
        patch = DraftPatch(vulnerability_id="V1", diff="diff", assistant_notes="n")
        decision = gate.review(patch, report)
        self.assertTrue(decision.approved)

    def test_gate_rejects_with_reason_when_fn_returns_false(self):
        gate = HumanReviewGate(lambda patch, report: False)
        report = VulnerabilityReport(id="V1", file_path="a.py", description="d")
        patch = DraftPatch(vulnerability_id="V1", diff="diff", assistant_notes="n")
        decision = gate.review(patch, report)
        self.assertFalse(decision.approved)
        self.assertEqual(decision.reason, "not_approved")

    def test_gate_tests_contract_not_business_rule(self):
        # This confirms the Gate honors whatever the external function
        # decides, and that it is actually consulted — it does not, and
        # cannot, test what SHOULD approve a patch, since HSBC discloses no
        # such criteria (case study Section 3.2).
        calls = []

        def fn(patch, report):
            calls.append((patch.vulnerability_id, report.id))
            return True

        gate = HumanReviewGate(fn)
        report = VulnerabilityReport(id="V9", file_path="a.py", description="d")
        patch = DraftPatch(vulnerability_id="V9", diff="diff", assistant_notes="n")
        gate.review(patch, report)
        self.assertEqual(calls, [("V9", "V9")])


if __name__ == "__main__":
    unittest.main()

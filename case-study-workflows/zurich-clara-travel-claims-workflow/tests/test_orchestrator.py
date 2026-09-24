import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import orchestrator
import mock_data
from authorization_gate import demo_decision_fn


class TestOrchestrator(unittest.TestCase):
    def test_happy_path_resolves_end_to_end(self):
        claim = mock_data.CLAIM_KWAME_HAPPY_PATH
        result = orchestrator.run_pipeline(claim, demo_decision_fn)
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["claim_id"], claim["claim_id"])

    def test_incomplete_intake_halts_before_downstream_stages_are_called(self):
        claim = {"claim_id": "X", "policy_id": "POLICY-001", "documents": []}
        with patch("orchestrator.extract") as mock_extract, \
             patch("orchestrator.check_coverage") as mock_coverage, \
             patch("orchestrator.AuthorizationGate") as mock_gate:
            result = orchestrator.run_pipeline(claim, demo_decision_fn)

            mock_extract.assert_not_called()
            mock_coverage.assert_not_called()
            mock_gate.assert_not_called()
            self.assertEqual(result["status"], "escalated")

    def test_low_confidence_halts_before_coverage_check_and_gate_are_called(self):
        claim = mock_data.CLAIM_LOW_EXTRACTION_CONFIDENCE
        with patch("orchestrator.check_coverage") as mock_coverage, \
             patch("orchestrator.AuthorizationGate") as mock_gate:
            result = orchestrator.run_pipeline(claim, demo_decision_fn)

            mock_coverage.assert_not_called()
            mock_gate.assert_not_called()
            self.assertEqual(result["status"], "escalated")
            self.assertEqual(result["reason"], "low_extraction_confidence")

    def test_no_matching_policy_halts_before_gate_is_called(self):
        claim = mock_data.CLAIM_NO_MATCHING_POLICY
        with patch("orchestrator.AuthorizationGate") as mock_gate:
            result = orchestrator.run_pipeline(claim, demo_decision_fn)

            mock_gate.assert_not_called()
            self.assertEqual(result["status"], "escalated")
            self.assertEqual(result["reason"], "no_matching_policy")

    def test_gate_rejection_produces_named_reason_not_generic_flag(self):
        claim = mock_data.CLAIM_KWAME_HAPPY_PATH
        always_escalate_fn = lambda coverage_result: "escalated_to_human"
        result = orchestrator.run_pipeline(claim, always_escalate_fn)

        self.assertEqual(result["status"], "escalated")
        self.assertEqual(result["reason"], "authorization_gate_rejection")

    def test_missing_decision_fn_raises_type_error_through_orchestrator(self):
        claim = mock_data.CLAIM_KWAME_HAPPY_PATH
        with self.assertRaises(TypeError):
            orchestrator.run_pipeline(claim, None)

    def test_invalid_decision_fn_return_value_raises_value_error_and_does_not_reach_resolve(self):
        claim = mock_data.CLAIM_KWAME_HAPPY_PATH
        bad_fn = lambda coverage_result: "maybe"
        with patch("orchestrator.resolve") as mock_resolve, \
             patch("orchestrator.escalate") as mock_escalate:
            with self.assertRaises(ValueError):
                orchestrator.run_pipeline(claim, bad_fn)
            mock_resolve.assert_not_called()
            mock_escalate.assert_not_called()


if __name__ == "__main__":
    unittest.main()

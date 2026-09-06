import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from authorization_gate import AuthorizationGate, demo_decision_fn


class TestAuthorizationGate(unittest.TestCase):
    def test_raises_type_error_without_decision_fn(self):
        with self.assertRaises(TypeError):
            AuthorizationGate(None)

    def test_raises_value_error_on_invalid_return_value(self):
        gate = AuthorizationGate(lambda coverage_result: "not_a_valid_value")
        with self.assertRaises(ValueError):
            gate.decide({"flight_cancellation_covered": True, "tour_covered": True})

    def test_honors_whatever_the_supplied_function_returns_resolved(self):
        gate = AuthorizationGate(lambda coverage_result: "resolved_by_human")
        self.assertEqual(
            gate.decide({"flight_cancellation_covered": True, "tour_covered": True}),
            "resolved_by_human",
        )

    def test_honors_whatever_the_supplied_function_returns_escalated(self):
        gate = AuthorizationGate(lambda coverage_result: "escalated_to_human")
        self.assertEqual(
            gate.decide({"flight_cancellation_covered": False, "tour_covered": False}),
            "escalated_to_human",
        )

    def test_demo_decision_fn_is_contract_compliant(self):
        """Confirms the demo policy itself returns only valid values -- this
        is a contract test, not a test of what SHOULD authorize a claim."""
        gate = AuthorizationGate(demo_decision_fn)
        result = gate.decide({"flight_cancellation_covered": True, "tour_covered": True})
        self.assertIn(result, {"resolved_by_human", "escalated_to_human"})


if __name__ == "__main__":
    unittest.main()

import unittest

from authorization_gate import AuthorizationGate, GateOutcome
from verification import VerifiedClaim


def make_verified_claim():
    return VerifiedClaim(diagnosis="kennel cough", amount=120.0, date="2026-05-01")


class AuthorizationGateTests(unittest.TestCase):
    def test_policy_returns_true_settles(self):
        gate = AuthorizationGate()
        outcome = gate.decide(make_verified_claim(), policy_fn=lambda claim: True)

        self.assertEqual(outcome, GateOutcome(status="SETTLED", reason=None))

    def test_policy_returns_false_escalates_with_not_authorized(self):
        gate = AuthorizationGate()
        outcome = gate.decide(make_verified_claim(), policy_fn=lambda claim: False)

        self.assertEqual(outcome.status, "ESCALATED")
        self.assertEqual(outcome.reason, "not_authorized")

    # NOTE (per this component's /v3 card): no test in this file constructs
    # a Gate without a policy_fn, or asserts behavior for a missing/
    # non-callable policy_fn. That case belongs entirely to the
    # Orchestrator's own test module (tests/test_orchestrator.py) - see the
    # error-vs-escalation split documented in authorization_gate.py and
    # orchestrator.py.


if __name__ == "__main__":
    unittest.main()

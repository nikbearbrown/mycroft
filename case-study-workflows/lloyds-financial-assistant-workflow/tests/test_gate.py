import unittest

from lloyds_pipeline.gate import AuthorizationGate


class TestAuthorizationGateContract(unittest.TestCase):
    """
    These tests verify a CONTRACT, not a business rule. They confirm the
    Gate enforces its own construction and return-type requirements, and
    honors whatever its supplied decision function returns. They do not,
    and cannot, test what SHOULD authorize a real query -- Lloyds has not
    disclosed that boundary, and this scaffold does not invent one.
    """

    def test_raises_typeerror_when_no_decision_fn_supplied(self):
        with self.assertRaises(TypeError):
            AuthorizationGate(None)

    def test_raises_typeerror_when_decision_fn_not_callable(self):
        with self.assertRaises(TypeError):
            AuthorizationGate("not a function")

    def test_raises_valueerror_when_decision_fn_returns_non_bool(self):
        gate = AuthorizationGate(lambda ctx: "yes")
        with self.assertRaises(ValueError):
            gate.evaluate({})

    def test_returns_answered_directly_when_decision_fn_returns_true(self):
        gate = AuthorizationGate(lambda ctx: True)
        self.assertEqual(gate.evaluate({}), "answered_directly")

    def test_returns_escalated_to_human_when_decision_fn_returns_false(self):
        gate = AuthorizationGate(lambda ctx: False)
        self.assertEqual(gate.evaluate({}), "escalated_to_human")

    def test_decision_fn_receives_the_context_it_was_given(self):
        received = {}

        def capture(ctx):
            received.update(ctx)
            return True

        gate = AuthorizationGate(capture)
        gate.evaluate({"claimed_amount": 42.50})
        self.assertEqual(received, {"claimed_amount": 42.50})


if __name__ == "__main__":
    unittest.main()

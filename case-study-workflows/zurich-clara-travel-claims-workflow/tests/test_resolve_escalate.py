import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from resolve_escalate import resolve, escalate


class TestResolveEscalate(unittest.TestCase):
    def test_resolve_returns_resolved_status(self):
        result = resolve("CLAIM-1", {"flight_cancellation_covered": True, "tour_covered": True})
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["claim_id"], "CLAIM-1")

    def test_escalate_attaches_specific_named_reason(self):
        result = escalate("CLAIM-1", "no_matching_policy", "policy_id=NOPE")
        self.assertEqual(result["status"], "escalated")
        self.assertEqual(result["reason"], "no_matching_policy")
        self.assertNotEqual(result["reason"], "escalated")  # not a generic flag


if __name__ == "__main__":
    unittest.main()

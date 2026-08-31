import unittest
from hsbc_pipeline.models import VulnerabilityReport
from hsbc_pipeline.assistant import draft_patch


class TestAssistant(unittest.TestCase):
    def test_draft_patch_is_deterministic(self):
        # Canned stand-in, not a real model call — no variability between runs.
        r = VulnerabilityReport(id="V1", file_path="a.py", description="desc")
        p1 = draft_patch(r)
        p2 = draft_patch(r)
        self.assertEqual(p1.diff, p2.diff)

    def test_draft_patch_references_vulnerability_id(self):
        r = VulnerabilityReport(id="V42", file_path="b.py", description="XSS risk")
        p = draft_patch(r)
        self.assertEqual(p.vulnerability_id, "V42")


if __name__ == "__main__":
    unittest.main()

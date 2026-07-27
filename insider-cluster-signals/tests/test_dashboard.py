"""Tests for build_dashboard.py — the built page carries the data and no placeholder.
Run from insider-cluster-signals/: python -m unittest discover tests
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("build_dashboard", MODULE_DIR / "build_dashboard.py")
build_dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_dashboard)

DESIGN_TOKENS = {"#FFFFFF", "#2a1a0e", "#C8102E", "#545454", "#D4D4D4", "#C8860E"}


class TestBuildDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = build_dashboard.build()
        cls.html = cls.out.read_text(encoding="utf-8")
        cls.scored = json.loads((MODULE_DIR / "data" / "verified" / "scored_signals.json").read_text())

    def test_placeholder_replaced(self):
        self.assertNotIn("/*__DATA__*/", self.html)

    def test_every_ticker_present(self):
        for signal in self.scored["signals"]:
            self.assertIn(signal["ticker"], self.html)

    def test_contains_edgar_evidence_url(self):
        self.assertIn("https://www.sec.gov/Archives/edgar/data/", self.html)

    def test_tier_counts_match_scored_signals(self):
        summary = self.scored["summary"]
        self.assertIn(f'"strong": {summary["strong"]}', self.html)
        self.assertIn(f'"watch": {summary["watch"]}', self.html)

    def test_only_design_md_hex_colors(self):
        import re
        used = set(re.findall(r"#[0-9A-Fa-f]{6}\b", self.html))
        self.assertTrue(used.issubset(DESIGN_TOKENS), f"non-palette colors: {used - DESIGN_TOKENS}")

    def test_no_unescaped_close_script_in_payload(self):
        # the JSON payload must not be able to terminate the <script> block early
        body = self.html.split("const DATA = ", 1)[1]
        payload = body.split(";\n", 1)[0]
        self.assertNotIn("</script>", payload)


if __name__ == "__main__":
    unittest.main()

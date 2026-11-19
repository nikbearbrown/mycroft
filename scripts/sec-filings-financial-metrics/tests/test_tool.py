"""Tests for secfma.tool — offline, against the bundled SMPL fixture (no network).

Run from scripts/sec-filings-financial-metrics/:
    python3 -m unittest discover -s tests
"""
import json
import pathlib
import sys
import unittest

PKG_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG_DIR))

from secfma import tool  # noqa: E402
from secfma.tool import BASE_METRICS, TOOL_SPEC, get_verified_financials, run_tool  # noqa: E402

FIXTURE = json.loads((PKG_DIR / "secfma" / "fixtures" / "companyfacts_CIK0000000001.json").read_text())


def fixture_fy_value(tag, end):
    """The FY value the fixture reports for a us-gaap tag at a period end."""
    for e in FIXTURE["facts"]["us-gaap"][tag]["units"]["USD"]:
        if e.get("fp") == "FY" and e.get("end") == end:
            return e["val"]
    raise KeyError(tag)


def sample(**kw):
    return get_verified_financials("SMPL", sample=True, **kw)


class ToolSpecTests(unittest.TestCase):
    def test_spec_shape(self):
        self.assertEqual(TOOL_SPEC["name"], "get_verified_financials")
        schema = TOOL_SPEC["input_schema"]
        self.assertEqual(schema["required"], ["ticker"])
        self.assertEqual(set(schema["properties"]), {"ticker", "fiscal_year", "metrics"})
        self.assertEqual(schema["properties"]["metrics"]["items"]["enum"], list(BASE_METRICS))
        json.dumps(TOOL_SPEC)  # serializable

    def test_openai_shape_matches(self):
        fn = tool.as_openai_function()["function"]
        self.assertEqual(fn["name"], TOOL_SPEC["name"])
        self.assertEqual(fn["parameters"], TOOL_SPEC["input_schema"])


class SuccessTests(unittest.TestCase):
    def test_latest_year_by_default(self):
        out = sample()
        self.assertTrue(out["ok"])
        self.assertEqual(out["fiscal_year"], 2024)
        self.assertEqual(out["available_years"], [2023, 2024])
        self.assertEqual(out["company"]["cik"], "0000000001")
        self.assertFalse(out["method"]["llm_in_path"])
        self.assertEqual(out["method"]["mode"], "sample")

    def test_value_matches_filing_and_carries_provenance(self):
        out = sample(fiscal_year=2024, metrics=["revenue"])
        rev = out["metrics"]["revenue"]
        self.assertEqual(rev["status"], "OK")
        self.assertEqual(rev["value"], fixture_fy_value(
            "RevenueFromContractWithCustomerExcludingAssessedTax", "2024-12-31"))
        self.assertEqual(rev["source_tag"], "RevenueFromContractWithCustomerExcludingAssessedTax")
        self.assertEqual(rev["tag_source"], "us-gaap")
        for field in ("accession", "form", "filed", "source_url"):
            self.assertTrue(rev[field], field)

    def test_specific_earlier_year(self):
        out = sample(fiscal_year=2023, metrics=["net_income"])
        self.assertEqual(out["period_end"], "2023-12-31")
        self.assertEqual(out["metrics"]["net_income"]["value"],
                         fixture_fy_value("NetIncomeLoss", "2023-12-31"))

    def test_only_requested_metrics_returned(self):
        out = sample(metrics=["revenue", "total_assets"])
        self.assertEqual(set(out["metrics"]), {"revenue", "total_assets"})

    def test_custom_extension_is_labelled(self):
        rd = sample()["metrics"]["research_and_development"]
        self.assertEqual(rd["status"], "OK")
        self.assertEqual(rd["tag_source"], "custom-extension")
        self.assertEqual(rd["source_tag"], "ResearchAndDevelopmentInvestment")

    def test_missing_is_never_zero(self):
        cash = sample()["metrics"]["cash_and_equivalents"]   # no tag in the fixture
        self.assertEqual(cash["status"], "MISSING")
        self.assertIsNone(cash["value"])
        self.assertTrue(cash["reason"])

    def test_validation_attached_for_the_period(self):
        val = sample()["validation"]
        names = [c["check"] for c in val["checks"]]
        self.assertIn("check_accounting_identity", names)
        identity = next(c for c in val["checks"] if c["check"] == "check_accounting_identity")
        self.assertEqual(identity["result"], "PASS")
        self.assertEqual(sum(val["summary"].values()), len(val["checks"]))

    def test_deterministic(self):
        self.assertEqual(sample(fiscal_year=2024), sample(fiscal_year=2024))


class ErrorTests(unittest.TestCase):
    def assertError(self, out, kind):
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"]["type"], kind)

    def test_unknown_year_lists_available(self):
        out = sample(fiscal_year=1999)
        self.assertError(out, "fiscal_year_not_found")
        self.assertEqual(out["error"]["available_years"], [2023, 2024])

    def test_unknown_ticker(self):
        self.assertError(get_verified_financials("NOPE", sample=True), "ticker_not_found")

    def test_unknown_metric(self):
        out = sample(metrics=["revenue", "vibes"])
        self.assertError(out, "unknown_metric")
        self.assertIn("revenue", out["error"]["valid_metrics"])

    def test_bad_arguments(self):
        self.assertError(get_verified_financials("", sample=True), "invalid_argument")
        self.assertError(sample(fiscal_year="2024"), "invalid_argument")
        self.assertError(sample(fiscal_year=True), "invalid_argument")


class RunToolTests(unittest.TestCase):
    def test_raw_call_matches_direct_call(self):
        self.assertEqual(run_tool({"ticker": "smpl", "fiscal_year": 2024}, sample=True),
                         sample(fiscal_year=2024))

    def test_raw_call_rejects_bad_shapes(self):
        for args in (None, [], {}, {"ticker": "SMPL", "year": 2024},
                     {"ticker": "SMPL", "metrics": "revenue"}):
            out = run_tool(args, sample=True)
            self.assertFalse(out["ok"], args)
            self.assertEqual(out["error"]["type"], "invalid_argument", args)


if __name__ == "__main__":
    unittest.main()

"""
Financial grader tests — Week 9/10 analyst skeleton.
No network: fetch_fn/call_agent_fn are always injected fakes.
LangFuse tracing itself is not asserted on here (the SDK degrades
gracefully without configured credentials — see observability.py);
this only verifies the accountability-mesh behavior is unchanged.
"""

import unittest
import uuid

from adapters.mock_adapter import make_mock_adapter
from financial_grader import (
    EdgarFetchError,
    analyze_ticker,
    fetch_company_facts,
    lookup_cik,
    summarize_facts,
)
from middleware import HaltError, ValidationLoopResult
from schemas import AgentID, ParseStatus

_TICKER_MAP = {
    "0000320193": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
}

_FACTS = {
    "facts": {
        "us-gaap": {
            "Assets": {
                "units": {
                    "USD": [
                        {"end": "2025-09-30", "val": 350000000000},
                        {"end": "2026-03-31", "val": 365000000000},
                    ]
                }
            },
            "Revenues": {
                "units": {
                    "USD": [
                        {"end": "2026-03-31", "val": 90000000000},
                    ]
                }
            },
            # NetIncomeLoss deliberately absent to test the "not reported" path
        }
    }
}


def _fake_ticker_map_fetch(url: str) -> dict:
    return _TICKER_MAP


def _fake_facts_fetch(url: str) -> dict:
    return _FACTS


class TestLookupCik(unittest.TestCase):

    def test_finds_known_ticker(self):
        cik = lookup_cik("AAPL", fetch_fn=_fake_ticker_map_fetch)
        self.assertEqual(cik, "0000320193")

    def test_case_insensitive(self):
        cik = lookup_cik("aapl", fetch_fn=_fake_ticker_map_fetch)
        self.assertEqual(cik, "0000320193")

    def test_unknown_ticker_raises(self):
        with self.assertRaises(EdgarFetchError):
            lookup_cik("ZZZZ", fetch_fn=_fake_ticker_map_fetch)


class TestFetchCompanyFacts(unittest.TestCase):

    def test_returns_injected_facts(self):
        facts = fetch_company_facts("AAPL", "0000320193", fetch_fn=_fake_facts_fetch)
        self.assertEqual(facts, _FACTS)


class TestSummarizeFacts(unittest.TestCase):

    def test_includes_ticker(self):
        summary = summarize_facts("AAPL", _FACTS)
        self.assertIn("Ticker: AAPL", summary)

    def test_picks_latest_assets_value(self):
        summary = summarize_facts("AAPL", _FACTS)
        self.assertIn("Assets: 365000000000.0", summary)

    def test_missing_concept_reported_as_not_reported(self):
        summary = summarize_facts("AAPL", _FACTS)
        self.assertIn("NetIncomeLoss: not reported", summary)

    def test_empty_facts_all_not_reported(self):
        summary = summarize_facts("AAPL", {"facts": {}})
        self.assertIn("Assets: not reported", summary)
        self.assertIn("Revenues: not reported", summary)
        self.assertIn("NetIncomeLoss: not reported", summary)


class TestAnalyzeTicker(unittest.TestCase):

    def setUp(self):
        self.run_id = uuid.uuid4()

    def test_happy_path_returns_validation_loop_result(self):
        result = analyze_ticker(
            "AAPL",
            "0000320193",
            make_mock_adapter("none"),
            run_id=self.run_id,
            fetch_fn=_fake_facts_fetch,
        )
        self.assertIsInstance(result, ValidationLoopResult)

    def test_happy_path_reasoning_object_for_financial_agent(self):
        result = analyze_ticker(
            "AAPL",
            "0000320193",
            make_mock_adapter("none"),
            run_id=self.run_id,
            fetch_fn=_fake_facts_fetch,
        )
        obj = result.reasoning_objects[0]
        self.assertEqual(obj.agent_id, AgentID.FINANCIAL)
        self.assertEqual(obj.parse_status, ParseStatus.SUCCESS)
        self.assertEqual(obj.run_id, self.run_id)

    def test_context_passed_to_agent_includes_facts(self):
        # mock_adapter echoes the context into thought_log — confirms EDGAR
        # facts actually flowed into the LLM call, not just a placeholder.
        result = analyze_ticker(
            "AAPL",
            "0000320193",
            make_mock_adapter("none"),
            run_id=self.run_id,
            fetch_fn=_fake_facts_fetch,
        )
        self.assertIn("Assets: 365000000000.0", result.reasoning_objects[0].thought_log)

    def test_retry_success_still_reaches_success(self):
        result = analyze_ticker(
            "AAPL",
            "0000320193",
            make_mock_adapter("retry_success"),
            run_id=self.run_id,
            fetch_fn=_fake_facts_fetch,
        )
        self.assertEqual(len(result.reasoning_objects), 2)
        self.assertEqual(result.reasoning_objects[1].parse_status, ParseStatus.SUCCESS)

    def test_halt_mode_raises_halt_error(self):
        with self.assertRaises(HaltError) as ctx:
            analyze_ticker(
                "AAPL",
                "0000320193",
                make_mock_adapter("halt"),
                run_id=self.run_id,
                fetch_fn=_fake_facts_fetch,
            )
        self.assertEqual(len(ctx.exception.reasoning_objects), 2)

    def test_bad_edgar_fetch_propagates(self):
        def _broken_fetch(url: str) -> dict:
            raise EdgarFetchError("simulated network failure")

        with self.assertRaises(EdgarFetchError):
            analyze_ticker(
                "AAPL",
                "0000320193",
                make_mock_adapter("none"),
                run_id=self.run_id,
                fetch_fn=_broken_fetch,
            )


if __name__ == "__main__":
    unittest.main()

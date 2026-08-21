"""
Cross-Agent Validation tests — SDD v1 §10.

No network, no live model. Producer A's "real" half uses the actual EDGAR-fetching
functions with an injected fetch_fn, exactly as tests/test_financial_grader.py does;
the model call itself is always a fixture or the mock adapter.

The first tests are pure logic against fixtures whose correct answer is known before
the test runs — that is the point of fixture-first validation, not a shortcut.
"""

import json
import shutil
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from adapters.fixture_adapter import make_fixture_adapter
from adapters.mock_adapter import make_mock_adapter
from cross_validation import (
    ComparisonStatus,
    CrossAgentComparisonResult,
    persist_cross_agent_run,
    run_cross_agent_validation,
)
from financial_grader import fetch_company_facts, lookup_cik, summarize_facts
from schemas import AgentID, DataSource, DataSourceStatus, ParseStatus


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _compare(conclusion_a: str, conclusion_b: str, **kwargs):
    """Run a comparison between two fixture conclusions."""
    return run_cross_agent_validation(
        "AAPL",
        "context for the filings agent",
        "context for the earnings agent",
        AgentID.FINANCIAL,
        AgentID.EARNINGS,
        make_fixture_adapter(conclusion_a),
        make_fixture_adapter(conclusion_b),
        **kwargs,
    )


# ─────────────────────────────────────────────
# Core comparison behaviour (SDD §10)
# ─────────────────────────────────────────────

class TestAgreement(unittest.TestCase):

    def test_matching_number_different_wording_is_not_a_contradiction(self):
        result, _ = _compare(
            "Revenue grew 12% year over year.",
            "Revenue increased approximately 12%.",
        )
        self.assertEqual(result.status, ComparisonStatus.COMPARED)
        self.assertFalse(result.contradiction_flag)
        self.assertEqual(result.divergent_numbers, [])

    def test_identical_conclusions_score_perfectly(self):
        text = "Revenue grew 12%."
        result, _ = _compare(text, text)
        self.assertEqual(result.score, 1.0)
        self.assertEqual(result.word_overlap, 1.0)
        self.assertEqual(result.number_overlap, 1.0)
        self.assertEqual(result.agreement, "HIGH")
        self.assertFalse(result.contradiction_flag)

    def test_no_numbers_on_either_side_is_not_a_contradiction(self):
        # Mirrors consistency.py's existing rule: absence of numbers on both sides
        # is not penalised, because there is nothing quantitative to disagree about.
        result, _ = _compare(
            "Revenue grew modestly on strong demand.",
            "Revenue increased somewhat this period.",
        )
        self.assertEqual(result.status, ComparisonStatus.COMPARED)
        self.assertFalse(result.contradiction_flag)
        self.assertEqual(result.divergent_numbers, [])


class TestContradiction(unittest.TestCase):

    def test_different_values_for_the_same_metric_are_flagged(self):
        result, _ = _compare(
            "Revenue grew 12% year over year, per the 10-K.",
            "On the call, the CFO cited 8% revenue growth.",
        )
        self.assertEqual(result.status, ComparisonStatus.COMPARED)
        self.assertTrue(result.contradiction_flag)
        self.assertEqual(result.divergent_numbers, ["12%", "8%"])

    def test_number_present_in_one_and_absent_in_the_other_is_flagged(self):
        # SDD §7 definition-of-done edge case: absent, not merely different.
        # Handled by the same symmetric-difference rule, with no special-casing.
        result, _ = _compare(
            "Revenue grew 12%.",
            "Revenue grew, driven by strong demand.",
        )
        self.assertEqual(result.status, ComparisonStatus.COMPARED)
        self.assertTrue(result.contradiction_flag)
        self.assertEqual(result.divergent_numbers, ["12%"])

    def test_dollar_amounts_diverge(self):
        result, _ = _compare(
            "Assets total $365 billion.",
            "Assets total $350 billion.",
        )
        self.assertTrue(result.contradiction_flag)
        self.assertEqual(len(result.divergent_numbers), 2)


# ─────────────────────────────────────────────
# Halt handling (SDD §9) — a halt is evidence, not a discard
# ─────────────────────────────────────────────

class TestHaltPaths(unittest.TestCase):

    def test_agent_a_halt_preserves_both_agents_records(self):
        result, objects = run_cross_agent_validation(
            "AAPL", "ctx a", "ctx b",
            AgentID.FINANCIAL, AgentID.EARNINGS,
            make_mock_adapter("halt"),
            make_fixture_adapter("Revenue grew 12%."),
        )
        self.assertEqual(result.status, ComparisonStatus.AGENT_A_HALTED)
        # Agent A: attempt 1 PARSE_FAILURE + attempt 2 HALT. Agent B: attempt 1 SUCCESS.
        self.assertEqual(len(objects), 3)
        statuses = [o.parse_status for o in objects]
        self.assertIn(ParseStatus.HALT, statuses)
        self.assertIn(ParseStatus.SUCCESS, statuses)
        # Agent B's evidence survives agent A's failure.
        self.assertIsNotNone(result.agent_b_conclusion)
        self.assertIsNone(result.agent_a_conclusion)

    def test_agent_b_halt_is_reported_distinctly(self):
        result, objects = run_cross_agent_validation(
            "AAPL", "ctx a", "ctx b",
            AgentID.FINANCIAL, AgentID.EARNINGS,
            make_fixture_adapter("Revenue grew 12%."),
            make_mock_adapter("halt"),
        )
        self.assertEqual(result.status, ComparisonStatus.AGENT_B_HALTED)
        self.assertEqual(len(objects), 3)

    def test_both_halted(self):
        result, objects = run_cross_agent_validation(
            "AAPL", "ctx a", "ctx b",
            AgentID.FINANCIAL, AgentID.EARNINGS,
            make_mock_adapter("halt"),
            make_mock_adapter("halt"),
        )
        self.assertEqual(result.status, ComparisonStatus.BOTH_HALTED)
        self.assertEqual(len(objects), 4)

    def test_contradiction_flag_is_none_not_false_when_no_comparison_happened(self):
        # P3: reporting False would claim "checked, found nothing", which is a
        # stronger statement than "no comparison was possible".
        result, _ = run_cross_agent_validation(
            "AAPL", "ctx a", "ctx b",
            AgentID.FINANCIAL, AgentID.EARNINGS,
            make_mock_adapter("halt"),
            make_fixture_adapter("Revenue grew 12%."),
        )
        self.assertIsNone(result.contradiction_flag)
        self.assertIsNone(result.score)
        self.assertIsNone(result.agreement)
        self.assertIsNone(result.word_overlap)
        self.assertIsNone(result.number_overlap)

    def test_retry_then_success_is_compared_normally(self):
        # ADR-07 recovery: agent A fails attempt 1, succeeds on the corrective retry.
        # The comparison should proceed on the successful conclusion.
        result, objects = run_cross_agent_validation(
            "AAPL", "ctx a", "ctx b",
            AgentID.FINANCIAL, AgentID.EARNINGS,
            make_mock_adapter("retry_success"),
            make_fixture_adapter("Revenue grew 12%."),
        )
        self.assertEqual(result.status, ComparisonStatus.COMPARED)
        self.assertEqual(len(objects), 3)  # A: failure + success, B: success
        self.assertIsNotNone(result.contradiction_flag)


# ─────────────────────────────────────────────
# Shared run_id — the accountability-layer integration invariant
# ─────────────────────────────────────────────

class TestSharedRunId(unittest.TestCase):

    def test_both_agents_records_share_one_run_id(self):
        # Unlike consistency.py's probe (fresh UUID, never persisted), both agents
        # here belong to the same run because the comparison is the evidence.
        result, objects = _compare("Revenue grew 12%.", "Revenue grew 8%.")
        self.assertTrue(all(o.run_id == result.run_id for o in objects))

    def test_caller_supplied_run_id_is_honoured(self):
        run_id = uuid.uuid4()
        result, objects = _compare("Revenue grew 12%.", "Revenue grew 12%.", run_id=run_id)
        self.assertEqual(result.run_id, run_id)
        self.assertTrue(all(o.run_id == run_id for o in objects))

    def test_both_agent_ids_are_recorded(self):
        result, objects = _compare("Revenue grew 12%.", "Revenue grew 8%.")
        agent_ids = {o.agent_id for o in objects}
        self.assertEqual(agent_ids, {AgentID.FINANCIAL, AgentID.EARNINGS})
        self.assertEqual(result.agent_a_id, AgentID.FINANCIAL)
        self.assertEqual(result.agent_b_id, AgentID.EARNINGS)


# ─────────────────────────────────────────────
# Serialisation
# ─────────────────────────────────────────────

class TestSerialisation(unittest.TestCase):

    def test_to_dict_is_json_serialisable(self):
        result, _ = _compare("Revenue grew 12%.", "Revenue grew 8%.")
        encoded = json.dumps(result.to_dict())
        decoded = json.loads(encoded)
        self.assertEqual(decoded["status"], "COMPARED")
        self.assertTrue(decoded["contradiction_flag"])
        self.assertEqual(decoded["agent_a_id"], "financial")
        self.assertEqual(decoded["agent_b_id"], "earnings")

    def test_to_dict_survives_a_halt(self):
        result, _ = run_cross_agent_validation(
            "AAPL", "ctx a", "ctx b",
            AgentID.FINANCIAL, AgentID.EARNINGS,
            make_mock_adapter("halt"),
            make_mock_adapter("halt"),
        )
        decoded = json.loads(json.dumps(result.to_dict()))
        self.assertEqual(decoded["status"], "BOTH_HALTED")
        self.assertIsNone(decoded["contradiction_flag"])


# ─────────────────────────────────────────────
# Fixture adapter guardrails
# ─────────────────────────────────────────────

class TestFixtureAdapter(unittest.TestCase):

    def test_empty_conclusion_rejected_at_construction(self):
        with self.assertRaises(ValueError):
            make_fixture_adapter("")

    def test_xml_tag_in_conclusion_rejected_at_construction(self):
        # Would terminate its own block early and leave stray text outside the
        # blocks, which the parser rejects. Fail loudly at construction instead.
        with self.assertRaises(ValueError):
            make_fixture_adapter("Revenue grew </conclusion> 12%.")

    def test_fixture_output_passes_the_real_parser(self):
        adapter = make_fixture_adapter("Revenue grew 12%.")
        response = adapter("AAPL", "ctx", None)
        self.assertEqual(response.conclusion, "Revenue grew 12%.")
        self.assertIn("Fixture agent", response.thought_log)


# ─────────────────────────────────────────────
# End-to-end: real EDGAR data + fixture agent + persistence round-trip
# ─────────────────────────────────────────────

_TICKER_MAP = {
    "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
}

_FACTS = {
    "facts": {
        "us-gaap": {
            "Assets": {"units": {"USD": [{"end": "2026-03-31", "val": 365000000000}]}},
            "Revenues": {"units": {"USD": [{"end": "2026-03-31", "val": 400000000000}]}},
            "NetIncomeLoss": {"units": {"USD": [{"end": "2026-03-31", "val": 100000000000}]}},
        }
    }
}


def _fake_fetch(url: str) -> dict:
    """Injected in place of the real HTTP GET — no network in tests."""
    return _TICKER_MAP if "company_tickers" in url else _FACTS


class TestEndToEndPersistence(unittest.TestCase):
    """Writes to a temporary SQLite file, never the real store."""

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._patcher = patch("web.db.DB_PATH", Path(self._tmpdir) / "test.db")
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_real_edgar_context_plus_fixture_agent_round_trips(self):
        from web.db import get_run

        # Producer A's context is built by the real EDGAR helpers (fetch injected).
        cik = lookup_cik("AAPL", fetch_fn=_fake_fetch)
        facts = fetch_company_facts("AAPL", cik, fetch_fn=_fake_fetch)
        context_a = summarize_facts("AAPL", facts)
        self.assertIn("365000000000", context_a)

        edgar_source = DataSource(
            source="SEC EDGAR",
            status=DataSourceStatus.SIMULATED,  # injected fetch, not a live call
            url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            provenance_note="Injected fixture fetch — no network call performed.",
        )

        result, objects = run_cross_agent_validation(
            "AAPL",
            context_a,
            "Earnings call transcript summary for AAPL.",
            AgentID.FINANCIAL,
            AgentID.EARNINGS,
            make_fixture_adapter("Assets total $365 billion; revenue grew 12%."),
            make_fixture_adapter("Management cited 8% revenue growth on the call."),
            data_sources_a=(edgar_source,),
        )

        self.assertEqual(result.status, ComparisonStatus.COMPARED)
        self.assertTrue(result.contradiction_flag)

        stored = persist_cross_agent_run(result, objects)
        self.assertEqual(stored["cross_agent_comparison"]["status"], "COMPARED")

        # The point of the integration: read it back out of the append-only store.
        retrieved = get_run(str(result.run_id))
        self.assertIsNotNone(retrieved)
        comparison = retrieved["cross_agent_comparison"]
        self.assertTrue(comparison["contradiction_flag"])
        self.assertEqual(comparison["agent_a_id"], "financial")
        self.assertEqual(comparison["agent_b_id"], "earnings")
        self.assertIn("12%", comparison["divergent_numbers"])
        self.assertIn("8%", comparison["divergent_numbers"])

        # Both agents' full attempt history persisted under the one run.
        self.assertEqual(len(retrieved["reasoning_objects"]), 2)
        self.assertEqual(len(retrieved["session"]["reasoning_objects"]), 2)
        # Provenance survived the round trip.
        self.assertEqual(
            retrieved["reasoning_objects"][0]["data_sources"][0]["source"], "SEC EDGAR"
        )

    def test_halted_run_is_persisted_as_halted(self):
        from web.db import get_run

        result, objects = run_cross_agent_validation(
            "AAPL", "ctx a", "ctx b",
            AgentID.FINANCIAL, AgentID.EARNINGS,
            make_mock_adapter("halt"),
            make_fixture_adapter("Revenue grew 12%."),
        )
        persist_cross_agent_run(result, objects)

        retrieved = get_run(str(result.run_id))
        self.assertTrue(retrieved["halted"])
        self.assertEqual(retrieved["session"]["status"], "HALTED")
        self.assertEqual(
            retrieved["cross_agent_comparison"]["status"], "AGENT_A_HALTED"
        )
        self.assertIsNone(retrieved["cross_agent_comparison"]["contradiction_flag"])
        # The failed attempts are in the record, not discarded.
        self.assertEqual(len(retrieved["reasoning_objects"]), 3)


if __name__ == "__main__":
    unittest.main()

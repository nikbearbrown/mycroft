"""
Accountability Layer — Phase 1 Tests
Covers: ReasoningObject, RunSession, SEC-01 investor projection, directive registry.

Run with:  python3 -m pytest tests/test_phase1_schemas.py -v
       or: python3 -m unittest tests.test_phase1_schemas -v
"""

import json
import sys
import os
import uuid
from datetime import datetime, timezone
import unittest

# Allow running from accountability_layer/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import (
    AgentID,
    Citation,
    ConfidenceClassification,
    DataSource,
    DataSourceStatus,
    ParseStatus,
    ReasoningObject,
    RunSession,
    RunStatus,
    ValidationError,
)
from directive import (
    ACTIVE_DIRECTIVE,
    DIRECTIVE_V1_0_0,
    get_active_directive,
    get_directive,
)


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

def make_reasoning_object(
    run_id=None,
    agent_id=AgentID.FINANCIAL,
    parse_status=ParseStatus.SUCCESS,
    conclusion="Strong Q3 earnings. Buy recommendation.",
    confidence_score=0.85,
    attempt_number=1,
    thought_log="<thought_log>Reviewed 10-K. No anomalies found.</thought_log>",
    data_quality_warnings=(),
    confidence_degradation_reason=None,
    raw_output=None,
    llm_tokens=None,
) -> ReasoningObject:
    return ReasoningObject(
        run_id=run_id or uuid.uuid4(),
        agent_id=agent_id,
        attempt_number=attempt_number,
        parse_status=parse_status,
        confidence_score=confidence_score,
        conclusion=conclusion,
        thought_log=thought_log,
        data_quality_warnings=data_quality_warnings,
        confidence_degradation_reason=confidence_degradation_reason,
        raw_output=raw_output,
        llm_tokens=llm_tokens,
    )


def make_run_session(run_id=None, ticker="AAPL") -> RunSession:
    return RunSession(
        run_id=run_id or uuid.uuid4(),
        ticker=ticker,
        directive_version=ACTIVE_DIRECTIVE.version,
        directive_text=ACTIVE_DIRECTIVE.text,
    )


# ─────────────────────────────────────────────
# ReasoningObject — happy path
# ─────────────────────────────────────────────

class TestReasoningObjectHappyPath(unittest.TestCase):

    def test_creates_with_required_fields(self):
        ro = make_reasoning_object()
        self.assertEqual(ro.agent_id, AgentID.FINANCIAL)
        self.assertEqual(ro.parse_status, ParseStatus.SUCCESS)
        self.assertEqual(ro.confidence_score, 0.85)
        self.assertIsNotNone(ro.reasoning_id)

    def test_reasoning_id_is_uuid(self):
        ro = make_reasoning_object()
        self.assertIsInstance(ro.reasoning_id, uuid.UUID)

    def test_created_at_is_timezone_aware(self):
        ro = make_reasoning_object()
        self.assertIsNotNone(ro.created_at.tzinfo)

    def test_confidence_score_rounded_to_4dp(self):
        ro = make_reasoning_object(confidence_score=0.123456789)
        self.assertEqual(ro.confidence_score_rounded, round(0.123456789, 4))

    def test_all_agent_ids_accepted(self):
        for agent in AgentID:
            ro = make_reasoning_object(agent_id=agent)
            self.assertEqual(ro.agent_id, agent)

    def test_parse_failure_without_conclusion_is_valid(self):
        ro = make_reasoning_object(parse_status=ParseStatus.PARSE_FAILURE, conclusion=None)
        self.assertEqual(ro.parse_status, ParseStatus.PARSE_FAILURE)
        self.assertIsNone(ro.conclusion)

    def test_halt_without_conclusion_is_valid(self):
        ro = make_reasoning_object(parse_status=ParseStatus.HALT, conclusion=None)
        self.assertEqual(ro.parse_status, ParseStatus.HALT)

    def test_data_sources_stored(self):
        ds = DataSource(
            source="SEC EDGAR",
            url="https://sec.gov/cgi-bin/browse-edgar",
            fetched_at=datetime.now(timezone.utc),
            status=DataSourceStatus.LIVE,
        )
        ro = ReasoningObject(
            run_id=uuid.uuid4(),
            agent_id=AgentID.FINANCIAL,
            attempt_number=1,
            parse_status=ParseStatus.SUCCESS,
            confidence_score=0.9,
            conclusion="Revenue up 14%.",
            data_sources=(ds,),
        )
        self.assertEqual(len(ro.data_sources), 1)
        self.assertEqual(ro.data_sources[0].source, "SEC EDGAR")

    def test_citations_stored(self):
        cit = Citation(label="10-K 2024 p.12", url="https://sec.gov/x", excerpt="Revenue grew 14%")
        ro = ReasoningObject(
            run_id=uuid.uuid4(),
            agent_id=AgentID.FINANCIAL,
            attempt_number=1,
            parse_status=ParseStatus.SUCCESS,
            confidence_score=0.9,
            conclusion="Strong buy.",
            citations=(cit,),
        )
        self.assertEqual(ro.citations[0].label, "10-K 2024 p.12")

    def test_attempt2_success_is_valid(self):
        ro = make_reasoning_object(attempt_number=2, parse_status=ParseStatus.SUCCESS)
        self.assertEqual(ro.attempt_number, 2)

    def test_attempt2_halt_is_valid(self):
        ro = make_reasoning_object(
            attempt_number=2,
            parse_status=ParseStatus.HALT,
            conclusion=None,
        )
        self.assertEqual(ro.parse_status, ParseStatus.HALT)


# ─────────────────────────────────────────────
# ReasoningObject — validation failures
# ─────────────────────────────────────────────

class TestReasoningObjectValidation(unittest.TestCase):

    def test_success_without_conclusion_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            make_reasoning_object(parse_status=ParseStatus.SUCCESS, conclusion=None)
        self.assertIn("conclusion is required", str(ctx.exception))

    def test_confidence_score_above_1_raises(self):
        with self.assertRaises(ValidationError):
            make_reasoning_object(confidence_score=1.1)

    def test_confidence_score_below_0_raises(self):
        with self.assertRaises(ValidationError):
            make_reasoning_object(confidence_score=-0.01)

    def test_attempt_number_3_raises(self):
        with self.assertRaises(ValidationError):
            make_reasoning_object(attempt_number=3)

    def test_attempt_number_0_raises(self):
        with self.assertRaises(ValidationError):
            make_reasoning_object(attempt_number=0)

    def test_attempt2_parse_failure_raises(self):
        """ADR-07: second attempt result must be SUCCESS or HALT, never PARSE_FAILURE."""
        with self.assertRaises(ValidationError) as ctx:
            make_reasoning_object(
                attempt_number=2,
                parse_status=ParseStatus.PARSE_FAILURE,
                conclusion=None,
            )
        self.assertIn("attempt_number=2 cannot have parse_status=PARSE_FAILURE", str(ctx.exception))

    def test_data_quality_warnings_without_degradation_reason_raises(self):
        """ADR-04: warnings present → degradation reason required."""
        with self.assertRaises(ValidationError) as ctx:
            make_reasoning_object(
                data_quality_warnings=("simulated_data",),
                confidence_degradation_reason=None,
            )
        self.assertIn("confidence_degradation_reason must be set", str(ctx.exception))

    def test_data_quality_warnings_with_reason_passes(self):
        ro = make_reasoning_object(
            data_quality_warnings=("simulated_data",),
            confidence_degradation_reason="simulated_data_penalty: score reduced by 0.2",
        )
        self.assertEqual(len(ro.data_quality_warnings), 1)

    def test_immutable_after_construction(self):
        """frozen=True: ReasoningObject must reject mutation."""
        ro = make_reasoning_object()
        with self.assertRaises((AttributeError, TypeError)):
            ro.confidence_score = 0.5  # type: ignore


# ─────────────────────────────────────────────
# RunSession — happy path
# ─────────────────────────────────────────────

class TestRunSessionHappyPath(unittest.TestCase):

    def test_creates_open_session(self):
        rs = make_run_session()
        self.assertEqual(rs.status, RunStatus.OPEN)
        self.assertEqual(rs.ticker, "AAPL")
        self.assertIsNotNone(rs.run_id)

    def test_ticker_normalised_to_uppercase(self):
        rs = RunSession(
            ticker="aapl",
            directive_version=ACTIVE_DIRECTIVE.version,
            directive_text=ACTIVE_DIRECTIVE.text,
        )
        self.assertEqual(rs.ticker, "AAPL")

    def test_ticker_whitespace_stripped(self):
        rs = RunSession(
            ticker="  NVDA  ",
            directive_version=ACTIVE_DIRECTIVE.version,
            directive_text=ACTIVE_DIRECTIVE.text,
        )
        self.assertEqual(rs.ticker, "NVDA")

    def test_directive_stored_verbatim(self):
        """ADR-05: full directive text must survive round-trip unchanged."""
        rs = make_run_session()
        self.assertEqual(rs.directive_text, ACTIVE_DIRECTIVE.text)

    def test_directive_version_stored(self):
        rs = make_run_session()
        self.assertEqual(rs.directive_version, "v1.1.0")

    def test_aan_not_triggered_by_default(self):
        rs = make_run_session()
        self.assertFalse(rs.aan_triggered)

    def test_complete_session_standard_confidence(self):
        rs = RunSession(
            ticker="TSLA",
            status=RunStatus.COMPLETE,
            directive_version=ACTIVE_DIRECTIVE.version,
            directive_text=ACTIVE_DIRECTIVE.text,
            run_confidence_score=0.72,
            confidence_classification=ConfidenceClassification.STANDARD,
            completed_at=datetime.now(timezone.utc),
        )
        self.assertEqual(rs.confidence_classification, ConfidenceClassification.STANDARD)

    def test_high_uncertainty_below_threshold(self):
        rs = RunSession(
            ticker="GME",
            status=RunStatus.COMPLETE,
            directive_version=ACTIVE_DIRECTIVE.version,
            directive_text=ACTIVE_DIRECTIVE.text,
            run_confidence_score=0.31,
            confidence_classification=ConfidenceClassification.HIGH_UNCERTAINTY,
            completed_at=datetime.now(timezone.utc),
        )
        self.assertEqual(rs.confidence_classification, ConfidenceClassification.HIGH_UNCERTAINTY)

    def test_exactly_0_4_is_standard(self):
        """ADR-08 boundary: 0.4 is STANDARD, not HIGH_UNCERTAINTY."""
        rs = RunSession(
            ticker="NVDA",
            status=RunStatus.COMPLETE,
            directive_version=ACTIVE_DIRECTIVE.version,
            directive_text=ACTIVE_DIRECTIVE.text,
            run_confidence_score=0.4,
            confidence_classification=ConfidenceClassification.STANDARD,
            completed_at=datetime.now(timezone.utc),
        )
        self.assertEqual(rs.confidence_classification, ConfidenceClassification.STANDARD)


# ─────────────────────────────────────────────
# RunSession — validation failures
# ─────────────────────────────────────────────

class TestRunSessionValidation(unittest.TestCase):

    def test_completed_at_on_open_session_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            RunSession(
                ticker="AAPL",
                status=RunStatus.OPEN,
                directive_version=ACTIVE_DIRECTIVE.version,
                directive_text=ACTIVE_DIRECTIVE.text,
                completed_at=datetime.now(timezone.utc),
            )
        self.assertIn("completed_at cannot be set while status is still OPEN", str(ctx.exception))

    def test_high_confidence_classified_as_high_uncertainty_raises(self):
        """ADR-08: score=0.75 must be STANDARD."""
        with self.assertRaises(ValidationError) as ctx:
            RunSession(
                ticker="AAPL",
                status=RunStatus.COMPLETE,
                directive_version=ACTIVE_DIRECTIVE.version,
                directive_text=ACTIVE_DIRECTIVE.text,
                run_confidence_score=0.75,
                confidence_classification=ConfidenceClassification.HIGH_UNCERTAINTY,
                completed_at=datetime.now(timezone.utc),
            )
        self.assertIn("inconsistent", str(ctx.exception))

    def test_low_confidence_classified_as_standard_raises(self):
        """ADR-08: score=0.2 must be HIGH_UNCERTAINTY."""
        with self.assertRaises(ValidationError) as ctx:
            RunSession(
                ticker="AAPL",
                status=RunStatus.COMPLETE,
                directive_version=ACTIVE_DIRECTIVE.version,
                directive_text=ACTIVE_DIRECTIVE.text,
                run_confidence_score=0.2,
                confidence_classification=ConfidenceClassification.STANDARD,
                completed_at=datetime.now(timezone.utc),
            )
        self.assertIn("inconsistent", str(ctx.exception))

    def test_ticker_too_long_raises(self):
        with self.assertRaises(ValidationError):
            RunSession(ticker="TOOLONGTICKER", directive_version="v1.0.0", directive_text="x")

    def test_empty_ticker_raises(self):
        with self.assertRaises(ValidationError):
            RunSession(ticker="", directive_version="v1.0.0", directive_text="x")

    def test_empty_directive_text_raises(self):
        with self.assertRaises(ValidationError):
            RunSession(ticker="AAPL", directive_version="v1.0.0", directive_text="   ")

    def test_immutable_after_construction(self):
        rs = make_run_session()
        with self.assertRaises((AttributeError, TypeError)):
            rs.status = RunStatus.COMPLETE  # type: ignore


# ─────────────────────────────────────────────
# SEC-01: thought_log leakage prevention
# ─────────────────────────────────────────────

class TestSEC01InvestorTierLeakage(unittest.TestCase):
    """
    SEC-01: investor-scoped serialisation must structurally exclude
    thought_log, raw_output, and llm_tokens.
    Not null-suppression — key must be absent from the output entirely.
    """

    def _make_ro_with_sensitive_data(self) -> ReasoningObject:
        return make_reasoning_object(
            thought_log="INTERNAL_THOUGHT_LOG — DO NOT EXPOSE",
            raw_output={"internal_key": "INTERNAL_RAW_OUTPUT"},
            llm_tokens={"tokens": ["INTERNAL_TOKEN_TRACE"]},
        )

    def test_investor_json_excludes_thought_log_key(self):
        ro = self._make_ro_with_sensitive_data()
        investor_json = ro.to_json(investor_scope=True)
        self.assertNotIn('"thought_log"', investor_json,
            "SEC-01 VIOLATION: thought_log key present in investor JSON")

    def test_investor_json_excludes_raw_output_key(self):
        ro = self._make_ro_with_sensitive_data()
        investor_json = ro.to_json(investor_scope=True)
        self.assertNotIn('"raw_output"', investor_json,
            "SEC-01 VIOLATION: raw_output key present in investor JSON")

    def test_investor_json_excludes_llm_tokens_key(self):
        ro = self._make_ro_with_sensitive_data()
        investor_json = ro.to_json(investor_scope=True)
        self.assertNotIn('"llm_tokens"', investor_json,
            "SEC-01 VIOLATION: llm_tokens key present in investor JSON")

    def test_investor_json_excludes_thought_log_content(self):
        """Belt-and-suspenders: sensitive string must not appear anywhere in output."""
        ro = self._make_ro_with_sensitive_data()
        investor_json = ro.to_json(investor_scope=True)
        self.assertNotIn("INTERNAL_THOUGHT_LOG", investor_json,
            "SEC-01 VIOLATION: thought_log content found in investor JSON")

    def test_investor_json_excludes_raw_output_content(self):
        ro = self._make_ro_with_sensitive_data()
        investor_json = ro.to_json(investor_scope=True)
        self.assertNotIn("INTERNAL_RAW_OUTPUT", investor_json,
            "SEC-01 VIOLATION: raw_output content found in investor JSON")

    def test_investor_json_excludes_llm_token_content(self):
        ro = self._make_ro_with_sensitive_data()
        investor_json = ro.to_json(investor_scope=True)
        self.assertNotIn("INTERNAL_TOKEN_TRACE", investor_json,
            "SEC-01 VIOLATION: llm_tokens content found in investor JSON")

    def test_investor_dict_excludes_all_sensitive_keys(self):
        ro = self._make_ro_with_sensitive_data()
        investor_dict = ro.to_dict(investor_scope=True)
        for key in ("thought_log", "raw_output", "llm_tokens"):
            self.assertNotIn(key, investor_dict,
                f"SEC-01 VIOLATION: '{key}' key present in investor dict")

    def test_auditor_json_includes_thought_log(self):
        """Auditor scope must retain all fields for full evidentiary record."""
        ro = self._make_ro_with_sensitive_data()
        auditor_json = ro.to_json(investor_scope=False)
        self.assertIn('"thought_log"', auditor_json)
        self.assertIn("INTERNAL_THOUGHT_LOG", auditor_json)

    def test_auditor_json_includes_raw_output(self):
        ro = self._make_ro_with_sensitive_data()
        auditor_json = ro.to_json(investor_scope=False)
        self.assertIn('"raw_output"', auditor_json)

    def test_investor_view_preserves_safe_fields(self):
        """Safe fields must survive the investor projection unchanged."""
        ro = make_reasoning_object(
            conclusion="Strong earnings. Buy recommendation.",
            confidence_score=0.78,
            agent_id=AgentID.EARNINGS,
        )
        investor_dict = ro.to_dict(investor_scope=True)
        self.assertEqual(investor_dict["conclusion"], "Strong earnings. Buy recommendation.")
        self.assertEqual(investor_dict["confidence_score"], round(0.78, 4))
        self.assertEqual(investor_dict["agent_id"], AgentID.EARNINGS.value)


# ─────────────────────────────────────────────
# Directive registry — ADR-05, SEC-04
# ─────────────────────────────────────────────

class TestDirective(unittest.TestCase):

    def test_active_directive_is_v1(self):
        d = get_active_directive()
        self.assertEqual(d.version, "v1.1.0")

    def test_directive_text_contains_thought_log_block(self):
        d = get_active_directive()
        self.assertIn("<thought_log>", d.text)

    def test_directive_text_contains_conclusion_block(self):
        d = get_active_directive()
        self.assertIn("<conclusion>", d.text)

    def test_directive_text_warns_on_structural_failure(self):
        """Agents must be told what happens when they deviate — ADR-01b."""
        d = get_active_directive()
        text_lower = d.text.lower()
        self.assertTrue(
            "retried" in text_lower or "validation" in text_lower,
            "Directive must warn agents about structural validation consequences"
        )

    def test_get_directive_by_version(self):
        d = get_directive("v1.0.0")
        self.assertEqual(d.version, "v1.0.0")
        self.assertIs(d, DIRECTIVE_V1_0_0)

    def test_get_unknown_directive_raises(self):
        with self.assertRaises(KeyError):
            get_directive("v99.0.0")

    def test_directive_is_immutable(self):
        """SEC-04: frozen dataclass — directive cannot be mutated at runtime."""
        d = get_active_directive()
        with self.assertRaises((AttributeError, TypeError)):
            d.text = "INJECTED MALICIOUS CONTENT"  # type: ignore

    def test_active_directive_retrievable_by_own_version(self):
        """Active directive version must exist in the registry."""
        active = get_active_directive()
        from_registry = get_directive(active.version)
        self.assertIs(active, from_registry)

    def test_directive_text_is_nonempty(self):
        d = get_active_directive()
        self.assertGreater(len(d.text.strip()), 100,
            "Directive text seems too short to be meaningful")


# ─────────────────────────────────────────────
# Serialisation round-trip
# ─────────────────────────────────────────────

class TestSerialisationRoundTrip(unittest.TestCase):

    def test_reasoning_object_to_json_is_valid_json(self):
        ro = make_reasoning_object()
        auditor_json = ro.to_json(investor_scope=False)
        parsed = json.loads(auditor_json)
        self.assertEqual(parsed["agent_id"], "financial")
        self.assertEqual(parsed["parse_status"], "SUCCESS")

    def test_run_session_to_dict_contains_ticker(self):
        rs = make_run_session(ticker="TSLA")
        d = rs.to_dict()
        self.assertEqual(d["ticker"], "TSLA")

    def test_run_session_to_dict_contains_directive_version(self):
        rs = make_run_session()
        d = rs.to_dict()
        self.assertEqual(d["directive_version"], "v1.1.0")

    def test_run_id_in_reasoning_object_matches_session(self):
        run_id = uuid.uuid4()
        rs = make_run_session(run_id=run_id)
        ro = make_reasoning_object(run_id=run_id)
        self.assertEqual(ro.run_id, rs.run_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)

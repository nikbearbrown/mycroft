"""
Phase 2 tests: structural parser + ADR-07 validation loop.
Provider-agnostic — no LLM package required.
MagicMock simulates call_agent_fn; _parse_response is tested directly.
"""

import unittest
import uuid
from unittest.mock import MagicMock

from parser import AgentResponse, StructuralParseError, _parse_response
from directive import get_active_directive
from middleware import (
    CORRECTIVE_DIRECTIVE_TEXT,
    HaltError,
    ValidationLoopResult,
    run_validation_loop,
)
from schemas import AgentID, ParseStatus


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _make_raw(thought: str = "Reasoning.", conclusion: str = "Analysis.") -> str:
    return f"<thought_log>\n  {thought}\n</thought_log>\n<conclusion>\n  {conclusion}\n</conclusion>"


def _make_response(thought: str = "Reasoning.", conclusion: str = "Analysis.") -> AgentResponse:
    return AgentResponse(thought_log=thought, conclusion=conclusion, raw_text=_make_raw(thought, conclusion))


def _make_parse_failure(raw: str = "Bad output") -> StructuralParseError:
    return StructuralParseError("parse failed", raw)


# ─────────────────────────────────────────────
# TestAgentParser — _parse_response unit tests
# ─────────────────────────────────────────────

class TestAgentParser(unittest.TestCase):

    def test_happy_path_returns_agent_response(self):
        result = _parse_response(_make_raw())
        self.assertIsInstance(result, AgentResponse)

    def test_happy_path_thought_log_extracted(self):
        result = _parse_response(_make_raw(thought="My internal reasoning."))
        self.assertEqual(result.thought_log, "My internal reasoning.")

    def test_happy_path_conclusion_extracted(self):
        result = _parse_response(_make_raw(conclusion="Strong buy."))
        self.assertEqual(result.conclusion, "Strong buy.")

    def test_happy_path_raw_text_preserved(self):
        raw = _make_raw()
        result = _parse_response(raw)
        self.assertEqual(result.raw_text, raw)

    def test_missing_thought_log_raises(self):
        raw = "<conclusion>\n  Analysis.\n</conclusion>"
        with self.assertRaises(StructuralParseError) as ctx:
            _parse_response(raw)
        self.assertIn("thought_log", str(ctx.exception))

    def test_missing_conclusion_raises(self):
        raw = "<thought_log>\n  Reasoning.\n</thought_log>"
        with self.assertRaises(StructuralParseError) as ctx:
            _parse_response(raw)
        self.assertIn("conclusion", str(ctx.exception))

    def test_missing_both_blocks_raises(self):
        raw = "Plain text with no XML blocks."
        with self.assertRaises(StructuralParseError) as ctx:
            _parse_response(raw)
        self.assertIn("both", str(ctx.exception))

    def test_text_before_blocks_raises(self):
        raw = "Preamble.\n" + _make_raw()
        with self.assertRaises(StructuralParseError) as ctx:
            _parse_response(raw)
        self.assertIn("outside", str(ctx.exception))

    def test_text_after_blocks_raises(self):
        raw = _make_raw() + "\nSome trailing text."
        with self.assertRaises(StructuralParseError) as ctx:
            _parse_response(raw)
        self.assertIn("outside", str(ctx.exception))

    def test_text_between_blocks_raises(self):
        raw = (
            "<thought_log>\n  Reasoning.\n</thought_log>\n"
            "Injected text.\n"
            "<conclusion>\n  Analysis.\n</conclusion>"
        )
        with self.assertRaises(StructuralParseError):
            _parse_response(raw)

    def test_structural_parse_error_carries_raw_response(self):
        raw = "No blocks here."
        with self.assertRaises(StructuralParseError) as ctx:
            _parse_response(raw)
        self.assertEqual(ctx.exception.raw_response, raw)

    def test_whitespace_only_between_blocks_is_valid(self):
        raw = "<thought_log>\n  Reasoning.\n</thought_log>\n\n\n<conclusion>\n  Analysis.\n</conclusion>"
        result = _parse_response(raw)
        self.assertIsNotNone(result)

    def test_multiline_content_extracted(self):
        raw = (
            "<thought_log>\n  Step 1.\n  Step 2.\n</thought_log>\n"
            "<conclusion>\n  Multi\n  line.\n</conclusion>"
        )
        result = _parse_response(raw)
        self.assertIn("Step 1", result.thought_log)
        self.assertIn("Step 2", result.thought_log)

    def test_empty_string_raises(self):
        with self.assertRaises(StructuralParseError):
            _parse_response("")


# ─────────────────────────────────────────────
# TestValidationLoop — ADR-07
# ─────────────────────────────────────────────

class TestValidationLoop(unittest.TestCase):

    def setUp(self):
        self.run_id = uuid.uuid4()

    # ── Happy path ────────────────────────────

    def test_happy_path_returns_validation_loop_result(self):
        call_fn = MagicMock(return_value=_make_response())
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertIsInstance(result, ValidationLoopResult)

    def test_happy_path_one_reasoning_object(self):
        call_fn = MagicMock(return_value=_make_response())
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertEqual(len(result.reasoning_objects), 1)

    def test_happy_path_attempt1_success(self):
        call_fn = MagicMock(return_value=_make_response())
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        obj = result.reasoning_objects[0]
        self.assertEqual(obj.parse_status, ParseStatus.SUCCESS)
        self.assertEqual(obj.attempt_number, 1)

    def test_happy_path_final_response_returned(self):
        response = _make_response(thought="Deep analysis.", conclusion="Buy.")
        call_fn = MagicMock(return_value=response)
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertIsNotNone(result.final_response)
        self.assertEqual(result.final_response.conclusion, "Buy.")

    def test_happy_path_thought_log_stored(self):
        call_fn = MagicMock(return_value=_make_response(thought="My reasoning."))
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertEqual(result.reasoning_objects[0].thought_log, "My reasoning.")

    def test_happy_path_conclusion_stored(self):
        call_fn = MagicMock(return_value=_make_response(conclusion="Strong buy."))
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertEqual(result.reasoning_objects[0].conclusion, "Strong buy.")

    # ── Fail then retry success ───────────────

    def test_fail_retry_success_two_objects(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_response()])
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertEqual(len(result.reasoning_objects), 2)

    def test_fail_attempt1_is_parse_failure(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure("garbage"), _make_response()])
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        obj1 = result.reasoning_objects[0]
        self.assertEqual(obj1.parse_status, ParseStatus.PARSE_FAILURE)
        self.assertEqual(obj1.attempt_number, 1)

    def test_retry_success_is_attempt2_success(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_response()])
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        obj2 = result.reasoning_objects[1]
        self.assertEqual(obj2.parse_status, ParseStatus.SUCCESS)
        self.assertEqual(obj2.attempt_number, 2)

    def test_fail_retry_success_final_response_not_none(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_response()])
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertIsNotNone(result.final_response)

    # ── Fail then retry fail → HALT ───────────

    def test_fail_retry_fail_raises_halt(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure("bad 1"), _make_parse_failure("bad 2")])
        with self.assertRaises(HaltError):
            run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)

    def test_halt_carries_two_objects(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_parse_failure()])
        with self.assertRaises(HaltError) as ctx:
            run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        self.assertEqual(len(ctx.exception.reasoning_objects), 2)

    def test_halt_object1_is_parse_failure(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_parse_failure()])
        with self.assertRaises(HaltError) as ctx:
            run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        obj1 = ctx.exception.reasoning_objects[0]
        self.assertEqual(obj1.parse_status, ParseStatus.PARSE_FAILURE)
        self.assertEqual(obj1.attempt_number, 1)

    def test_halt_object2_is_halt(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_parse_failure()])
        with self.assertRaises(HaltError) as ctx:
            run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        obj2 = ctx.exception.reasoning_objects[1]
        self.assertEqual(obj2.parse_status, ParseStatus.HALT)
        self.assertEqual(obj2.attempt_number, 2)

    def test_both_attempts_written_even_on_halt(self):
        """ADR-07: both records written regardless of outcome."""
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_parse_failure()])
        try:
            run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        except HaltError as exc:
            statuses = [o.parse_status for o in exc.reasoning_objects]
            self.assertIn(ParseStatus.PARSE_FAILURE, statuses)
            self.assertIn(ParseStatus.HALT, statuses)
        else:
            self.fail("Expected HaltError was not raised")

    # ── Directive behaviour ───────────────────

    def test_corrective_directive_differs_from_active(self):
        active = get_active_directive()
        self.assertNotEqual(CORRECTIVE_DIRECTIVE_TEXT, active.text)

    def test_retry_uses_corrective_directive(self):
        """Second call must receive a directive with CORRECTIVE_DIRECTIVE_TEXT."""
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_response()])
        run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        # call_agent_fn(ticker, context, directive) — directive is 3rd positional arg
        first_directive = call_fn.call_args_list[0][0][2]
        second_directive = call_fn.call_args_list[1][0][2]
        self.assertNotEqual(first_directive.text, second_directive.text)
        self.assertEqual(second_directive.text, CORRECTIVE_DIRECTIVE_TEXT)

    def test_first_attempt_uses_active_directive_by_default(self):
        call_fn = MagicMock(return_value=_make_response())
        run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        used_directive = call_fn.call_args_list[0][0][2]
        self.assertEqual(used_directive.text, get_active_directive().text)

    # ── Identity consistency ──────────────────

    def test_run_id_consistent_across_attempts(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_response()])
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.FINANCIAL, call_agent_fn=call_fn)
        for obj in result.reasoning_objects:
            self.assertEqual(obj.run_id, self.run_id)

    def test_agent_id_consistent_across_attempts(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_response()])
        result = run_validation_loop("AAPL", "ctx", self.run_id, AgentID.EARNINGS, call_agent_fn=call_fn)
        for obj in result.reasoning_objects:
            self.assertEqual(obj.agent_id, AgentID.EARNINGS)

    def test_halt_run_id_consistent(self):
        call_fn = MagicMock(side_effect=[_make_parse_failure(), _make_parse_failure()])
        with self.assertRaises(HaltError) as ctx:
            run_validation_loop("TSLA", "ctx", self.run_id, AgentID.PATENT, call_agent_fn=call_fn)
        for obj in ctx.exception.reasoning_objects:
            self.assertEqual(obj.run_id, self.run_id)


if __name__ == "__main__":
    unittest.main()

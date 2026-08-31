import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from assistant.orchestrator_assistant import run_assistant_pipeline
from assistant import orchestrator_assistant as orch_module
from helpers import assert_never_called, assert_called_once


def test_intake_incomplete_halts_before_retrieval_and_synthesis():
    """Halt 1: empty query. Retrieval and Synthesis must never be called —
    not just: the final status looks halted."""
    with patch.object(orch_module, "retrieve") as spy_retrieve, \
         patch.object(orch_module, "synthesize") as spy_synthesize:
        result = run_assistant_pipeline("")
        assert result == {"status": "intake_incomplete"}
        assert_never_called(spy_retrieve, "retrieve()")
        assert_never_called(spy_synthesize, "synthesize()")


def test_no_match_halts_before_synthesis():
    """Halt 2: no retrieval match. Synthesis must never be called."""
    with patch.object(orch_module, "synthesize") as spy_synthesize:
        result = run_assistant_pipeline("What is the price of tulip bulbs?")
        assert result["status"] == "no_match_found"
        assert_never_called(spy_synthesize, "synthesize()")


def test_clean_run_reaches_handoff():
    """Clean path: a real match runs end-to-end to a handed_off_to_advisor
    terminal state, proving the happy path works, not only the halts."""
    result = run_assistant_pipeline("What is the semiconductors outlook?")
    assert result["status"] == "handed_off_to_advisor"
    assert result["draft"] != ""
    assert len(result["sources"]) > 0


def test_no_send_or_finalize_function_exists_in_orchestrator():
    module_attrs = dir(orch_module)
    forbidden = ["send", "finalize", "submit", "dispatch"]
    for attr in module_attrs:
        for word in forbidden:
            assert word not in attr.lower(), (
                f"Found forbidden attribute '{attr}' in orchestrator_assistant.py"
            )


if __name__ == "__main__":
    test_intake_incomplete_halts_before_retrieval_and_synthesis()
    test_no_match_halts_before_synthesis()
    test_clean_run_reaches_handoff()
    test_no_send_or_finalize_function_exists_in_orchestrator()
    print("test_orchestrator_assistant.py: all tests passed")

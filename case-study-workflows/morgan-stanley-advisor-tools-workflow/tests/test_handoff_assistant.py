import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from assistant.handoff_assistant import handoff_to_advisor
from assistant.synthesis import SynthesisResult
from assistant import handoff_assistant as handoff_module


def test_handoff_no_match_returns_no_match_status():
    result = handoff_to_advisor(synthesis_result=None, match_found=False)
    assert result == {"status": "no_match_found"}


def test_handoff_clean_run_returns_draft():
    synthesis_result = SynthesisResult(draft_answer="Some draft.", sources_used=["DOC-001"])
    result = handoff_to_advisor(synthesis_result=synthesis_result, match_found=True)
    assert result["status"] == "handed_off_to_advisor"
    assert result["draft"] == "Some draft."
    assert result["sources"] == ["DOC-001"]


def test_no_send_or_finalize_function_exists_in_module():
    module_attrs = dir(handoff_module)
    forbidden = ["send", "finalize", "submit", "dispatch"]
    for attr in module_attrs:
        for word in forbidden:
            assert word not in attr.lower(), (
                f"Found forbidden attribute '{attr}' in handoff_assistant.py — "
                f"this pipeline must not define a send/finalize function."
            )


if __name__ == "__main__":
    test_handoff_no_match_returns_no_match_status()
    test_handoff_clean_run_returns_draft()
    test_no_send_or_finalize_function_exists_in_module()
    print("test_handoff_assistant.py: all tests passed")

import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from debrief.orchestrator_debrief import run_debrief_pipeline
from debrief import orchestrator_debrief as orch_module
from debrief.mock_transcript_source import get_transcript
from helpers import assert_never_called


def test_consent_not_given_halts_before_transcription():
    """Halt 1: no consent. Transcription must never be called."""
    fixture = get_transcript(with_action_items=True)
    with patch.object(orch_module, "transcribe") as spy_transcribe:
        result = run_debrief_pipeline(consent_flag=False, transcript_fixture=fixture)
        assert result == {"status": "consent_not_given"}
        assert_never_called(spy_transcribe, "transcribe()")


def test_clean_run_reaches_handoff_with_distinct_statuses():
    """Clean path: consent given, transcript has action items, runs
    end-to-end to a handed_off_to_advisor terminal state with the Finding-1
    status distinction intact."""
    fixture = get_transcript(with_action_items=True)
    result = run_debrief_pipeline(consent_flag=True, transcript_fixture=fixture)
    assert result["status"] == "handed_off_to_advisor"
    assert result["email_status"] == "awaiting_advisor_action"
    assert result["salesforce_note_status"] == "saved"
    assert result["email_status"] != result["salesforce_note_status"]


def test_clean_run_without_action_items():
    fixture = get_transcript(with_action_items=False)
    result = run_debrief_pipeline(consent_flag=True, transcript_fixture=fixture)
    assert result["status"] == "handed_off_to_advisor"
    assert "No outstanding action items" in result["draft_email"]


def test_no_send_finalize_or_write_function_exists_in_orchestrator():
    module_attrs = dir(orch_module)
    forbidden = ["send", "finalize", "submit", "dispatch", "write"]
    for attr in module_attrs:
        for word in forbidden:
            assert word not in attr.lower(), (
                f"Found forbidden attribute '{attr}' in orchestrator_debrief.py"
            )


if __name__ == "__main__":
    test_consent_not_given_halts_before_transcription()
    test_clean_run_reaches_handoff_with_distinct_statuses()
    test_clean_run_without_action_items()
    test_no_send_finalize_or_write_function_exists_in_orchestrator()
    print("test_orchestrator_debrief.py: all tests passed")

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from debrief.handoff_debrief import handoff_to_advisor
from debrief.post_meeting_draft import PostMeetingDraft
from debrief import handoff_debrief as handoff_module


def test_handoff_consent_not_given_returns_status():
    result = handoff_to_advisor(draft=None, consent_cleared=False)
    assert result == {"status": "consent_not_given"}


def test_handoff_clean_run_returns_full_draft_with_distinct_statuses():
    draft = PostMeetingDraft(
        summary="Summary text.",
        draft_email="Email text.",
        email_status="awaiting_advisor_action",
        salesforce_note="Note text.",
        salesforce_note_status="saved",
    )
    result = handoff_to_advisor(draft=draft, consent_cleared=True)
    assert result["status"] == "handed_off_to_advisor"
    assert result["email_status"] == "awaiting_advisor_action"
    assert result["salesforce_note_status"] == "saved"


def test_no_send_finalize_or_salesforce_write_function_exists_in_module():
    module_attrs = dir(handoff_module)
    forbidden = ["send", "finalize", "submit", "dispatch", "write"]
    for attr in module_attrs:
        for word in forbidden:
            assert word not in attr.lower(), (
                f"Found forbidden attribute '{attr}' in handoff_debrief.py — "
                f"no send/finalize/write function may exist in this pipeline."
            )


if __name__ == "__main__":
    test_handoff_consent_not_given_returns_status()
    test_handoff_clean_run_returns_full_draft_with_distinct_statuses()
    test_no_send_finalize_or_salesforce_write_function_exists_in_module()
    print("test_handoff_debrief.py: all tests passed")

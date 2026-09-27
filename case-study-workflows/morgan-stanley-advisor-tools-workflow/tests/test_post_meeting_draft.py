import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from debrief.live_notes import LiveNotesResult
from debrief.post_meeting_draft import draft_post_meeting_outputs


def test_draft_produces_summary_email_and_note():
    live_notes = LiveNotesResult(
        notes=["Client mentioned wanting to revisit allocation."],
        action_items=["I'll get you the Q3 report by Friday."],
    )
    draft = draft_post_meeting_outputs(live_notes)
    assert draft.summary != ""
    assert "Q3 report" in draft.draft_email
    assert draft.salesforce_note != ""


def test_email_and_salesforce_note_have_distinct_statuses():
    """Design Review Finding 1: the case study's own workflow table confirms
    the follow-up email as non-autonomous (advisor edits/sends at their
    discretion) and the Salesforce note-save as autonomous. This test proves
    that distinction is coded, not just documented — a future regression
    that flattens both back to one status would fail this test."""
    live_notes = LiveNotesResult(notes=["Some note."], action_items=[])
    draft = draft_post_meeting_outputs(live_notes)

    assert draft.email_status == "awaiting_advisor_action"
    assert draft.salesforce_note_status == "saved"
    assert draft.email_status != draft.salesforce_note_status


def test_draft_handles_no_notes_gracefully():
    live_notes = LiveNotesResult(notes=[], action_items=[])
    draft = draft_post_meeting_outputs(live_notes)
    assert draft.draft_email != ""
    assert draft.salesforce_note != ""


if __name__ == "__main__":
    test_draft_produces_summary_email_and_note()
    test_email_and_salesforce_note_have_distinct_statuses()
    test_draft_handles_no_notes_gracefully()
    print("test_post_meeting_draft.py: all tests passed")

"""
WHAT THIS FILE DOES: Pure function. Takes live-notes output and produces a
meeting summary, a draft follow-up email, and a Salesforce note — bundled
into one return object, since case study Section 4 Scenario B Step 3
describes these as one post-meeting drafting act, not three sequential
calls.

CONFIRMED / CONSTRUCTED, WITH A DELIBERATE STATUS DISTINCTION (Design Review
Finding 1): The case study's own workflow table states these two outputs
have DIFFERENT confirmed autonomy levels, not the same one:
  - The follow-up email is explicitly non-autonomous — "for an Advisor to
    edit and send at their discretion" (Section 3.2, confirmed, non-
    autonomous).
  - The Salesforce note-save is listed in the workflow table as
    "Autonomous (confirmed function)" — Debrief is confirmed to actually
    save this note, not merely draft one awaiting advisor action.

This module's return object reflects that distinction: `email_status` is
`"awaiting_advisor_action"`; `salesforce_note_status` is `"saved"`.

IMPORTANT LIMITATION, STATED PLAINLY (per the locked Finding 1 resolution,
option (b)): the `"saved"` status is asserted by this mock, not produced by
an executing write to any real or mock Salesforce API. No `salesforce_write`
module exists in this repository. This is a deliberate simplification for a
reference implementation illustrating the CONFIRMED distinction between the
two output types, not a system built to actually perform a Salesforce write.
If this codebase were extended toward production, that write would need to
become a real, separately-tested function — not a status string.
"""

from dataclasses import dataclass
from .live_notes import LiveNotesResult


@dataclass
class PostMeetingDraft:
    summary: str = ""
    draft_email: str = ""
    email_status: str = "awaiting_advisor_action"
    salesforce_note: str = ""
    salesforce_note_status: str = "saved"


def draft_post_meeting_outputs(live_notes_result: LiveNotesResult) -> PostMeetingDraft:
    summary = "; ".join(live_notes_result.notes) if live_notes_result.notes else ""

    if live_notes_result.action_items:
        draft_email = (
            "Following up on our conversation. Action items: "
            + "; ".join(live_notes_result.action_items)
        )
    else:
        draft_email = "Following up on our conversation. No outstanding action items."

    salesforce_note = f"Meeting summary: {summary}" if summary else "Meeting summary: (no notes captured)"

    return PostMeetingDraft(
        summary=summary,
        draft_email=draft_email,
        email_status="awaiting_advisor_action",
        salesforce_note=salesforce_note,
        salesforce_note_status="saved",
    )

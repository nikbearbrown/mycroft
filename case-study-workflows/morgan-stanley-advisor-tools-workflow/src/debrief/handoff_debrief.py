"""
WHAT THIS FILE DOES: Terminal stage of the Debrief pipeline. Takes whatever
post_meeting_draft.py produced and returns a status object representing the
handoff to the advisor. This file, and everything it imports, defines no
send-email function, no Salesforce-write function, and no finalize function
of any kind — matching the same structural absence as handoff_assistant.py.

CONFIRMED / CONSTRUCTED: CONSTRUCTED stub. Grounded in case study Section
3.2's explicit "for an Advisor to edit and send at their discretion"
language for the email. The Salesforce note's `"saved"` status passed
through here is NOT produced by a write function in this file or anywhere
in this repository — see post_meeting_draft.py's docstring for the full
statement of that limitation (Design Review Finding 1, resolution (b)).
"""

from .post_meeting_draft import PostMeetingDraft


def handoff_to_advisor(draft: PostMeetingDraft, consent_cleared: bool) -> dict:
    if not consent_cleared:
        return {"status": "consent_not_given"}

    return {
        "status": "handed_off_to_advisor",
        "summary": draft.summary,
        "draft_email": draft.draft_email,
        "email_status": draft.email_status,
        "salesforce_note": draft.salesforce_note,
        "salesforce_note_status": draft.salesforce_note_status,
    }

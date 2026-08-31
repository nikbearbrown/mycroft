"""
WHAT THIS FILE DOES: Runs the Debrief pipeline end to end in strict
sequence: Consent Gate -> [halt if not cleared] -> Transcription -> Live
Notes -> Post-Meeting Draft -> Handoff. The only module in this pipeline
with knowledge of the full sequence.

CONFIRMED / CONSTRUCTED: Sequencing mirrors the case study's disclosed shape
(consent -> transcribe -> live notes -> post-meeting draft -> advisor
review) without adding any step the case study does not support.

Halt map (two states):
  1. Consent not given   -> halts before Transcription
  2. Clean run           -> reaches Handoff

This module defines no send, finalize, or salesforce-write function, and
imports none.
"""

from .consent_gate import check_consent
from .transcription import transcribe
from .live_notes import extract_live_notes
from .post_meeting_draft import draft_post_meeting_outputs
from .handoff_debrief import handoff_to_advisor


def run_debrief_pipeline(consent_flag: bool, transcript_fixture: dict) -> dict:
    consent_result = check_consent(consent_flag)

    # Halt 1: consent
    if not consent_result.cleared:
        return handoff_to_advisor(draft=None, consent_cleared=False)

    transcription_result = transcribe(transcript_fixture)
    live_notes_result = extract_live_notes(transcription_result)
    draft = draft_post_meeting_outputs(live_notes_result)

    # Clean run
    return handoff_to_advisor(draft=draft, consent_cleared=True)

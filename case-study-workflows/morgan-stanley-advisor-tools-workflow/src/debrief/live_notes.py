"""
WHAT THIS FILE DOES: Generates notes and surfaces action items from a
transcribed meeting, standing in for Debrief's confirmed "live during the
meeting" note/action-item generation.

CONFIRMED / CONSTRUCTED: Note and action-item generation as a capability is
CONFIRMED — case study Section 4 Scenario B Step 2: "Debrief generates notes
on Rachel's behalf and surfaces action items as they come up in
conversation." The extraction mechanism here ([DEV]: keyword/phrase
pattern-matching for commitment or request language, e.g. "I'll get you...")
is CONSTRUCTED; Morgan Stanley discloses that action items are surfaced, not
how.

Kept deliberately distinct from post_meeting_draft.py: the case study
describes live notes/action items (during the meeting) and a post-meeting
summary + email + Salesforce note (after the meeting) as sequentially
separate outputs, not one combined output — this module only produces the
former.
"""

from dataclasses import dataclass, field
from .transcription import TranscriptionResult

COMMITMENT_PHRASES = ["i'll", "i will", "we'll get you", "will get you", "will follow up"]


@dataclass
class LiveNotesResult:
    notes: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)


def extract_live_notes(transcription_result: TranscriptionResult) -> LiveNotesResult:
    """[DEV] Naive pattern match: any speaker turn containing a commitment
    phrase is treated as both a note and an action item. All turns are
    treated as notes."""
    notes = list(transcription_result.speaker_turns)
    action_items = [
        turn for turn in transcription_result.speaker_turns
        if any(phrase in turn.lower() for phrase in COMMITMENT_PHRASES)
    ]

    return LiveNotesResult(notes=notes, action_items=action_items)

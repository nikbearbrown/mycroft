"""
WHAT THIS FILE DOES: Provides fabricated meeting-transcript fixtures for the
Debrief pipeline's Transcription and Live Notes stages to operate on.

CONFIRMED / CONSTRUCTED: CONSTRUCTED in full. No real Morgan Stanley client,
advisor, or meeting content appears anywhere in this file. The named advisor
("Rachel") and client ("Mr. Alvarez") in the case study's Section 4 are
themselves stated there to be the case study's own constructed illustration,
not real individuals — this module's fixtures are a further, separate
fabrication built only to exercise this pipeline's code paths in tests.

Two fixtures are provided: one containing clear commitment/request language
for the action-item extraction branch to find, one containing none, so that
branch has something real to prove against in both directions.
"""

TRANSCRIPT_WITH_ACTION_ITEMS = {
    "meeting_id": "MTG-001",
    "raw_text": (
        "Advisor: Thanks for making time today. You mentioned wanting to "
        "revisit the portfolio allocation before year end.\n"
        "Client: Right, and I'd also like to see the Q3 report before we "
        "meet again.\n"
        "Advisor: I'll get you the Q3 report by Friday. I'll also follow up "
        "with a written summary of the allocation options we discussed.\n"
        "Client: That works for me."
    ),
}

TRANSCRIPT_WITHOUT_ACTION_ITEMS = {
    "meeting_id": "MTG-002",
    "raw_text": (
        "Advisor: Good to see you. How was the trip?\n"
        "Client: It was great, thanks for asking.\n"
        "Advisor: Glad to hear it. Everything on your end looks stable, "
        "nothing needs attention right now.\n"
        "Client: Good to know. Talk soon."
    ),
}


def get_transcript(with_action_items: bool = True) -> dict:
    """Returns one of the two fabricated transcript fixtures."""
    return TRANSCRIPT_WITH_ACTION_ITEMS if with_action_items else TRANSCRIPT_WITHOUT_ACTION_ITEMS

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from debrief.transcription import transcribe
from debrief.live_notes import extract_live_notes
from debrief.mock_transcript_source import get_transcript


def test_extract_finds_action_items_when_present():
    fixture = get_transcript(with_action_items=True)
    transcription_result = transcribe(fixture)
    result = extract_live_notes(transcription_result)
    assert len(result.notes) > 0
    assert len(result.action_items) > 0
    assert any("Q3 report" in item for item in result.action_items)


def test_extract_finds_no_action_items_when_absent():
    fixture = get_transcript(with_action_items=False)
    transcription_result = transcribe(fixture)
    result = extract_live_notes(transcription_result)
    assert len(result.notes) > 0
    assert result.action_items == []


if __name__ == "__main__":
    test_extract_finds_action_items_when_present()
    test_extract_finds_no_action_items_when_absent()
    print("test_live_notes.py: all tests passed")

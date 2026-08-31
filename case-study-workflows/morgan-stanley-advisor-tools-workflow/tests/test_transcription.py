import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from debrief.transcription import transcribe
from debrief.mock_transcript_source import get_transcript


def test_transcribe_produces_speaker_turns():
    fixture = get_transcript(with_action_items=True)
    result = transcribe(fixture)
    assert len(result.speaker_turns) > 0
    assert result.raw_text == fixture["raw_text"]


def test_transcribe_empty_fixture_returns_empty_turns():
    result = transcribe({"raw_text": ""})
    assert result.speaker_turns == []


if __name__ == "__main__":
    test_transcribe_produces_speaker_turns()
    test_transcribe_empty_fixture_returns_empty_turns()
    print("test_transcription.py: all tests passed")

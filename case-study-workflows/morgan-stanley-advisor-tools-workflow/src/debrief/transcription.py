"""
WHAT THIS FILE DOES: Mock stand-in for Whisper-based transcription. Converts
a raw meeting-transcript fixture into a structured representation. Only
reachable if consent_gate.py has cleared.

CONFIRMED / CONSTRUCTED: Whisper-based transcription is CONFIRMED (case
study Section 3.1 — Debrief is "built on GPT-4 + Whisper (transcription)").
This module's internal structure ([DEV]: naive split into speaker turns by
newline) is CONSTRUCTED and makes no claim to approximate real Whisper
transcription quality or accuracy.
"""

from dataclasses import dataclass, field


@dataclass
class TranscriptionResult:
    speaker_turns: list[str] = field(default_factory=list)
    raw_text: str = ""


def transcribe(transcript_fixture: dict) -> TranscriptionResult:
    """[DEV] Naive mock: splits the fixture's raw_text on newlines into
    speaker turns. No real audio, no real Whisper model involved."""
    raw_text = transcript_fixture.get("raw_text", "")
    speaker_turns = [line.strip() for line in raw_text.split("\n") if line.strip()]

    return TranscriptionResult(speaker_turns=speaker_turns, raw_text=raw_text)

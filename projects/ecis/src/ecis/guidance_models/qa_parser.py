"""Pair analyst questions with management answers in the Q&A section."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ecis.config.settings import settings
from ecis.extraction.speaker_roles import classify_speaker

_SECTION_RE = re.compile(r"^\[SECTION:\s*(\w+)\]$", re.I)
_SPEAKER_RE = re.compile(r"^\[SPEAKER:\s*(.+)\]$", re.I)
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_QUESTION_CUES = re.compile(
    r"(?i)\b(?:can\s+you|could\s+you|what(?:'s|\s+is|\s+are)|how\s+(?:do|did|will|should)|"
    r"why\s+(?:did|is|are|was)|would\s+you|please\s+(?:talk|walk|comment)|walk\s+us)\b"
)


def _turns(text: str) -> list[dict[str, Any]]:
    section = "prepared_remarks"
    speaker = ""
    buf: list[str] = []
    turns: list[dict[str, Any]] = []
    offset = 0

    def flush(end: int) -> None:
        body = "\n".join(buf).strip()
        if not body:
            return
        start = max(0, end - len(body))
        turns.append({
            "section_label": section,
            "speaker": speaker,
            "speaker_role": classify_speaker(speaker),
            "text": body,
            "char_start": start,
            "char_end": end,
        })

    for line in text.split("\n"):
        offset += len(line) + 1
        sec = _SECTION_RE.match(line.strip())
        if sec:
            flush(offset)
            buf = []
            section = sec.group(1).lower()
            continue
        spk = _SPEAKER_RE.match(line.strip())
        if spk:
            flush(offset)
            buf = []
            speaker = spk.group(1).strip()
            continue
        buf.append(line)
    flush(offset)
    return turns


def _is_question(turn: dict[str, Any]) -> bool:
    if turn["speaker_role"] == "analyst":
        return True
    text = turn.get("text") or ""
    return "?" in text or bool(_QUESTION_CUES.search(text))


def _is_management(turn: dict[str, Any]) -> bool:
    return turn["speaker_role"] in {"ceo", "cfo", "coo", "ir", "unknown"}


def parse_qa(
    text: str,
    *,
    ticker: str = "",
    transcript_date: str = "",
) -> list[dict[str, Any]]:
    """Return structured question-answer pairs from a normalised transcript."""
    qa_turns = [t for t in _turns(text) if t["section_label"] in {"qa", "q_and_a", "q&a"}]
    if not qa_turns:
        qa_turns = [t for t in _turns(text) if _is_question(t) or t["speaker_role"] == "analyst"]

    pairs: list[dict[str, Any]] = []
    i = 0
    idx = 0
    while i < len(qa_turns):
        turn = qa_turns[i]
        if not _is_question(turn):
            i += 1
            continue
        question_parts = [turn["text"]]
        q_speakers = [turn["speaker"]]
        start = turn["char_start"]
        j = i + 1
        while j < len(qa_turns) and _is_question(qa_turns[j]) and not _is_management(qa_turns[j]):
            question_parts.append(qa_turns[j]["text"])
            q_speakers.append(qa_turns[j]["speaker"])
            j += 1
        answers: list[str] = []
        a_speakers: list[str] = []
        a_roles: list[str] = []
        end = turn["char_end"]
        while j < len(qa_turns) and _is_management(qa_turns[j]) and not _is_question(qa_turns[j]):
            answers.append(qa_turns[j]["text"])
            a_speakers.append(qa_turns[j]["speaker"])
            a_roles.append(qa_turns[j]["speaker_role"])
            end = qa_turns[j]["char_end"]
            j += 1
        if not answers and j < len(qa_turns) and _is_management(qa_turns[j]):
            answers.append(qa_turns[j]["text"])
            a_speakers.append(qa_turns[j]["speaker"])
            a_roles.append(qa_turns[j]["speaker_role"])
            end = qa_turns[j]["char_end"]
            j += 1
        idx += 1
        pairs.append({
            "ticker": (ticker or "").upper(),
            "transcript_date": transcript_date,
            "pair_index": idx,
            "question": " ".join(question_parts).strip(),
            "answer": " ".join(answers).strip(),
            "question_speaker": q_speakers[0] if q_speakers else "",
            "answer_speaker": a_speakers[0] if a_speakers else "",
            "answer_role": a_roles[0] if a_roles else "unknown",
            "follow_up": len(question_parts) > 1,
            "char_start": start,
            "char_end": end,
        })
        i = j if j > i else i + 1
    return pairs


def _date_from_name(path: Path) -> str:
    m = _DATE_RE.search(path.name)
    return m.group(1) if m else ""


def iter_normalised_transcripts(ticker: str | None = None) -> list[tuple[str, str, Path]]:
    root = settings.normalised_dir
    if not root.exists():
        return []
    out: list[tuple[str, str, Path]] = []
    targets = [root / ticker.upper()] if ticker else [p for p in root.iterdir() if p.is_dir()]
    for folder in targets:
        if not folder.exists():
            continue
        tkr = folder.name.upper()
        for path in sorted(folder.glob("*.txt")):
            out.append((tkr, _date_from_name(path), path))
    return out


def parse_qa_corpus(ticker: str | None = None) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for tkr, day, path in iter_normalised_transcripts(ticker):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        pairs.extend(parse_qa(text, ticker=tkr, transcript_date=day))
    return pairs

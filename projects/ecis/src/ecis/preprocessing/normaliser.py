"""Normalise cleaned transcripts: identify sections, normalise speakers, add inline markers."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from ecis.config.settings import settings
from ecis.preprocessing.boilerplate import strip_boilerplate

logger = logging.getLogger(__name__)

_PREPARED_REMARKS_PATTERNS = [
    re.compile(r"(?i)^\s*(?:prepared\s+remarks|opening\s+remarks|presentation)\s*$", re.MULTILINE),
    re.compile(r"(?i)(?:good\s+(?:morning|afternoon|evening).*?(?:welcome|thank\s+you\s+for\s+joining))", re.MULTILINE),
]

_QA_PATTERNS = [
    re.compile(r"(?i)^\s*(?:question[- ]and[- ]answer|q\s*&\s*a|q&a\s+session)\s*$", re.MULTILINE),
    re.compile(r"(?i)(?:we\s+(?:will|can)\s+now\s+(?:open|take|begin).*?questions)", re.MULTILINE),
    re.compile(r"(?i)(?:operator|moderator).*?(?:first\s+question|open\s+the\s+line)", re.MULTILINE),
]

_SPEAKER_PATTERN = re.compile(
    r"^([A-Z][A-Za-z\.\-\' ]{2,50})"
    r"(?:\s*[-–—,]\s*"
    r"((?:CEO|CFO|COO|CTO|President|Chairman|Director|Analyst|Operator|"
    r"Chief\s+\w+\s+Officer|Vice\s+President|SVP|EVP|Managing\s+Director|"
    r"Senior\s+Vice\s+President|Executive\s+Vice\s+President)[\w\s,]*))?"
    r"\s*[:\-–—]?\s*$",
    re.MULTILINE | re.IGNORECASE,
)

_GENERIC_SPEAKERS = {"operator", "moderator", "unidentified analyst", "unknown speaker"}


def _detect_qa_start(text: str) -> int | None:
    """Return the character position where the Q&A section begins, or None."""
    for pattern in _QA_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.start()

    midpoint = len(text) // 2
    second_half = text[midpoint:]
    lines = second_half.split("\n")
    question_density = sum(1 for line in lines if "?" in line) / max(len(lines), 1)
    if question_density > 0.15:
        return midpoint

    return None


def _normalise_speaker(raw_name: str) -> str:
    """Normalise a speaker name to a consistent format."""
    name = raw_name.strip().rstrip(":-–—").strip()
    name = re.sub(r"\s+", " ", name)
    if name.lower() in _GENERIC_SPEAKERS:
        return name.title()
    return name


def _extract_speakers(text: str) -> list[tuple[int, str, str]]:
    """Find speaker labels in the text.

    Returns list of (char_position, canonical_name, raw_match).
    """
    speakers = []
    for m in _SPEAKER_PATTERN.finditer(text):
        raw_name = m.group(1)
        title = m.group(2) or ""
        canonical = _normalise_speaker(raw_name)
        if title:
            canonical = f"{canonical}, {title.strip()}"
        speakers.append((m.start(), canonical, m.group(0)))
    return speakers


def normalise_transcript(cleaned_text: str) -> str:
    """Add section and speaker markers to a cleaned transcript."""
    cleaned_text = strip_boilerplate(cleaned_text)
    output_lines: list[str] = []

    qa_start = _detect_qa_start(cleaned_text)

    if qa_start is not None:
        prepared = cleaned_text[:qa_start]
        qa = cleaned_text[qa_start:]

        output_lines.append("[SECTION: prepared_remarks]")
        output_lines.append("")
        output_lines.extend(_add_speaker_markers(prepared).split("\n"))
        output_lines.append("")
        output_lines.append("[SECTION: qa]")
        output_lines.append("")
        output_lines.extend(_add_speaker_markers(qa).split("\n"))
    else:
        output_lines.append("[SECTION: prepared_remarks]")
        output_lines.append("")
        output_lines.extend(_add_speaker_markers(cleaned_text).split("\n"))

    return "\n".join(output_lines)


def _add_speaker_markers(text: str) -> str:
    """Insert [SPEAKER: ...] markers before speaker paragraphs."""
    speakers = _extract_speakers(text)
    if not speakers:
        return text

    result = text
    for pos, canonical, raw_match in reversed(speakers):
        marker = f"[SPEAKER: {canonical}]"
        result = result[:pos] + marker + "\n" + result[pos + len(raw_match):]

    return result


def normalise_file(cleaned_path: Path, ticker: str) -> Path | None:
    """Normalise a single cleaned file and write to the normalised directory."""
    text = cleaned_path.read_text(encoding="utf-8")
    if not text.strip():
        logger.warning("Empty file: %s", cleaned_path)
        return None

    normalised = normalise_transcript(text)

    out_dir = settings.normalised_dir / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / cleaned_path.name
    out_path.write_text(normalised, encoding="utf-8")
    logger.info("Normalised %s → %s", cleaned_path, out_path)
    return out_path


def normalise_all(ticker: str) -> list[Path]:
    """Normalise all cleaned files for a ticker."""
    settings.ensure_dirs()
    cleaned_dir = settings.cleaned_dir / ticker
    if not cleaned_dir.exists():
        logger.warning("No cleaned files for %s", ticker)
        return []

    output_paths: list[Path] = []
    for cleaned_path in sorted(cleaned_dir.glob("*.txt")):
        out = normalise_file(cleaned_path, ticker)
        if out:
            output_paths.append(out)
    return output_paths

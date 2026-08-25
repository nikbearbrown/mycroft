from __future__ import annotations

import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import Any

from ecis.config.settings import settings

logger = logging.getLogger(__name__)

_tokenizer = None


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer
        _tokenizer = AutoTokenizer.from_pretrained(settings.finbert_model_name)
    return _tokenizer


def _token_count(text: str) -> int:
    return len(_get_tokenizer().encode(text, add_special_tokens=False))


def _parse_sections(normalised_text: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_section = "prepared_remarks"
    current_speaker = ""
    current_lines: list[str] = []

    for line in normalised_text.split("\n"):
        section_match = re.match(r"^\[SECTION:\s*(\w+)\]$", line)
        if section_match:
            if current_lines:
                sections.append({
                    "section_label": current_section,
                    "speaker": current_speaker,
                    "text": "\n".join(current_lines).strip(),
                })
                current_lines = []
            current_section = section_match.group(1)
            continue

        speaker_match = re.match(r"^\[SPEAKER:\s*(.+)\]$", line)
        if speaker_match:
            if current_lines:
                sections.append({
                    "section_label": current_section,
                    "speaker": current_speaker,
                    "text": "\n".join(current_lines).strip(),
                })
                current_lines = []
            current_speaker = speaker_match.group(1)
            continue

        current_lines.append(line)

    if current_lines:
        sections.append({
            "section_label": current_section,
            "speaker": current_speaker,
            "text": "\n".join(current_lines).strip(),
        })

    return [s for s in sections if s["text"]]


def chunk_text(
    text: str,
    *,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[tuple[str, int, int]]:
    """Split text into overlapping chunks by token count.

    Returns list of (chunk_text, char_start, char_end).
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size_tokens
    if overlap is None:
        overlap = settings.chunk_overlap_tokens

    tokenizer = _get_tokenizer()
    encoding = tokenizer.encode(text, add_special_tokens=False)

    if len(encoding) <= chunk_size:
        return [(text, 0, len(text))]

    chunks: list[tuple[str, int, int]] = []
    step = chunk_size - overlap

    for start_tok in range(0, len(encoding), step):
        end_tok = min(start_tok + chunk_size, len(encoding))
        token_ids = encoding[start_tok:end_tok]
        chunk_str = tokenizer.decode(token_ids, skip_special_tokens=True)

        char_start = text.find(chunk_str[:40])
        if char_start == -1:
            char_start = 0
        char_end = char_start + len(chunk_str)

        chunks.append((chunk_str, char_start, min(char_end, len(text))))

        if end_tok >= len(encoding):
            break

    return chunks


def chunk_transcript(
    normalised_path: Path,
    ticker: str,
    transcript_date: date,
) -> list[dict[str, Any]]:
    """Chunk a normalised transcript into metadata-tagged chunks.

    Returns list of chunk dicts ready for embedding and storage.
    """
    text = normalised_path.read_text(encoding="utf-8")
    sections = _parse_sections(text)

    all_chunks: list[dict[str, Any]] = []
    chunk_index = 0

    for section in sections:
        raw_chunks = chunk_text(section["text"])

        for chunk_text_str, char_start, char_end in raw_chunks:
            if _token_count(chunk_text_str) > 512:
                logger.warning(
                    "Chunk %d for %s exceeds 512 tokens (%d), may be truncated by FinBERT",
                    chunk_index, ticker, _token_count(chunk_text_str),
                )

            all_chunks.append({
                "chunk_index": chunk_index,
                "text": chunk_text_str,
                "source_file": str(normalised_path),
                "ticker": ticker,
                "transcript_date": str(transcript_date),
                "section_label": section["section_label"],
                "speaker": section["speaker"],
                "char_start": char_start,
                "char_end": char_end,
            })
            chunk_index += 1

    return all_chunks


def chunk_and_save(
    normalised_path: Path,
    ticker: str,
    transcript_date: date,
) -> Path:
    """Chunk a transcript and write the result to JSON."""
    chunks = chunk_transcript(normalised_path, ticker, transcript_date)

    out_dir = settings.chunks_dir / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{normalised_path.stem}_chunks.json"
    out_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    logger.info("Chunked %s → %d chunks → %s", normalised_path, len(chunks), out_path)
    return out_path


def chunk_all(ticker: str, transcript_date: date | None = None) -> list[Path]:
    """Chunk all normalised files for a ticker."""
    settings.ensure_dirs()
    norm_dir = settings.normalised_dir / ticker
    if not norm_dir.exists():
        logger.warning("No normalised files for %s", ticker)
        return []

    if transcript_date is None:
        from datetime import date as d
        transcript_date = d.today()

    output_paths: list[Path] = []
    for norm_path in sorted(norm_dir.glob("*.txt")):
        stem = norm_path.stem
        try:
            file_date = date.fromisoformat(stem)
        except ValueError:
            file_date = transcript_date

        out = chunk_and_save(norm_path, ticker, file_date)
        output_paths.append(out)

    return output_paths

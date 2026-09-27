"""Clean raw EDGAR HTML and FMP JSON files into plain text."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup

from ecis.config.settings import settings
from ecis.preprocessing.boilerplate import strip_boilerplate

logger = logging.getLogger(__name__)


def clean_edgar_html(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")

    for tag in soup.find_all(["script", "style", "meta", "link"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = strip_boilerplate(text)
    text = _normalise_whitespace(text)
    return text.strip()


def clean_fmp_json(json_text: str) -> str:
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in FMP file")
        return ""

    if isinstance(data, list):
        parts = []
        for item in data:
            content = item.get("content", "")
            if content:
                parts.append(content)
        text = "\n\n".join(parts)
    elif isinstance(data, dict):
        text = data.get("content", "") or data.get("transcript", "")
    text = _normalise_whitespace(text)
    return strip_boilerplate(text).strip()


def _normalise_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines)


def clean_file(raw_path: Path) -> str:
    content = raw_path.read_text(encoding="utf-8", errors="replace")
    if raw_path.suffix in (".html", ".htm"):
        return clean_edgar_html(content)
    elif raw_path.suffix == ".json":
        return clean_fmp_json(content)
    else:
        logger.warning("Unknown file type: %s", raw_path.suffix)
        return _normalise_whitespace(content)


def clean_all(ticker: str) -> list[Path]:
    settings.ensure_dirs()
    output_paths: list[Path] = []

    for source_dir in (settings.raw_edgar_dir / ticker, settings.raw_fmp_dir / ticker):
        if not source_dir.exists():
            continue
        for raw_path in sorted(source_dir.iterdir()):
            if raw_path.is_dir():
                continue

            cleaned_text = clean_file(raw_path)
            if not cleaned_text:
                logger.warning("Empty output for %s", raw_path)
                continue

            out_dir = settings.cleaned_dir / ticker
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{raw_path.stem}.txt"
            out_path.write_text(cleaned_text, encoding="utf-8")
            output_paths.append(out_path)
            logger.info("Cleaned %s → %s", raw_path, out_path)

    return output_paths

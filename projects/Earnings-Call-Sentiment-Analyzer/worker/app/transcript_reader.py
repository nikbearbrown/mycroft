from pathlib import Path

import pdfplumber


def read_transcript(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        with pdfplumber.open(path) as document:
            pages = [page.extract_text() or "" for page in document.pages]
        text = "\n\n".join(pages).strip()
        if not text:
            raise ValueError("The PDF does not contain extractable text")
        return text
    raise ValueError("Only .txt and .pdf transcript files are supported")

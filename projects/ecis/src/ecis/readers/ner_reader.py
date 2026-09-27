"""Named entity reader using spaCy for financial entity extraction."""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

_nlp = None

_METRIC_PATTERNS = [
    re.compile(r"\b(?:revenue|revenues)\b", re.IGNORECASE),
    re.compile(r"\b(?:earnings?\s+per\s+share|EPS)\b", re.IGNORECASE),
    re.compile(r"\b(?:operating\s+(?:income|margin|profit))\b", re.IGNORECASE),
    re.compile(r"\b(?:gross\s+(?:margin|profit))\b", re.IGNORECASE),
    re.compile(r"\b(?:net\s+(?:income|profit|loss))\b", re.IGNORECASE),
    re.compile(r"\b(?:free\s+cash\s+flow|FCF)\b", re.IGNORECASE),
    re.compile(r"\b(?:EBITDA|EBIT)\b"),
    re.compile(r"\b(?:capital\s+expenditure|capex|CapEx)\b", re.IGNORECASE),
    re.compile(r"\b(?:operating\s+expenses?|opex|OpEx)\b", re.IGNORECASE),
    re.compile(r"\b(?:guidance|outlook|forecast)\b", re.IGNORECASE),
    re.compile(r"\b(?:subscriber|user|customer)\s+(?:count|growth|adds?|base)\b", re.IGNORECASE),
    re.compile(r"\b(?:average\s+revenue\s+per\s+user|ARPU)\b", re.IGNORECASE),
    re.compile(r"\b(?:same[- ]store\s+sales|comparable\s+sales|comp\s+sales)\b", re.IGNORECASE),
]

_MONEY_PATTERN = re.compile(
    r"\$\s*[\d,]+(?:\.\d+)?\s*(?:billion|million|thousand|B|M|K|bn|mn)?\b"
    r"|\b[\d,]+(?:\.\d+)?\s*(?:billion|million|thousand)\s+dollars\b",
    re.IGNORECASE,
)

_PERCENT_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?(?:\s*%|\s+percent(?:age)?(?:\s+points?)?)\b",
    re.IGNORECASE,
)


def _load_nlp():
    global _nlp
    if _nlp is not None:
        return _nlp

    import spacy

    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("en_core_web_sm not found, downloading...")
        from spacy.cli import download
        download("en_core_web_sm")
        _nlp = spacy.load("en_core_web_sm")

    logger.info("spaCy model loaded")
    return _nlp


def read_chunk(chunk_text: str) -> dict[str, list[str]]:
    nlp = _load_nlp()
    doc = nlp(chunk_text)

    entities: dict[str, list[str]] = {
        "companies": [],
        "money": [],
        "percentages": [],
        "dates": [],
        "metrics": [],
    }

    for ent in doc.ents:
        text = ent.text.strip()
        if not text:
            continue
        if ent.label_ == "ORG":
            entities["companies"].append(text)
        elif ent.label_ == "MONEY":
            entities["money"].append(text)
        elif ent.label_ == "PERCENT":
            entities["percentages"].append(text)
        elif ent.label_ in ("DATE", "TIME"):
            entities["dates"].append(text)

    # Supplement with regex patterns for amounts spaCy misses
    for m in _MONEY_PATTERN.finditer(chunk_text):
        val = m.group().strip()
        if val not in entities["money"]:
            entities["money"].append(val)

    for m in _PERCENT_PATTERN.finditer(chunk_text):
        val = m.group().strip()
        if val not in entities["percentages"]:
            entities["percentages"].append(val)

    for pattern in _METRIC_PATTERNS:
        for m in pattern.finditer(chunk_text):
            val = m.group().strip()
            if val not in entities["metrics"]:
                entities["metrics"].append(val)

    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))

    return entities


def read_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for chunk in chunks:
        ents = read_chunk(chunk["text"])
        results.append({
            "chunk_index": chunk.get("chunk_index", 0),
            "entities": ents,
        })
    return results

"""Keyword-based guidance direction reader using the taxonomy YAML."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

from ecis.config.settings import settings
from ecis.schemas.signal import GuidanceDirection

logger = logging.getLogger(__name__)

_taxonomy: dict[str, list[re.Pattern]] | None = None


def _load_taxonomy() -> dict[str, list[re.Pattern]]:
    global _taxonomy
    if _taxonomy is not None:
        return _taxonomy

    taxonomy_path = settings.project_root / "config" / "taxonomy.yaml"
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    _taxonomy = {}
    for direction, phrases in raw.items():
        patterns = []
        for phrase in phrases:
            escaped = re.escape(phrase)
            pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
            patterns.append(pattern)
        _taxonomy[direction] = patterns

    total = sum(len(p) for p in _taxonomy.values())
    logger.info("Loaded taxonomy: %d phrases across %d directions", total, len(_taxonomy))
    return _taxonomy


def read_chunk(chunk_text: str) -> dict[str, Any]:
    taxonomy = _load_taxonomy()

    matches_by_direction: dict[str, list[tuple[int, int, str]]] = {}

    for direction, patterns in taxonomy.items():
        for pattern in patterns:
            for m in pattern.finditer(chunk_text):
                matches_by_direction.setdefault(direction, []).append(
                    (m.start(), m.end(), m.group())
                )

    if not matches_by_direction:
        return {
            "matched": False,
            "direction": None,
            "phrases": [],
            "confidence": 0.0,
            "match_positions": [],
        }

    best_direction = max(matches_by_direction, key=lambda d: len(matches_by_direction[d]))
    best_matches = matches_by_direction[best_direction]
    all_phrases = [m[2] for m in best_matches]

    return {
        "matched": True,
        "direction": best_direction,
        "phrases": all_phrases,
        "confidence": 1.0,
        "match_positions": best_matches,
    }


def read_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for chunk in chunks:
        result = read_chunk(chunk["text"])
        result["chunk_index"] = chunk.get("chunk_index", 0)
        results.append(result)
    return results

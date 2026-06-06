"""Purpose: Parse ArXiv RSS text into raw_intelligence records.
Input: JSON object with raw feed text from data/raw/aeo-workflow-a/.
Output: Parsed ArXiv records for data/verified/aeo-workflow-a/.
Side effects: Optional file write only.
Idempotent: Yes; parsing is deterministic.
Recipe: recipes/workflow-a-extract-store-raw-data.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_raw_intelligence_shared import emit, load_input, parse_rss_or_atom


def parse_arxiv(payload: dict[str, Any] | str) -> list[dict[str, Any]]:
    """Purpose: Parse ArXiv RSS text into raw_intelligence records.
    Input: JSON object with raw feed text.
    Output: Parsed ArXiv records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output except pulled timestamp.
    Recipe: recipes/workflow-a-extract-store-raw-data.md
    """
    raw = payload.get("raw", "") if isinstance(payload, dict) else payload
    return parse_rss_or_atom(str(raw), "ArXiv", "research", "ai")


if __name__ == "__main__":
    sample = {"raw": "<rss><channel><item><title>AI paper</title><link>https://arxiv.org/abs/1</link><description>Abstract</description></item></channel></rss>"}
    payload = load_input(sample)
    emit(parse_arxiv(payload["data"]), payload["output"])

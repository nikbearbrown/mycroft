"""Purpose: Parse TechCrunch RSS text into raw_intelligence records.
Input: JSON object with raw feed text from data/raw/aeo-workflow-a/.
Output: Parsed TechCrunch records for data/verified/aeo-workflow-a/.
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


def parse_techcrunch(payload: dict[str, Any] | str) -> list[dict[str, Any]]:
    """Purpose: Parse TechCrunch RSS text into raw_intelligence records.
    Input: JSON object with raw feed text.
    Output: Parsed TechCrunch records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output except pulled timestamp.
    Recipe: recipes/workflow-a-extract-store-raw-data.md
    """
    raw = payload.get("raw", "") if isinstance(payload, dict) else payload
    return parse_rss_or_atom(str(raw), "TechCrunch", "news", "ai")


if __name__ == "__main__":
    sample = {"raw": "<rss><channel><item><title>AI news</title><link>https://example.com/a</link><description>Body</description></item></channel></rss>"}
    payload = load_input(sample)
    emit(parse_techcrunch(payload["data"]), payload["output"])

"""Purpose: Parse Reddit listing JSON into raw_intelligence records.
Input: JSON object with raw Reddit listing from data/raw/aeo-workflow-a/.
Output: Parsed Reddit records for data/verified/aeo-workflow-a/.
Side effects: Optional file write only.
Idempotent: Yes; parsing is deterministic.
Recipe: recipes/workflow-a-extract-store-raw-data.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_raw_intelligence_shared import emit, load_input, parse_reddit_json


def parse_reddit(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Purpose: Parse Reddit listing JSON into raw_intelligence records.
    Input: JSON object with raw Reddit listing.
    Output: Parsed Reddit records.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output except pulled timestamp.
    Recipe: recipes/workflow-a-extract-store-raw-data.md
    """
    raw = payload.get("raw", payload) if isinstance(payload, dict) else {}
    return parse_reddit_json(raw, "ai")


if __name__ == "__main__":
    sample = {"raw": {"data": {"children": [{"data": {"title": "AI discussion", "url": "https://reddit.com/r/a", "created_utc": 1780704000}}]}}}
    payload = load_input(sample)
    emit(parse_reddit(payload["data"]), payload["output"])

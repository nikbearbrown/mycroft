"""Purpose: Parse Google News RSS into article records.
Input: Raw RSS text payload from data/raw/mycroft-news-intelligence-agent/.
Output: Normalized article records.
Side effects: Optional file write only.
Idempotent: Yes; parsing is deterministic.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import emit, load_input, parse_google_rss
def parse_mycroft_google_rss(payload: dict[str, Any] | str) -> list[dict[str, Any]]:
    raw = payload.get("raw", "") if isinstance(payload, dict) else payload
    return parse_google_rss(str(raw))
if __name__ == "__main__":
    sample = {"raw":"<rss><channel><item><title>NVIDIA shares fall</title><link>u</link><description>Risk</description></item></channel></rss>"}
    payload = load_input(sample)
    emit(parse_mycroft_google_rss(payload["data"]), payload["output"])

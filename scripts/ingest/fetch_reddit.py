"""Purpose: Fetch Reddit AI community listing JSON.
Input: Optional JSON object with url; default is the n8n Reddit listing URL.
Output: Raw JSON metadata for data/raw/aeo-workflow-a/.
Side effects: Performs one HTTP GET; optionally writes JSON to the supplied output path.
Idempotent: Yes for unchanged listing content; it does not mutate remote state.
Recipe: recipes/workflow-a-extract-store-raw-data.md
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_raw_intelligence_shared import emit, load_input


def fetch_reddit(config: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
    """Purpose: Fetch Reddit AI community listing JSON.
    Input: Optional JSON object with url.
    Output: Raw JSON metadata.
    Side effects: Performs one HTTP GET.
    Idempotent: Yes for unchanged listing content.
    Recipe: recipes/workflow-a-extract-store-raw-data.md
    """
    url = (config or {}).get("url") or "https://www.reddit.com/r/artificial+MachineLearning+OpenAI.json?limit=25&sort=hot"
    request = urllib.request.Request(url, headers={"User-Agent": "mycroft-aeo-workflow-a/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = json.loads(response.read().decode("utf-8", errors="replace"))
    return {"source_name": "Reddit", "url": url, "raw": raw}


if __name__ == "__main__":
    payload = load_input({})
    try:
        result = fetch_reddit(payload["data"])
    except Exception as exc:
        result = {"source_name": "Reddit", "error": str(exc)}
    emit(result, payload["output"])

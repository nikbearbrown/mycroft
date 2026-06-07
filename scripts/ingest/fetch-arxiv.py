"""Purpose: Fetch the ArXiv cs.AI RSS feed.
Input: Optional JSON object with url; default is the n8n ArXiv RSS URL.
Output: Raw feed text metadata for data/raw/aeo-workflow-a/.
Side effects: Performs one HTTP GET; optionally writes JSON to the supplied output path.
Idempotent: Yes for unchanged feed content; it does not mutate remote state.
Recipe: recipes/workflow-a-extract-store-raw-data.md
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_raw_intelligence_shared import emit, load_input


def fetch_arxiv(config: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
    """Purpose: Fetch the ArXiv cs.AI RSS feed.
    Input: Optional JSON object with url.
    Output: Raw feed text metadata.
    Side effects: Performs one HTTP GET.
    Idempotent: Yes for unchanged feed content.
    Recipe: recipes/workflow-a-extract-store-raw-data.md
    """
    url = (config or {}).get("url") or "https://export.arxiv.org/rss/cs.AI"
    with urllib.request.urlopen(url, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
    return {"source_name": "ArXiv", "url": url, "raw": raw, "bytes": len(raw)}


if __name__ == "__main__":
    payload = load_input({})
    try:
        result = fetch_arxiv(payload["data"])
    except Exception as exc:
        result = {"source_name": "ArXiv", "error": str(exc)}
    emit(result, payload["output"])

"""Purpose: Fetch recent AI/ML/NLP ArXiv papers.
Input: Optional JSON config with query and max_results.
Output: Raw ArXiv API response metadata for data/raw/ai-talent-intelligence-agent/.
Side effects: Performs one HTTP GET; optional file write.
Idempotent: Yes for unchanged ArXiv response; does not mutate remote state.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, load_input


def fetch_ai_talent_arxiv(config: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
    """Purpose: Fetch recent AI/ML/NLP ArXiv papers.
    Input: Optional JSON config with query and max_results.
    Output: Raw ArXiv API response metadata.
    Side effects: Performs one HTTP GET.
    Idempotent: Yes for unchanged ArXiv response.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    config = config or {}
    params = urllib.parse.urlencode({
        "search_query": config.get("search_query", "cat:cs.AI OR cat:cs.LG OR cat:cs.CL"),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": int(config.get("max_results", 50)),
    })
    url = f"http://export.arxiv.org/api/query?{params}"
    with urllib.request.urlopen(url, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
    return {"source_name": "ArXiv", "url": url, "raw": raw}


if __name__ == "__main__":
    payload = load_input({})
    try:
        result = fetch_ai_talent_arxiv(payload["data"])
    except Exception as exc:
        result = {"source_name": "ArXiv", "error": str(exc)}
    emit(result, payload["output"])

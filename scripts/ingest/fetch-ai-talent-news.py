"""Purpose: Prepare or perform Serper news search for AI researcher movement.
Input: Optional JSON config with query and num.
Output: Raw Serper response metadata for data/raw/ai-talent-intelligence-agent/.
Side effects: Performs one HTTP POST only when SERPER_API_KEY is available; optional file write.
Idempotent: Yes for same query and response; does not mutate remote state.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, load_input


def fetch_ai_talent_news(config: dict[str, Any] | None = None, timeout: int = 20) -> dict[str, Any]:
    """Purpose: Prepare or perform Serper news search for AI researcher movement.
    Input: Optional JSON config with query and num.
    Output: Raw Serper response metadata or live-call-required spec.
    Side effects: Performs one HTTP POST only when SERPER_API_KEY is available.
    Idempotent: Yes for same query and response.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    config = config or {}
    query = config.get("q", '"AI researcher" ("hired" OR "joined" OR "appointed") (OpenAI OR Anthropic OR Google OR Meta)')
    body = json.dumps({"q": query, "num": int(config.get("num", 20))}).encode("utf-8")
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return {"source_name": "Serper News", "query": query, "live_call_performed": False, "credential_env": "SERPER_API_KEY", "news": []}
    request = urllib.request.Request("https://google.serper.dev/news", data=body, headers={"X-API-KEY": api_key, "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = json.loads(response.read().decode("utf-8", errors="replace"))
    return {"source_name": "Serper News", "query": query, "raw": raw, "live_call_performed": True}


if __name__ == "__main__":
    payload = load_input({})
    try:
        result = fetch_ai_talent_news(payload["data"])
    except Exception as exc:
        result = {"source_name": "Serper News", "error": str(exc)}
    emit(result, payload["output"])

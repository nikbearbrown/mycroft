"""Purpose: Extract RAG evaluation questions from a CSV file already on disk.
Input: JSON object with path pointing to a local CSV under data/ or verified fixtures.
Output: Question rows for reports/generated/news-monitoring-agent/.
Side effects: Reads only the supplied local file; optional output write.
Idempotent: Yes; CSV extraction is deterministic.
Recipe: recipes/news-monitoring-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from typing import Any

from scripts.tools.news_monitoring_agent_shared import emit_json, load_json_input, read_csv_questions


def extract_questions_from_file(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Purpose: Extract RAG evaluation questions from a CSV file already on disk.
    Input: JSON object with path pointing to a local CSV.
    Output: Question rows.
    Side effects: Reads only the supplied local file.
    Idempotent: Yes; same file yields same output.
    Recipe: recipes/news-monitoring-agent.md
    """
    path = str(payload.get("path") or payload.get("file") or "data/verified/news-monitoring-agent/questions.csv")
    return read_csv_questions(path)


if __name__ == "__main__":
    payload = load_json_input({"path": "data/verified/news-monitoring-agent/questions.csv"})
    try:
        result = extract_questions_from_file(payload["data"])
    except Exception as exc:
        result = [{"error": str(exc)}]
    emit_json(result, payload["output"])

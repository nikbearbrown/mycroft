"""Purpose: Prepare Reddit rows for raw_intelligence storage.
Input: Parsed Reddit records from data/verified/aeo-workflow-a/.
Output: Idempotent storage row payloads for data/verified/aeo-workflow-a/.
Side effects: Optional file write only; no database writes.
Idempotent: Yes; duplicate URLs are collapsed deterministically.
Recipe: recipes/workflow-a-extract-store-raw-data.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.aeo_raw_intelligence_shared import emit, load_input, prepare_store_rows


def store_reddit(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Purpose: Prepare Reddit rows for raw_intelligence storage.
    Input: Parsed Reddit records.
    Output: Idempotent storage row payloads.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; duplicate URLs are collapsed.
    Recipe: recipes/workflow-a-extract-store-raw-data.md
    """
    return prepare_store_rows(items, "Reddit")


if __name__ == "__main__":
    payload = load_input([{"title": "AI", "url": "https://reddit.com/r/a", "raw_content": "Body"}])
    emit(store_reddit(payload["data"]), payload["output"])

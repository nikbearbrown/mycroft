"""Purpose: Keep only AI talent signals above the significance threshold.
Input: List of analyzed talent signals from data/verified/ai-talent-intelligence-agent/.
Output: High-significance signals.
Side effects: Optional file write only.
Idempotent: Yes; filtering is deterministic.
Recipe: recipes/ai-talent-intelligence-agent.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.gigo.ai_talent_shared import emit, filter_high_significance as filter_signals, load_input


def filter_high_significance(items: list[dict[str, Any]], threshold: int = 5) -> list[dict[str, Any]]:
    """Purpose: Keep only AI talent signals above the significance threshold.
    Input: List of analyzed talent signals.
    Output: High-significance signals.
    Side effects: None except optional caller-managed file write.
    Idempotent: Yes; same input yields same output.
    Recipe: recipes/ai-talent-intelligence-agent.md
    """
    return filter_signals(items, threshold)


if __name__ == "__main__":
    payload = load_input([{"significance": 8}, {"significance": 3}])
    emit(filter_high_significance(payload["data"]), payload["output"])

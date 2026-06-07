"""Purpose: Provide monitored AI/tech company configuration.
Input: No required input.
Output: Company records with symbols, names, aliases, and risk multipliers.
Side effects: Optional file write only.
Idempotent: Yes; static configuration is deterministic.
Recipe: recipes/mycroft-news-intelligence-agent.md
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from scripts.gigo.mycroft_news_intelligence_shared import company_list, emit, load_input
def mycroft_company_list() -> list[dict]:
    return company_list()
if __name__ == "__main__":
    payload = load_input(None)
    emit(mycroft_company_list(), payload["output"])

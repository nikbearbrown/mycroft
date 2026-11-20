"""Side-by-side comparison tables with source citations."""

from __future__ import annotations

from typing import Any

from ecis.intelligence.execute import _fmt, _rows
from ecis.intelligence.intent import parse_intent


def _cite(table: str, row: dict[str, Any]) -> str:
    tkr = row.get("ticker") or row.get("leader") or row.get("name") or "TICKER"
    q = row.get("quarter") or row.get("to_quarter") or ""
    return f"{table}.{tkr}.{q}"


def synthesise_comparison(query: str) -> dict[str, Any]:
    parsed = parse_intent(query)
    tickers = parsed["tickers"]
    tables = ["dodge_scores", "momentum_features", "tft_forecasts", "topic_shifts", "survival_curves"]
    citations: list[str] = []
    chunks = [f"Comparing {', '.join(tickers) or 'listed tickers'}."]
    for table in tables:
        rows = _rows(table, tickers or None)
        if not rows:
            continue
        keys = ("ticker", "quarter", "dodge", "momentum", "horizon", "p50", "survival", "js", "flag")
        chunks.append(f"{table}:\n{_fmt(rows, keys)}")
        for row in rows[:4]:
            citations.append(_cite(table, row))
    outlier = None
    dodge = _rows("dodge_scores", tickers or None)
    if dodge:
        ranked = sorted(dodge, key=lambda r: float(r.get("dodge") or 0), reverse=True)
        outlier = ranked[0]
        chunks.append(
            f"outlier: ticker={outlier.get('ticker')} dodge={outlier.get('dodge')} "
            f"quarter={outlier.get('quarter')}"
        )
        citations.append(_cite("dodge_scores", outlier))
    text = "\n\n".join(chunks)
    if citations:
        text += "\n\nsources: " + ", ".join(dict.fromkeys(citations))
    return {
        "intent": "comparison",
        "tickers": tickers,
        "tables": tables,
        "text": text,
        "citations": citations,
        "outlier": outlier,
        "query": query,
    }

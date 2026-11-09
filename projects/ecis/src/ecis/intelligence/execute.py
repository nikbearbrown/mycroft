"""Route parsed intents to snapshot tables and compose a text reply."""

from __future__ import annotations

from typing import Any

from ecis.analytics.store import fetch_table
from ecis.intelligence.intent import parse_intent


def _rows(table: str, tickers: list[str] | None = None) -> list[dict[str, Any]]:
    try:
        rows = fetch_table(table, limit=200)
    except Exception:
        return []
    if not tickers:
        return rows
    wanted = {t.upper() for t in tickers}
    return [r for r in rows if (r.get("ticker") or r.get("leader") or r.get("supplier") or "").upper() in wanted
            or (r.get("follower") or r.get("customer") or "").upper() in wanted]


def _fmt(rows: list[dict[str, Any]], keys: tuple[str, ...], limit: int = 8) -> str:
    if not rows:
        return "No matching rows."
    lines = []
    for row in rows[:limit]:
        bits = [f"{k}={row.get(k)}" for k in keys if k in row]
        lines.append(", ".join(bits))
    return "\n".join(lines)


def run_query(query: str) -> dict[str, Any]:
    parsed = parse_intent(query)
    intent = parsed["intent"]
    tickers = parsed["tickers"]
    tables: list[str] = []
    text = ""
    if intent == "retrieval":
        tables = ["dodge_scores", "management_confidence", "contradictions"]
        chunks = []
        for table in tables:
            rows = _rows(table, tickers or None)
            if rows:
                chunks.append(f"{table}:\n{_fmt(rows, ('ticker', 'quarter', 'dodge', 'confidence', 'rule', 'severity'))}")
        text = "\n\n".join(chunks) or "No retrieval hits. Run `--guidance-models` and `--reliability` first."
    elif intent == "comparison":
        tables = ["dodge_scores", "signal_chains", "contagion_links"]
        chunks = [f"Comparing {', '.join(tickers) or 'listed tickers'}."]
        for table in tables:
            rows = _rows(table, tickers or None)
            if rows:
                chunks.append(f"{table}:\n{_fmt(rows, ('ticker', 'leader', 'follower', 'quarter', 'dodge', 'hedging_streak', 'granger_r'))}")
        text = "\n\n".join(chunks)
    elif intent == "analysis":
        tables = ["signal_chains", "ood_flags", "selective_predictions", "contagion_links"]
        chunks = ["Scan for deterioration, abstention, and contagion."]
        chains = [r for r in _rows("signal_chains") if r.get("flag") == "sustained_deterioration"]
        abstain = [r for r in _rows("selective_predictions") if r.get("abstain") == 1]
        if chains:
            chunks.append("deterioration:\n" + _fmt(chains, ("ticker", "quarter", "flag", "weight")))
        if abstain:
            chunks.append("abstained:\n" + _fmt(abstain, ("ticker", "quarter", "reasons", "uncertainty")))
        links = _rows("contagion_links")
        if links:
            chunks.append("contagion:\n" + _fmt(links, ("leader", "follower", "granger_r", "lag_quarters")))
        text = "\n\n".join(chunks)
    else:
        tables = ["explanations", "shap_values", "ood_flags"]
        rows = _rows("explanations", tickers or None)
        text = _fmt(rows, ("ticker", "quarter", "text")) if rows else "No explanations yet. Run `--reliability`."
    return {
        "intent": intent,
        "tickers": tickers,
        "tables": tables,
        "text": text,
        "query": query,
    }

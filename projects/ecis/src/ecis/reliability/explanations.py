"""Plain-English templates from top feature attributions. Tickers stay as-is from the registry."""

from __future__ import annotations

from typing import Any

_LABEL = {
    "hedging_index": "hedging",
    "management_confidence": "management confidence",
    "specificity_change": "guidance specificity",
    "ceo_cfo_divergence": "CEO-CFO divergence",
    "dodge_score": "dodge score",
    "market_share_shift": "market-share language",
    "fls_delta": "forward-looking density",
    "finbert_delta": "tone",
    "sector_mood_z": "sector mood",
}


def _clause(feature: str, value: float) -> str:
    name = _LABEL.get(feature, feature.replace("_", " "))
    if value >= 0:
        return f"{name} rose"
    return f"{name} fell"


def explain_row(ticker: str, contributions: list[dict[str, Any]]) -> str:
    ranked = sorted(contributions, key=lambda r: abs(float(r.get("shap") or 0)), reverse=True)[:3]
    if not ranked:
        return f"{ticker} has no feature attributions yet."
    parts = [_clause(r["feature"], float(r.get("shap") or 0)) for r in ranked]
    if len(parts) == 1:
        return f"{ticker} flagged because {parts[0]}."
    if len(parts) == 2:
        return f"{ticker} flagged because {parts[0]} while {parts[1]}."
    return f"{ticker} flagged because {parts[0]} while {parts[1]} and {parts[2]}."


def explain_predictions(shap_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in shap_rows:
        ticker = (row.get("ticker") or "TICKER").upper()
        text = explain_row(ticker, row.get("contributions") or [])
        out.append({
            "ticker": ticker,
            "quarter": row.get("quarter"),
            "model_name": row.get("model_name"),
            "text": text,
            "top_features": row.get("top_features"),
        })
    return out

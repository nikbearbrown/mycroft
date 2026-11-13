"""Hybrid retrieval: Chroma transcript quotes plus structured snapshot rows."""

from __future__ import annotations

from typing import Any

from ecis.intelligence.execute import run_query


def _quotes(query: str, tickers: list[str] | None, n: int = 3) -> list[dict[str, Any]]:
    try:
        from ecis.embedding.embedder import query_similar
    except Exception:
        return []
    hits: list[dict[str, Any]] = []
    try:
        if tickers:
            for tkr in tickers:
                hits.extend(query_similar(query, n_results=n, ticker=tkr))
        else:
            hits = query_similar(query, n_results=n)
    except Exception:
        return []
    out = []
    for hit in hits[: n * 2]:
        meta = hit.get("metadata") or {}
        out.append({
            "text": (hit.get("text") or "")[:400],
            "ticker": meta.get("ticker"),
            "transcript_date": meta.get("transcript_date"),
            "section_label": meta.get("section_label"),
            "distance": hit.get("distance"),
        })
    return out


def hybrid_answer(query: str) -> dict[str, Any]:
    structured = run_query(query)
    quotes = _quotes(query, structured.get("tickers") or None)
    chunks = [structured.get("text") or ""]
    if quotes:
        lines = ["quotes:"]
        for q in quotes:
            tag = q.get("ticker") or "TICKER"
            day = q.get("transcript_date") or ""
            lines.append(f"{tag} {day}: {q['text']}")
        chunks.append("\n".join(lines))
    text = "\n\n".join(c for c in chunks if c).strip()
    structured["quotes"] = quotes
    structured["text"] = text
    structured["retrieval"] = "hybrid" if quotes else "structured"
    tables = list(structured.get("tables") or [])
    if quotes:
        tables.append("chroma")
    structured["tables"] = tables
    return structured

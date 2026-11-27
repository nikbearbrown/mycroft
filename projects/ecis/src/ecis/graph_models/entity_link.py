"""Resolve company mentions to canonical tickers from the registry. """

from __future__ import annotations

import re
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.db.init_db import get_connection
from ecis.db.ticker_registry import list_tickers
from ecis.guidance_models.qa_parser import parse_qa_corpus

_SKIP = {"inc", "corp", "ltd", "llc", "the", "and", "company", "co", "group"}


def _alias_map() -> dict[str, tuple[str, float]]:
    """Map lowercase alias -> (ticker, prior). Exact ticker beats name tokens."""
    out: dict[str, tuple[str, float]] = {}
    try:
        recs = list_tickers()
    except Exception:
        recs = []
    for rec in recs:
        tkr = (rec.get("ticker") or "").upper()
        if not tkr:
            continue
        out[tkr.lower()] = (tkr, 0.95)
        name = rec.get("company_name") or ""
        if name and name.upper() != tkr:
            out[name.lower()] = (tkr, 0.85)
            for tok in re.findall(r"[A-Za-z]{3,}", name):
                if tok.lower() not in _SKIP:
                    out.setdefault(tok.lower(), (tkr, 0.65))
    return out


def link_text(text: str, source_ticker: str, aliases: dict[str, tuple[str, float]] | None = None) -> list[dict[str, Any]]:
    aliases = aliases if aliases is not None else _alias_map()
    blob = text or ""
    hits = []
    seen = set()
    for alias, (tkr, prior) in sorted(aliases.items(), key=lambda kv: -len(kv[0])):
        if len(alias) < 2:
            continue
        pat = re.compile(rf"\b{re.escape(alias)}\b", re.I)
        m = pat.search(blob)
        if not m or tkr in seen:
            continue
        seen.add(tkr)
        start = max(0, m.start() - 40)
        hits.append({
            "mention": m.group(0),
            "linked_ticker": tkr,
            "confidence": prior,
            "context": blob[start:m.end() + 40],
        })
    return hits


def link_mentions(ticker: str | None = None) -> list[dict[str, Any]]:
    aliases = _alias_map()
    out: list[dict[str, Any]] = []
    try:
        conn = get_connection("signals")
        query = "SELECT ticker, transcript_date, supporting_quote FROM signals"
        params: list[str] = []
        if ticker:
            query += " WHERE ticker = ?"
            params.append(ticker.upper())
        quotes = [dict(r) for r in conn.execute(query, params).fetchall()]
        conn.close()
    except Exception:
        quotes = []
    for row in quotes:
        src = (row.get("ticker") or "").upper()
        for hit in link_text(row.get("supporting_quote") or "", src, aliases):
            if hit["linked_ticker"] == src:
                continue
            out.append({
                "ticker_source": src,
                "transcript_date": (row.get("transcript_date") or "")[:10],
                "quarter": quarter_key(row.get("transcript_date")),
                **hit,
                "method": "alias",
            })
    for pair in parse_qa_corpus(ticker):
        src = (pair.get("ticker") or "").upper()
        blob = f"{pair.get('question') or ''} {pair.get('answer') or ''}"
        for hit in link_text(blob, src, aliases):
            if hit["linked_ticker"] == src:
                continue
            out.append({
                "ticker_source": src,
                "transcript_date": (pair.get("transcript_date") or "")[:10],
                "quarter": quarter_key(pair.get("transcript_date")),
                **hit,
                "method": "alias",
            })
    return out

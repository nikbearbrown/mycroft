"""Company graph: nodes are tickers, edges are contagion, supply-chain, and sector links."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.store import fetch_table
from ecis.db.ticker_registry import list_tickers
from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows
from ecis.intelligence.contagion import contagion_links
from ecis.intelligence.supply_chain import load_links


def _latest_features(ticker: str | None = None) -> dict[str, dict[str, Any]]:
    rows = build_revision_rows(ticker)
    latest: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda r: r["quarter"]):
        latest[row["ticker"]] = row
    return latest


def build_graph(ticker: str | None = None) -> dict[str, Any]:
    recs = list_tickers()
    if not recs:
        recs = [{"ticker": t, "sector": "AI", "company_name": t} for t in _latest_features(ticker)]
    nodes = []
    sectors: dict[str, str] = {}
    names: dict[str, str] = {}
    feats = _latest_features(ticker)
    for rec in recs:
        tkr = (rec.get("ticker") or "").upper()
        if not tkr:
            continue
        if ticker and tkr != ticker.upper() and ticker.upper() not in feats:
            pass
        sectors[tkr] = rec.get("sector") or "AI"
        names[tkr] = rec.get("company_name") or tkr
        row = feats.get(tkr) or {}
        vector = list(row.get("vector") or [0.0] * len(FEATURE_NAMES))
        nodes.append({
            "ticker": tkr,
            "sector": sectors[tkr],
            "company_name": names[tkr],
            "quarter": row.get("quarter"),
            "vector": vector,
            "target": row.get("target"),
            "hedging_index": (row.get("features") or {}).get("hedging_index"),
        })
    if ticker:
        keep = {ticker.upper()}
    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def _add(src: str, dst: str, kind: str, weight: float, **extra: Any) -> None:
        if not src or not dst or src == dst:
            return
        key = (src, dst, kind)
        if key in seen:
            return
        seen.add(key)
        edges.append({"src": src, "dst": dst, "kind": kind, "weight": float(weight), **extra})

    by_sector: dict[str, list[str]] = defaultdict(list)
    for n in nodes:
        by_sector[n["sector"]].append(n["ticker"])
    for names_in_sector in by_sector.values():
        for a in names_in_sector:
            for b in names_in_sector:
                if a != b:
                    _add(a, b, "sector", 0.35, lag=0, granger_r=None)

    for row in contagion_links(None):
        _add(row["leader"], row["follower"], "contagion", float(row.get("granger_r") or 0.25),
             lag=row.get("lag_quarters") or 1, granger_r=row.get("granger_r"))
    for a, b in load_links():
        _add(a, b, "supply", 0.55, lag=1, granger_r=None)
    try:
        for row in fetch_table("correlations", limit=500):
            _add((row.get("ticker_a") or "").upper(), (row.get("ticker_b") or "").upper(),
                 "correlation", abs(float(row.get("coefficient") or 0)),
                 lag=row.get("lag") or 0, granger_r=row.get("coefficient"))
    except Exception:
        pass

    if ticker:
        t = ticker.upper()
        nbrs = {t}
        for e in edges:
            if e["src"] == t or e["dst"] == t:
                nbrs.add(e["src"])
                nbrs.add(e["dst"])
        nodes = [n for n in nodes if n["ticker"] in nbrs]
        edges = [e for e in edges if e["src"] in nbrs and e["dst"] in nbrs]
    return {"nodes": nodes, "edges": edges}

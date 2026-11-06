from __future__ import annotations

import os
from typing import Any

from ecis.analytics.stats import pearson
from ecis.db.init_db import get_connection
from ecis.intelligence.contagion import _series


def load_links() -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    raw = os.getenv("SUPPLY_CHAIN_PAIRS", "")
    for part in raw.split(","):
        if ":" in part:
            a, b = part.split(":", 1)
            if a.strip() and b.strip():
                links.append((a.strip().upper(), b.strip().upper()))
    try:
        conn = get_connection("agents")
        rows = conn.execute("SELECT supplier, customer FROM supply_links").fetchall()
        conn.close()
        for row in rows:
            links.append(((row["supplier"] or "").upper(), (row["customer"] or "").upper()))
    except Exception:
        pass
    seen = set()
    out = []
    for pair in links:
        if pair in seen or not pair[0] or not pair[1] or pair[0] == pair[1]:
            continue
        seen.add(pair)
        out.append(pair)
    return out


def upsert_link(supplier: str, customer: str) -> None:
    conn = get_connection("agents")
    conn.execute(
        "INSERT OR IGNORE INTO supply_links (supplier, customer) VALUES (?, ?)",
        (supplier.upper(), customer.upper()),
    )
    conn.commit()
    conn.close()


def supply_propagation(ticker: str | None = None) -> list[dict[str, Any]]:
    links = load_links()
    if ticker:
        t = ticker.upper()
        links = [p for p in links if t in p]
    hedge = _series("hedging_index")
    conf = _series("confidence")
    out = []
    for supplier, customer in links:
        hs, hc = hedge.get(supplier, {}), hedge.get(customer, {})
        shared = sorted(set(hs) & set(hc))
        if len(shared) < 3:
            continue
        r1 = pearson([hs[q] for q in shared[:-1]], [hc[q] for q in shared[1:]])
        r0 = pearson([hs[q] for q in shared], [hc[q] for q in shared])
        delay = 1 if (r1 or 0) > (r0 or 0) + 0.05 else 0
        cs, cc = conf.get(supplier, {}), conf.get(customer, {})
        conf_drop = False
        if shared:
            last, prev = shared[-1], shared[0]
            conf_drop = (cs.get(last, 50) < cs.get(prev, 50) - 5) and (hc.get(last, 0) > hc.get(shared[0], 0))
        out.append({
            "supplier": supplier,
            "customer": customer,
            "signal_type": "hedging_index",
            "same_quarter_r": r0,
            "lag1_r": r1,
            "delay_quarters": delay,
            "early_warning": int(delay >= 1 or conf_drop),
            "n": len(shared),
        })
    return out

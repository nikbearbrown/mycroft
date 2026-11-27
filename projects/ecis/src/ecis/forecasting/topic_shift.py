"""Quarter-over-quarter Jensen-Shannon topic-shift alerts."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

SHIFT_MAX = 0.25


def _kl(p: list[float], q: list[float]) -> float:
    s = 0.0
    for a, b in zip(p, q):
        if a <= 0:
            continue
        s += a * math.log(a / max(b, 1e-12))
    return s


def js_divergence(p: list[float], q: list[float]) -> float:
    n = max(len(p), len(q))
    pp = list(p) + [0.0] * (n - len(p))
    qq = list(q) + [0.0] * (n - len(q))
    sp, sq = sum(pp) or 1.0, sum(qq) or 1.0
    pp = [x / sp for x in pp]
    qq = [x / sq for x in qq]
    mid = [0.5 * (a + b) for a, b in zip(pp, qq)]
    return 0.5 * _kl(pp, mid) + 0.5 * _kl(qq, mid)


def _distributions(topics: list[dict[str, Any]], key: str) -> dict[tuple[str, str], dict[int, float]]:
    out: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for row in topics:
        ident = (row.get(key) or "", row.get("quarter") or "")
        out[ident][int(row.get("topic_id") or 0)] = float(row.get("weight") or 0)
    return out


def track_shifts(topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scope, key in (("ticker", "ticker"), ("sector", "sector")):
        dist = _distributions(topics, key)
        by_id: dict[str, list[str]] = defaultdict(list)
        for ident, _ in dist.items():
            if ident[0] and ident[1] not in by_id[ident[0]]:
                by_id[ident[0]].append(ident[1])
        for ident, quarters in by_id.items():
            quarters = sorted(quarters)
            for prev, cur in zip(quarters, quarters[1:]):
                a = dist[(ident, prev)]
                b = dist[(ident, cur)]
                ids = sorted(set(a) | set(b))
                p = [a.get(i, 0.0) for i in ids]
                q = [b.get(i, 0.0) for i in ids]
                js = js_divergence(p, q)
                rows.append({
                    "scope": scope,
                    "name": ident,
                    "from_quarter": prev,
                    "to_quarter": cur,
                    "js": js,
                    "flag": "shift" if js >= SHIFT_MAX else "ok",
                })
    return rows

"""Abstain when conformal width, dropout variance, or ensemble disagreement is high."""

from __future__ import annotations

import os
from typing import Any

WIDTH_MAX = float(os.getenv("SELECTIVE_WIDTH_MAX", "0.35"))
VAR_MAX = float(os.getenv("SELECTIVE_VARIANCE_MAX", "0.04"))
DIS_MAX = float(os.getenv("SELECTIVE_DISAGREE_MAX", "0.18"))


def decide_abstention(
    intervals: list[dict[str, Any]],
    dropout: list[dict[str, Any]],
    disagreement: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    drop = {(r.get("ticker"), r.get("quarter")): r for r in dropout}
    dis = {(r.get("ticker"), r.get("quarter")): r for r in disagreement}
    out = []
    seen: set[tuple[str, str]] = set()
    for row in intervals:
        key = ((row.get("ticker") or "").upper(), row.get("quarter") or "")
        if key in seen:
            continue
        seen.add(key)
        reasons = []
        width = float(row.get("width") or 0)
        if width > WIDTH_MAX:
            reasons.append("wide_interval")
        dv = drop.get(key) or {}
        if float(dv.get("variance") or 0) > VAR_MAX:
            reasons.append("mc_dropout")
        dj = dis.get(key) or {}
        if float(dj.get("disagreement") or 0) > DIS_MAX:
            reasons.append("ensemble_disagreement")
        out.append({
            "ticker": key[0],
            "quarter": key[1],
            "abstain": int(bool(reasons)),
            "reasons": reasons,
            "width": width,
            "variance": dv.get("variance"),
            "disagreement": dj.get("disagreement"),
            "uncertainty": "high" if reasons else "ok",
        })
    return out

"""Pairwise feature interactions that beat either feature alone."""

from __future__ import annotations

from typing import Any

from ecis.guidance_models.revision_features import FEATURE_NAMES, build_revision_rows
from ecis.analytics.stats import pearson
from ecis.scoring.significance import paired_permutation_diff


def discover_interactions(ticker: str | None = None, top_n: int = 8) -> list[dict[str, Any]]:
    rows = [r for r in build_revision_rows(ticker) if r.get("target") is not None]
    if len(rows) < 4:
        return []
    names = list(FEATURE_NAMES)
    y = [float(r["target"]) for r in rows]
    cols = {n: [float(r["features"].get(n) or 0) for r in rows] for n in names}
    singles = {n: pearson(cols[n], y) for n in names}

    scored: list[dict[str, Any]] = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            inter = [cols[a][k] * cols[b][k] for k in range(len(y))]
            r = pearson(inter, y)
            best_single = max(abs(singles[a] or 0), abs(singles[b] or 0))
            gain = (abs(r) if r is not None else 0.0) - best_single
            if gain <= 0:
                continue
            se_i = [(p - t) ** 2 for p, t in zip(inter, y)]
            se_a = [(p - t) ** 2 for p, t in zip(cols[a], y)]
            perm = paired_permutation_diff(se_i, se_a, n_perm=200)
            scored.append({
                "feature_a": a,
                "feature_b": b,
                "interaction": f"{a}*{b}",
                "pearson": r,
                "gain": gain,
                "p_value": perm["p_value"],
            })
    scored.sort(key=lambda r: -(r["gain"] or 0))
    return scored[:top_n]

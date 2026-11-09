"""Versioned feature vectors for next-quarter guidance revision."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.guidance_models.dodge import aggregate_dodge
from ecis.guidance_models.market_share import track_shifts
from ecis.analytics.features import quarter_key
from ecis.analytics.management import ceo_cfo_divergence, guidance_language, management_confidence
from ecis.analytics.sector_sentiment import cross_sector_zscores
from ecis.db.init_db import get_connection
from ecis.db.ticker_registry import get_ticker

FEATURE_NAMES = [
    "hedging_index",
    "management_confidence",
    "specificity_change",
    "ceo_cfo_divergence",
    "dodge_score",
    "market_share_shift",
    "fls_delta",
    "finbert_delta",
    "sector_mood_z",
]
FEATURE_VERSION = "rev-v1"


def _signal_quarters(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = """
        SELECT ticker, transcript_date, direction,
               COALESCE(hedging_index, 0) AS hedging_index,
               COALESCE(fls_density, 0) AS fls_density,
               COALESCE(tone_shift, 0) AS tone_shift
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[((row["ticker"] or "").upper(), quarter_key(row.get("transcript_date")))].append(row)
    out: list[dict[str, Any]] = []
    for (tkr, q), items in buckets.items():
        n = max(len(items), 1)
        dirs = [r["direction"] for r in items]
        majority = max(set(dirs), key=dirs.count)
        out.append({
            "ticker": tkr,
            "quarter": q,
            "direction": majority,
            "hedging_index": sum(float(r["hedging_index"]) for r in items) / n,
            "fls_density": sum(float(r["fls_density"]) for r in items) / n,
            "tone_shift": sum(float(r["tone_shift"]) for r in items) / n,
        })
    return sorted(out, key=lambda r: (r["ticker"], r["quarter"]))


def _index(rows: list[dict[str, Any]], *keys: str) -> dict[tuple, dict[str, Any]]:
    out = {}
    for row in rows:
        out[tuple(row.get(k) for k in keys)] = row
    return out


def build_revision_rows(ticker: str | None = None) -> list[dict[str, Any]]:
    quarters = _signal_quarters(ticker)
    conf = _index(management_confidence(ticker), "ticker", "quarter")
    guide = _index(guidance_language(ticker), "ticker", "quarter")
    div = {}
    for row in ceo_cfo_divergence(ticker):
        div[(row["ticker"], row["quarter"])] = row
    dodge = {}
    for row in aggregate_dodge(ticker=ticker):
        if row.get("scope") == "call":
            dodge[(row["ticker"], row["quarter"])] = row
    shifts = _index(track_shifts(ticker), "ticker", "quarter")
    mood_z = {}
    for row in cross_sector_zscores(ticker):
        mood_z[(row["sector"], row["quarter"])] = row

    by_tkr: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in quarters:
        by_tkr[row["ticker"]].append(row)

    out: list[dict[str, Any]] = []
    for tkr, items in by_tkr.items():
        items = sorted(items, key=lambda r: r["quarter"])
        for i, row in enumerate(items):
            nxt = items[i + 1] if i + 1 < len(items) else None
            prev = items[i - 1] if i else None
            sector = "AI"
            try:
                rec = get_ticker(tkr)
                if rec:
                    sector = rec.get("sector") or "AI"
            except Exception:
                pass
            features = {
                "hedging_index": row["hedging_index"],
                "management_confidence": (conf.get((tkr, row["quarter"])) or {}).get("confidence") or 50.0,
                "specificity_change": (guide.get((tkr, row["quarter"])) or {}).get("specificity_change") or 0.0,
                "ceo_cfo_divergence": (div.get((tkr, row["quarter"])) or {}).get("confidence_gap") or 0.0,
                "dodge_score": (dodge.get((tkr, row["quarter"])) or {}).get("dodge") or 0.0,
                "market_share_shift": (shifts.get((tkr, row["quarter"])) or {}).get("score_change") or 0.0,
                "fls_delta": row["fls_density"] - (prev["fls_density"] if prev else row["fls_density"]),
                "finbert_delta": row["tone_shift"] - (prev["tone_shift"] if prev else 0.0),
                "sector_mood_z": (mood_z.get((sector, row["quarter"])) or {}).get("z_score") or 0.0,
            }
            target = None
            if nxt is not None:
                target = 1 if nxt["direction"] != row["direction"] else 0
            out.append({
                "ticker": tkr,
                "quarter": row["quarter"],
                "features": features,
                "vector": [float(features[n]) for n in FEATURE_NAMES],
                "target": target,
                "current_direction": row["direction"],
                "next_direction": None if nxt is None else nxt["direction"],
                "feature_version": FEATURE_VERSION,
            })
    return out


def normalize_vectors(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return rows
    dims = len(FEATURE_NAMES)
    means = [0.0] * dims
    stds = [1.0] * dims
    for j in range(dims):
        xs = [r["vector"][j] for r in rows]
        mu = sum(xs) / len(xs)
        var = sum((x - mu) ** 2 for x in xs) / max(len(xs) - 1, 1)
        sd = var ** 0.5
        means[j] = mu
        stds[j] = sd if sd > 1e-9 else 1.0
    out = []
    for row in rows:
        copy = dict(row)
        copy["vector"] = [(row["vector"][j] - means[j]) / stds[j] for j in range(dims)]
        out.append(copy)
    return out

"""Figurative vs concrete language: financial-metaphor lexicon plus density flags."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import quarter_key
from ecis.analytics.stats import mean, stdev
from ecis.db.init_db import get_connection

METAPHORS = (
    "headwind", "headwinds", "tailwind", "tailwinds", "runway", "pipeline",
    "moat", "inflection", "inflection point", "on ramp", "flywheel",
    "green shoots", "put wind in", "storm", "fog", "bridge to",
)


def metaphor_hits(text: str) -> list[str]:
    blob = (text or "").lower()
    return [m for m in METAPHORS if m in blob]


def density(text: str) -> float:
    tokens = max(len((text or "").split()), 1)
    return min(1.0, len(metaphor_hits(text)) / max(tokens / 40.0, 1.0))


def track_metaphors(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = "SELECT ticker, transcript_date, speaker_role, supporting_quote FROM signals"
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    buckets: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for row in rows:
        role = (row.get("speaker_role") or "unknown").lower()
        buckets[((row["ticker"] or "").upper(), (row["transcript_date"] or "")[:10], role)].append(
            row.get("supporting_quote") or ""
        )

    hist: dict[str, list[float]] = defaultdict(list)
    out = []
    for (tkr, day, role), quotes in sorted(buckets.items()):
        text = " ".join(quotes)
        dens = density(text)
        hist[tkr].append(dens)
        mu = mean(hist[tkr])
        sd = stdev(hist[tkr])
        spike = dens is not None and mu is not None and dens > (mu + (sd or 0.08))
        out.append({
            "ticker": tkr,
            "transcript_date": day,
            "quarter": quarter_key(day),
            "speaker_role": role,
            "density": dens,
            "hits": metaphor_hits(text),
            "flag": "spike" if spike else "normal",
            "historical_mean": mu,
        })
    return out

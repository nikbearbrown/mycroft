"""Management confidence, guidance-language tracker, and CEO vs CFO divergence."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import (
    definitive_ratio,
    fls,
    hedging,
    numerical_specificity,
    quarter_key,
    tone_from_signal,
)
from ecis.analytics.stats import mean, stdev
from ecis.db.init_db import get_connection

DIVERGENCE_FLAG = 20.0


def _signals(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = """
        SELECT ticker, transcript_date, speaker_role, direction,
               COALESCE(confidence_calibrated, confidence_raw) AS confidence,
               supporting_quote AS quote,
               hedging_index, fls_density, tone_shift
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    return rows


def confidence_score(row: dict[str, Any]) -> float:
    """0–100 composite: inverse hedging, FLS, definitive ratio, numerical specificity."""
    text = row.get("quote") or ""
    hedge = hedging(row, text)
    fls_val = fls(row, text)
    definite = definitive_ratio(text)
    specific = numerical_specificity(text)
    raw = (
        (1.0 - hedge) * 0.35
        + fls_val * 0.25
        + definite * 0.20
        + specific * 0.20
    )
    return max(0.0, min(100.0, raw * 100.0))


def management_confidence(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = _signals(ticker)
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        tkr = (row.get("ticker") or "").upper()
        q = quarter_key(row.get("transcript_date"))
        buckets[(tkr, q)].append(row)

    out: list[dict[str, Any]] = []
    for (tkr, quarter), items in sorted(buckets.items()):
        scores = [confidence_score(r) for r in items]
        texts = [r.get("quote") or "" for r in items]
        out.append({
            "ticker": tkr,
            "quarter": quarter,
            "n_signals": len(items),
            "confidence": mean(scores),
            "hedging_mean": mean([hedging(r, r.get("quote") or "") for r in items]),
            "fls_mean": mean([fls(r, r.get("quote") or "") for r in items]),
            "definitive_ratio": mean([definitive_ratio(t) for t in texts]),
            "numerical_specificity": mean([numerical_specificity(t) for t in texts]),
        })
    return out


def guidance_language(ticker: str | None = None) -> list[dict[str, Any]]:
    """Quarter-over-quarter change in numerical specificity of guidance language."""
    conf = management_confidence(ticker)
    by_ticker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in conf:
        by_ticker[row["ticker"]].append(row)

    out: list[dict[str, Any]] = []
    for tkr, items in by_ticker.items():
        items = sorted(items, key=lambda r: r["quarter"])
        prev: float | None = None
        prev_q: str | None = None
        for row in items:
            spec = row.get("numerical_specificity")
            delta = None
            flag = "stable"
            if spec is not None and prev is not None:
                delta = spec - prev
                if delta >= 0.15:
                    flag = "more_specific"
                elif delta <= -0.15:
                    flag = "more_vague"
            out.append({
                "ticker": tkr,
                "quarter": row["quarter"],
                "prior_quarter": prev_q,
                "specificity": spec,
                "specificity_change": delta,
                "flag": flag,
                "confidence": row.get("confidence"),
            })
            prev = spec
            prev_q = row["quarter"]
    return out


def ceo_cfo_divergence(ticker: str | None = None) -> list[dict[str, Any]]:
    """Tone / confidence gap between CEO and CFO on the same call."""
    rows = _signals(ticker)
    buckets: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        role = (row.get("speaker_role") or "unknown").lower()
        if role not in {"ceo", "cfo"}:
            continue
        tkr = (row.get("ticker") or "").upper()
        date = (row.get("transcript_date") or "")[:10]
        buckets[(tkr, date)][role].append(row)

    divergences: list[dict[str, Any]] = []
    hist: dict[str, list[float]] = defaultdict(list)
    for (tkr, date), roles in sorted(buckets.items()):
        if "ceo" not in roles or "cfo" not in roles:
            continue
        ceo_tone = mean([tone_from_signal(r) for r in roles["ceo"]])
        cfo_tone = mean([tone_from_signal(r) for r in roles["cfo"]])
        ceo_conf = mean([confidence_score(r) for r in roles["ceo"]])
        cfo_conf = mean([confidence_score(r) for r in roles["cfo"]])
        if ceo_conf is None or cfo_conf is None:
            continue
        gap = abs(ceo_conf - cfo_conf)
        tone_gap = None
        if ceo_tone is not None and cfo_tone is not None:
            tone_gap = abs(ceo_tone - cfo_tone)
        hist[tkr].append(gap)
        divergences.append({
            "ticker": tkr,
            "transcript_date": date,
            "quarter": quarter_key(date),
            "ceo_confidence": ceo_conf,
            "cfo_confidence": cfo_conf,
            "confidence_gap": gap,
            "ceo_tone": ceo_tone,
            "cfo_tone": cfo_tone,
            "tone_gap": tone_gap,
            "flag": "aligned",
        })

    for row in divergences:
        series = hist.get(row["ticker"]) or []
        mu = mean(series)
        sd = stdev(series)
        flagged = row["confidence_gap"] >= DIVERGENCE_FLAG
        if mu is not None and sd is not None and sd > 0:
            flagged = flagged or row["confidence_gap"] >= mu + sd
        row["flag"] = "divergent" if flagged else "aligned"
        row["historical_mean_gap"] = mu
    return divergences

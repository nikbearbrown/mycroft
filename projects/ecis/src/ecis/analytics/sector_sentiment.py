"""Sector sentiment aggregator, mood index, and cross-sector z-score heatmap."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ecis.analytics.features import fls, hedging, quarter_key, tone_from_signal
from ecis.analytics.stats import mean, median, stdev, weighted_mean, zscore
from ecis.db.init_db import get_connection

MOOD_BULLISH = 0.25
MOOD_BEARISH = -0.25


def _market_caps() -> dict[str, float]:
    conn = get_connection("agents")
    try:
        rows = conn.execute("SELECT ticker, market_cap, sector FROM tickers").fetchall()
    except Exception:
        conn.close()
        return {}
    conn.close()
    caps: dict[str, float] = {}
    for row in rows:
        ticker = (row["ticker"] or "").upper()
        cap = row["market_cap"] if "market_cap" in row.keys() else None
        try:
            caps[ticker] = float(cap) if cap not in (None, "") else 1.0
        except (TypeError, ValueError):
            caps[ticker] = 1.0
    return caps


def _sectors() -> dict[str, str]:
    conn = get_connection("agents")
    try:
        rows = conn.execute("SELECT ticker, sector FROM tickers").fetchall()
    except Exception:
        conn.close()
        return {}
    conn.close()
    return {(row["ticker"] or "").upper(): (row["sector"] or "AI") for row in rows}


def _signals(ticker: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection("signals")
    query = """
        SELECT ticker, transcript_date, direction,
               COALESCE(confidence_calibrated, confidence_raw) AS confidence,
               supporting_quote AS quote,
               hedging_index, fls_density, tone_shift, speaker_role
        FROM signals
    """
    params: list[str] = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker.upper())
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    return rows


def _weight(ticker: str, caps: dict[str, float]) -> float:
    w = caps.get(ticker.upper(), 1.0)
    return w if w and w > 0 else 1.0


def aggregate_sector_sentiment(ticker: str | None = None) -> list[dict[str, Any]]:
    """Mean / median / stdev of tone, hedging, and FLS, market-cap weighted when caps exist."""
    rows = _signals(ticker)
    caps = _market_caps()
    sectors = _sectors()
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        tkr = (row.get("ticker") or "").upper()
        sector = sectors.get(tkr, "AI")
        q = quarter_key(row.get("transcript_date"))
        buckets[(sector, q)].append(row)

    out: list[dict[str, Any]] = []
    for (sector, quarter), items in sorted(buckets.items()):
        tones = [tone_from_signal(r) for r in items]
        hedges = [hedging(r, r.get("quote") or "") for r in items]
        flss = [fls(r, r.get("quote") or "") for r in items]
        weights = [_weight((r.get("ticker") or ""), caps) for r in items]
        tickers = sorted({(r.get("ticker") or "").upper() for r in items})
        out.append({
            "sector": sector,
            "quarter": quarter,
            "n_signals": len(items),
            "n_tickers": len(tickers),
            "tone_mean": weighted_mean(tones, weights),
            "tone_median": median(tones),
            "tone_stdev": stdev(tones),
            "hedging_mean": weighted_mean(hedges, weights),
            "hedging_median": median(hedges),
            "hedging_stdev": stdev(hedges),
            "fls_mean": weighted_mean(flss, weights),
            "fls_median": median(flss),
            "fls_stdev": stdev(flss),
            "equal_weighted": 1 if all(w == 1.0 for w in weights) else 0,
        })
    return out


def _mood_score(tone: float | None, hedge: float | None, fls_val: float | None) -> float | None:
    parts = []
    if tone is not None:
        parts.append(float(tone))
    if hedge is not None:
        parts.append(1.0 - float(hedge))
    if fls_val is not None:
        parts.append(float(fls_val) * 2.0 - 1.0)
    if not parts:
        return None
    return sum(parts) / len(parts)


def _regime(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= MOOD_BULLISH:
        return "bullish"
    if score <= MOOD_BEARISH:
        return "bearish"
    return "neutral"


def sector_mood_index(ticker: str | None = None) -> list[dict[str, Any]]:
    """Composite mood from polarity, inverse hedging, and FLS; flags regime vs prior quarter."""
    sentiment = aggregate_sector_sentiment(ticker)
    by_sector: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sentiment:
        by_sector[row["sector"]].append(row)

    out: list[dict[str, Any]] = []
    for sector, items in by_sector.items():
        items = sorted(items, key=lambda r: r["quarter"])
        prev_score: float | None = None
        for row in items:
            score = _mood_score(row.get("tone_mean"), row.get("hedging_mean"), row.get("fls_mean"))
            regime = _regime(score)
            shift = None
            if score is not None and prev_score is not None:
                shift = score - prev_score
                if shift <= -0.15:
                    regime = "bearish"
                elif shift >= 0.15:
                    regime = "bullish"
            out.append({
                "sector": sector,
                "quarter": row["quarter"],
                "mood_score": score,
                "regime": regime,
                "mood_shift": shift,
                "n_signals": row["n_signals"],
                "n_tickers": row["n_tickers"],
            })
            prev_score = score
    return out


def cross_sector_zscores(ticker: str | None = None) -> list[dict[str, Any]]:
    """Z-score each sector's mood against all sectors in the same quarter."""
    moods = sector_mood_index(ticker)
    by_q: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in moods:
        by_q[row["quarter"]].append(row)
    out: list[dict[str, Any]] = []
    for quarter, items in sorted(by_q.items()):
        scores = [r.get("mood_score") for r in items]
        for row in items:
            out.append({
                "sector": row["sector"],
                "quarter": quarter,
                "mood_score": row.get("mood_score"),
                "z_score": zscore(row.get("mood_score"), scores),
                "regime": row.get("regime"),
            })
    return out

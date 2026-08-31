"""Outcome resolver: fetch market prices and evaluate signal correctness."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import yfinance as yf

from ecis.db.init_db import get_connection

logger = logging.getLogger(__name__)

HORIZONS = (30, 90, 180)
BENCHMARK_TICKER = "SPY"


def _fetch_price(ticker: str, target_date: date, tolerance_days: int = 5) -> float | None:
    """Fetch closing price on or near target_date.

    Looks within +/- tolerance_days for the nearest trading day.
    """
    start = target_date - timedelta(days=tolerance_days)
    end = target_date + timedelta(days=tolerance_days + 1)
    try:
        df = yf.download(ticker, start=str(start), end=str(end), progress=False)
        if df.empty:
            return None
        idx = df.index.get_indexer([target_date], method="nearest")[0]
        return float(df.iloc[idx]["Close"].iloc[0]) if hasattr(df.iloc[idx]["Close"], "iloc") else float(df.iloc[idx]["Close"])
    except Exception as exc:
        logger.error("Price fetch failed for %s on %s: %s", ticker, target_date, exc)
        return None


def _evaluate_correctness(direction: str, excess_return: float) -> int | None:
    """Determine if the signal was correct based on direction and excess return.

    Returns 1 (correct), 0 (incorrect), or None (indeterminate).
    """
    if abs(excess_return) < 0.005:
        return None

    if direction == "raised" and excess_return > 0:
        return 1
    elif direction == "lowered" and excess_return < 0:
        return 1
    elif direction == "maintained" and abs(excess_return) < 0.03:
        return 1
    elif direction in ("raised", "lowered"):
        return 0
    return None


def _had_split(ticker: str, t0: date) -> bool:
    try:
        actions = yf.Ticker(ticker).splits
        if actions is None or getattr(actions, "empty", True):
            return False
        for ts in actions.index:
            split_day = ts.date() if hasattr(ts, "date") else date.fromisoformat(str(ts)[:10])
            if t0 <= split_day <= date.today():
                return True
    except Exception as exc:
        logger.debug("Split lookup failed for %s: %s", ticker, exc)
    return False


def resolve_signal(signal_id: int, *, force: bool = False) -> list[dict[str, Any]]:
    """Resolve outcomes for a single signal across all horizons.

    Returns list of outcome dicts that were inserted.
    """
    conn = get_connection("signals")
    row = conn.execute(
        "SELECT ticker, direction, transcript_date FROM signals WHERE signal_id = ?",
        (signal_id,),
    ).fetchone()
    conn.close()

    if not row:
        logger.warning("Signal %d not found", signal_id)
        return []

    ticker = row["ticker"]
    direction = row["direction"]
    t0_date = date.fromisoformat(row["transcript_date"])
    today = date.today()
    split_adjusted = 1 if _had_split(ticker, t0_date) else 0

    if force:
        _invalidate_outcomes(signal_id)
    else:
        cached = _cached_outcomes(signal_id, str(t0_date), split_adjusted)
        if cached is not None:
            return cached

    price_t0 = _fetch_price(ticker, t0_date)
    bench_t0 = _fetch_price(BENCHMARK_TICKER, t0_date)

    if price_t0 is None or bench_t0 is None:
        logger.warning("Could not fetch t0 prices for signal %d (%s on %s)", signal_id, ticker, t0_date)
        return []

    outcomes = []
    for horizon in HORIZONS:
        t1_date = t0_date + timedelta(days=horizon)
        if t1_date > today:
            continue

        price_t1 = _fetch_price(ticker, t1_date)
        bench_t1 = _fetch_price(BENCHMARK_TICKER, t1_date)

        if price_t1 is None or bench_t1 is None:
            continue

        stock_return = (price_t1 - price_t0) / price_t0
        bench_return = (bench_t1 - bench_t0) / bench_t0
        excess = stock_return - bench_return
        correct = _evaluate_correctness(direction, excess)

        outcome = {
            "signal_id": signal_id,
            "horizon_days": horizon,
            "stock_price_t0": round(price_t0, 4),
            "stock_price_t1": round(price_t1, 4),
            "benchmark_price_t0": round(bench_t0, 4),
            "benchmark_price_t1": round(bench_t1, 4),
            "stock_return": round(stock_return, 6),
            "benchmark_return": round(bench_return, 6),
            "excess_return": round(excess, 6),
            "correct": correct,
            "transcript_date": str(t0_date),
            "split_adjusted": split_adjusted,
        }
        outcomes.append(outcome)

    if outcomes:
        _write_outcomes(outcomes)

    return outcomes


def _cached_outcomes(signal_id: int, transcript_date: str, split_adjusted: int) -> list[dict[str, Any]] | None:
    conn = get_connection("outcomes")
    try:
        rows = conn.execute(
            """SELECT * FROM outcomes WHERE signal_id = ?""",
            (signal_id,),
        ).fetchall()
    except Exception:
        conn.close()
        return None
    conn.close()
    if not rows:
        return None
    stale = False
    for row in rows:
        keys = row.keys()
        cached_date = row["transcript_date"] if "transcript_date" in keys else None
        cached_split = row["split_adjusted"] if "split_adjusted" in keys else 0
        if cached_date and cached_date != transcript_date:
            stale = True
            break
        if split_adjusted and not cached_split:
            stale = True
            break
    if stale:
        _invalidate_outcomes(signal_id)
        return None
    return []


def _invalidate_outcomes(signal_id: int) -> None:
    conn = get_connection("outcomes")
    conn.execute("DELETE FROM outcomes WHERE signal_id = ?", (signal_id,))
    conn.commit()
    conn.close()


def _write_outcomes(outcomes: list[dict[str, Any]]) -> None:
    """Insert outcomes into the outcomes database."""
    conn = get_connection("outcomes")
    conn.execute("PRAGMA foreign_keys=OFF")
    for o in outcomes:
        conn.execute(
            """INSERT OR IGNORE INTO outcomes
               (signal_id, horizon_days, stock_price_t0, stock_price_t1,
                benchmark_price_t0, benchmark_price_t1,
                stock_return, benchmark_return, excess_return, correct,
                transcript_date, split_adjusted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                o["signal_id"], o["horizon_days"],
                o["stock_price_t0"], o["stock_price_t1"],
                o["benchmark_price_t0"], o["benchmark_price_t1"],
                o["stock_return"], o["benchmark_return"],
                o["excess_return"], o["correct"],
                o.get("transcript_date"),
                o.get("split_adjusted", 0),
            ),
        )
    conn.commit()
    conn.close()
    logger.info("Wrote %d outcomes", len(outcomes))


def resolve_ticker(ticker: str, *, force: bool = False) -> int:
    """Resolve outcomes for all signals of a given ticker.

    Returns the number of outcomes resolved.
    """
    conn = get_connection("signals")
    rows = conn.execute(
        "SELECT signal_id FROM signals WHERE ticker = ?", (ticker,)
    ).fetchall()
    conn.close()

    if not rows:
        logger.info("No signals found for %s", ticker)
        return 0

    outcome_conn = get_connection("outcomes")
    existing = set()
    for r in outcome_conn.execute("SELECT DISTINCT signal_id FROM outcomes").fetchall():
        existing.add(r["signal_id"])
    outcome_conn.close()

    total = 0
    for row in rows:
        sid = row["signal_id"]
        if sid in existing and not force:
            continue
        outcomes = resolve_signal(sid, force=force)
        total += len(outcomes)

    logger.info("Resolved %d outcomes for %s", total, ticker)
    return total


def resolve_all(*, force: bool = False) -> int:
    """Resolve outcomes for all unresolved signals."""
    conn = get_connection("signals")
    tickers = [r["ticker"] for r in conn.execute("SELECT DISTINCT ticker FROM signals").fetchall()]
    conn.close()

    total = 0
    for ticker in tickers:
        total += resolve_ticker(ticker, force=force)
    return total

"""Scorer: query signals+outcomes and compute per-reader and aggregate metrics."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from ecis.db.init_db import get_connection
from ecis.scoring.metrics import (
    brier_score,
    expected_calibration_error,
    murphy_decomposition,
    skill_score,
)

logger = logging.getLogger(__name__)


def _fetch_scored_data(
    ticker: str | None = None,
    source_method: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch joined signals+outcomes data."""
    conn_s = get_connection("signals")
    conn_o = get_connection("outcomes")

    query = "SELECT signal_id, ticker, direction, confidence_raw, source_method, llm_model, low_confidence FROM signals"
    params: list[Any] = []
    conditions = []

    if ticker:
        conditions.append("ticker = ?")
        params.append(ticker)
    if source_method:
        conditions.append("source_method = ?")
        params.append(source_method)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    try:
        signals = conn_s.execute(query, params).fetchall()
    except Exception:
        query = query.replace(", llm_model, low_confidence", "")
        signals = conn_s.execute(query, params).fetchall()
    conn_s.close()

    results = []
    for sig in signals:
        if "low_confidence" in sig.keys() and sig["low_confidence"]:
            continue
        outcomes = conn_o.execute(
            "SELECT horizon_days, correct, excess_return FROM outcomes WHERE signal_id = ?",
            (sig["signal_id"],),
        ).fetchall()

        for out in outcomes:
            if out["correct"] is not None:
                results.append({
                    "signal_id": sig["signal_id"],
                    "ticker": sig["ticker"],
                    "direction": sig["direction"],
                    "confidence": sig["confidence_raw"],
                    "source_method": sig["source_method"],
                    "llm_model": sig["llm_model"] if "llm_model" in sig.keys() else None,
                    "horizon_days": out["horizon_days"],
                    "correct": out["correct"],
                    "excess_return": out["excess_return"],
                })

    conn_o.close()
    return results


def score_reader(
    source_method: str | None = None,
    ticker: str | None = None,
    horizon: int | None = None,
) -> dict[str, Any]:
    """Compute all metrics for a specific reader (or all if None)."""
    data = _fetch_scored_data(ticker=ticker, source_method=source_method)

    if horizon:
        data = [d for d in data if d["horizon_days"] == horizon]

    if not data:
        return {
            "source_method": source_method or "all",
            "ticker": ticker or "all",
            "horizon": horizon or "all",
            "n_samples": 0,
            "brier": None,
            "skill_score": None,
            "ece": None,
            "murphy": None,
        }

    confidences = [d["confidence"] for d in data]
    outcomes = [d["correct"] for d in data]

    bs = brier_score(confidences, outcomes)
    base_rate = sum(outcomes) / len(outcomes)
    ref_brier = base_rate * (1 - base_rate)
    ss = skill_score(bs, ref_brier)
    ece, ece_bins = expected_calibration_error(confidences, outcomes)
    murphy = murphy_decomposition(confidences, outcomes)
    excess = [d["excess_return"] for d in data if d.get("excess_return") is not None]
    ir = None
    if len(excess) >= 2:
        std = float(np.std(excess))
        if std > 0:
            ir = round(float(np.mean(excess) / std), 6)

    return {
        "source_method": source_method or "all",
        "ticker": ticker or "all",
        "horizon": horizon or "all",
        "n_samples": len(data),
        "base_rate": round(base_rate, 4),
        "brier": round(bs, 6),
        "skill_score": round(ss, 6),
        "ece": ece,
        "ece_bins": ece_bins,
        "murphy": murphy,
        "information_ratio": ir,
    }


def score_all_readers(
    ticker: str | None = None,
    horizon: int | None = None,
) -> list[dict[str, Any]]:
    """Score all reader types individually plus aggregate."""
    readers = ["keyword", "finbert", "llm", "triangulated"]
    results = []

    for reader in readers:
        result = score_reader(source_method=reader, ticker=ticker, horizon=horizon)
        if result["n_samples"] > 0:
            results.append(result)

    aggregate = score_reader(source_method=None, ticker=ticker, horizon=horizon)
    aggregate["source_method"] = "aggregate"
    results.append(aggregate)

    return results


def score_by_llm_model(
    ticker: str | None = None,
    horizon: int | None = None,
) -> list[dict[str, Any]]:
    """Score signals grouped by llm_model alias (llama / mistral / qwen)."""
    from ecis.config.settings import settings

    data = _fetch_scored_data(ticker=ticker)
    if horizon:
        data = [d for d in data if d["horizon_days"] == horizon]

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in data:
        raw = row.get("llm_model") or ""
        alias = settings.model_alias(raw) if raw else "unknown"
        groups.setdefault(alias, []).append(row)

    results = []
    for alias, rows in sorted(groups.items()):
        confidences = [d["confidence"] for d in rows]
        outcomes = [d["correct"] for d in rows]
        bs = brier_score(confidences, outcomes)
        base_rate = sum(outcomes) / len(outcomes) if outcomes else 0.0
        ref_brier = base_rate * (1 - base_rate)
        ss = skill_score(bs, ref_brier)
        ece, _ = expected_calibration_error(confidences, outcomes)
        murphy = murphy_decomposition(confidences, outcomes)
        results.append({
            "llm_model": alias,
            "n_samples": len(rows),
            "brier": round(bs, 6),
            "skill_score": round(ss, 6),
            "ece": ece,
            "murphy": murphy,
        })
    return results


def print_scorecard(ticker: str | None = None, horizon: int | None = None) -> None:
    """Print a formatted scoring report."""
    results = score_all_readers(ticker=ticker, horizon=horizon)

    scope = f"Ticker: {ticker or 'ALL'} | Horizon: {horizon or 'ALL'} days"
    print(f"\n{'='*70}")
    print(f"  ECIS Scoring Report — {scope}")
    print(f"{'='*70}")
    print(f"  {'Reader':<15} {'N':>6} {'Brier':>8} {'Skill':>8} {'ECE':>8} {'Reliab':>8} {'Resol':>8}")
    print(f"  {'-'*15} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    for r in results:
        if r["n_samples"] == 0:
            continue
        murphy = r.get("murphy", {})
        print(
            f"  {r['source_method']:<15} {r['n_samples']:>6} "
            f"{r['brier']:>8.4f} {r['skill_score']:>8.4f} {r['ece']:>8.4f} "
            f"{murphy.get('reliability', 0):>8.4f} {murphy.get('resolution', 0):>8.4f}"
        )

    print(f"{'='*70}\n")

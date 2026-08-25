"""Dashboard data layer: query functions returning DataFrames for Streamlit."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from ecis.config.settings import settings


def _db_path(name: str) -> Path:
    return settings.db_dir / f"{name}.db"


def _connect(name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path(name)))
    conn.row_factory = sqlite3.Row
    return conn


def get_signals(
    ticker: str | None = None,
    direction: str | None = None,
    source_method: str | None = None,
    llm_model: str | None = None,
    limit: int = 500,
) -> pd.DataFrame:
    """Fetch signals as a DataFrame."""
    conn = _connect("signals")
    query = "SELECT * FROM signals"
    conditions = []
    params: list[Any] = []

    if ticker:
        conditions.append("ticker = ?")
        params.append(ticker)
    if direction:
        conditions.append("direction = ?")
        params.append(direction)
    if source_method:
        conditions.append("source_method = ?")
        params.append(source_method)
    if llm_model:
        conditions.append("llm_model LIKE ?")
        params.append(f"%{llm_model}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_outcomes(signal_ids: list[int] | None = None) -> pd.DataFrame:
    """Fetch outcomes as a DataFrame."""
    conn = _connect("outcomes")
    if signal_ids:
        placeholders = ",".join("?" * len(signal_ids))
        query = f"SELECT * FROM outcomes WHERE signal_id IN ({placeholders})"
        df = pd.read_sql_query(query, conn, params=signal_ids)
    else:
        df = pd.read_sql_query("SELECT * FROM outcomes", conn)
    conn.close()
    return df


def get_signals_with_outcomes(ticker: str | None = None) -> pd.DataFrame:
    """Join signals with outcomes for scoring views."""
    signals = get_signals(ticker=ticker, limit=10000)
    if signals.empty:
        return signals

    outcomes = get_outcomes(signal_ids=signals["signal_id"].tolist())
    if outcomes.empty:
        return signals

    merged = signals.merge(outcomes, on="signal_id", how="left", suffixes=("", "_out"))
    return merged


def get_agent_actions(agent_name: str | None = None, limit: int = 200) -> pd.DataFrame:
    """Fetch agent actions log."""
    conn = _connect("agents")
    query = "SELECT * FROM agent_actions"
    params: list[Any] = []

    if agent_name:
        query += " WHERE agent_name = ?"
        params.append(agent_name)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_reader_weights() -> pd.DataFrame:
    """Fetch current reader weights."""
    conn = _connect("agents")
    df = pd.read_sql_query("SELECT * FROM reader_weights", conn)
    conn.close()
    return df


def get_tickers() -> list[str]:
    """Get list of tickers from the registry, falling back to signals."""
    try:
        from ecis.db.ticker_registry import list_ticker_symbols

        symbols = list_ticker_symbols()
        if symbols:
            return symbols
    except Exception:
        pass

    conn = _connect("signals")
    try:
        rows = conn.execute("SELECT DISTINCT ticker FROM signals ORDER BY ticker").fetchall()
        return [r["ticker"] for r in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def get_summary_stats() -> dict[str, Any]:
    """Get high-level summary statistics."""
    conn_s = _connect("signals")
    try:
        total_signals = conn_s.execute("SELECT COUNT(*) as n FROM signals").fetchone()["n"]
        tickers = conn_s.execute("SELECT COUNT(DISTINCT ticker) as n FROM signals").fetchone()["n"]
        by_direction = dict(
            conn_s.execute(
                "SELECT direction, COUNT(*) as n FROM signals GROUP BY direction"
            ).fetchall()
        )
    except sqlite3.OperationalError:
        total_signals = 0
        tickers = 0
        by_direction = {}
    conn_s.close()

    conn_o = _connect("outcomes")
    try:
        total_outcomes = conn_o.execute("SELECT COUNT(*) as n FROM outcomes").fetchone()["n"]
    except sqlite3.OperationalError:
        total_outcomes = 0
    conn_o.close()

    return {
        "total_signals": total_signals,
        "total_tickers": tickers,
        "total_outcomes": total_outcomes,
        "by_direction": dict(by_direction),
    }


def get_pending_approvals() -> pd.DataFrame:
    """Pending HITL proposals as a DataFrame."""
    from ecis.db.approvals import list_pending

    rows = list_pending()
    if not rows:
        return pd.DataFrame()
    flat = []
    for r in rows:
        proposal = r.get("proposal") or {}
        evidence = r.get("evidence") or {}
        flat.append({
            "approval_id": r.get("approval_id"),
            "agent_name": r.get("agent_name"),
            "action_type": r.get("action_type"),
            "created_at": r.get("created_at"),
            "proposal": proposal,
            "evidence": evidence,
        })
    return pd.DataFrame(flat)


def get_ticker_registry() -> pd.DataFrame:
    from ecis.db.ticker_registry import list_tickers

    rows = list_tickers()
    return pd.DataFrame(rows) if rows else pd.DataFrame()

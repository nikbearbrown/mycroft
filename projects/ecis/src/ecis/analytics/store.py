"""Persist business-analytics snapshots in agents.db."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Iterable

from ecis.db.init_db import get_connection

TABLES = (
    "sector_sentiment",
    "sector_mood",
    "cross_sector_z",
    "management_confidence",
    "guidance_language",
    "ceo_cfo_divergence",
    "signal_price_corr",
    "surprise_analytics",
    "reaction_windows",
)


def _conn() -> sqlite3.Connection:
    return get_connection("agents")


def replace_rows(table: str, rows: Iterable[dict[str, Any]], columns: tuple[str, ...]) -> int:
    if table not in TABLES:
        raise ValueError(f"Unknown analytics table: {table}")
    conn = _conn()
    conn.execute(f"DELETE FROM {table}")
    n = 0
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    for row in rows:
        values = []
        for col in columns:
            val = row.get(col)
            if isinstance(val, (dict, list)):
                val = json.dumps(val)
            elif isinstance(val, bool):
                val = int(val)
            values.append(val)
        conn.execute(sql, values)
        n += 1
    conn.commit()
    conn.close()
    return n


def fetch_table(table: str, limit: int = 200) -> list[dict[str, Any]]:
    if table not in TABLES:
        raise ValueError(f"Unknown analytics table: {table}")
    conn = _conn()
    rows = conn.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

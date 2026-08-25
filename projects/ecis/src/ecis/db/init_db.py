"""Initialise the four SQLite databases used by ECIS."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ecis.config.settings import settings

_SIGNALS_SCHEMA = """
CREATE TABLE IF NOT EXISTS signals (
    signal_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker           TEXT    NOT NULL,
    direction        TEXT    NOT NULL CHECK (direction IN ('raised','lowered','maintained')),
    confidence_raw   REAL    NOT NULL CHECK (confidence_raw BETWEEN 0 AND 1),
    confidence_calibrated REAL CHECK (confidence_calibrated BETWEEN 0 AND 1),
    source_method    TEXT    NOT NULL,
    supporting_quote TEXT    NOT NULL,
    section_label    TEXT    NOT NULL,
    speaker          TEXT    DEFAULT '',
    transcript_date  TEXT    NOT NULL,
    chunk_index      INTEGER NOT NULL,
    char_start       INTEGER NOT NULL,
    char_end         INTEGER NOT NULL,
    reasoning_trace  TEXT,
    ner_entities     TEXT,          -- JSON-encoded dict
    self_consistency_votes TEXT,    -- JSON-encoded list
    verification_status TEXT,
    llm_model        TEXT,
    content_hash     TEXT,
    retry_count      INTEGER NOT NULL DEFAULT 0,
    provenance       TEXT,
    raw_llm_output   TEXT,
    low_confidence   INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_signals_ticker ON signals(ticker);
CREATE INDEX IF NOT EXISTS idx_signals_date   ON signals(transcript_date);
CREATE INDEX IF NOT EXISTS idx_signals_hash ON signals(ticker, transcript_date, content_hash);
"""

_OUTCOMES_SCHEMA = """
CREATE TABLE IF NOT EXISTS outcomes (
    outcome_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id        INTEGER NOT NULL,
    horizon_days     INTEGER NOT NULL CHECK (horizon_days IN (30, 90, 180)),
    stock_price_t0   REAL,
    stock_price_t1   REAL,
    benchmark_price_t0 REAL,
    benchmark_price_t1 REAL,
    stock_return     REAL,
    benchmark_return REAL,
    excess_return    REAL,
    correct          INTEGER,
    transcript_date  TEXT,
    split_adjusted   INTEGER NOT NULL DEFAULT 0,
    resolved_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(signal_id, horizon_days, transcript_date)
);

CREATE INDEX IF NOT EXISTS idx_outcomes_signal ON outcomes(signal_id);
"""

_AGENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_actions (
    action_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name       TEXT    NOT NULL,
    observation      TEXT    NOT NULL,
    action_taken     TEXT    NOT NULL,
    result           TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_agent_actions_agent ON agent_actions(agent_name);

CREATE TABLE IF NOT EXISTS reader_weights (
    reader_name      TEXT    PRIMARY KEY,
    weight           REAL    NOT NULL CHECK (weight BETWEEN 0 AND 1),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS escalation_thresholds (
    param_name       TEXT    PRIMARY KEY,
    value            REAL    NOT NULL,
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS vindication_records (
    record_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker           TEXT    NOT NULL,
    chunk_index      INTEGER NOT NULL,
    conflict_type    TEXT    NOT NULL,
    vindicated_reader TEXT   NOT NULL,
    defeated_reader  TEXT    NOT NULL,
    reasoning        TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

_CHECKPOINTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    graph_id         TEXT    NOT NULL,
    node_id          TEXT    NOT NULL,
    state_json       TEXT    NOT NULL,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_graph ON checkpoints(graph_id);
"""

_FILE_METADATA_SCHEMA = """
CREATE TABLE IF NOT EXISTS file_metadata (
    file_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker           TEXT    NOT NULL,
    filing_date      TEXT    NOT NULL,
    source           TEXT    NOT NULL CHECK (source IN ('edgar','fmp')),
    file_path        TEXT    NOT NULL UNIQUE,
    period_of_report TEXT,
    downloaded_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_file_meta_ticker ON file_metadata(ticker);
"""

_TICKERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS tickers (
    ticker                    TEXT PRIMARY KEY,
    company_name              TEXT NOT NULL DEFAULT '',
    sector                    TEXT NOT NULL DEFAULT 'AI',
    fiscal_calendar           TEXT NOT NULL DEFAULT 'calendar',
    transcript_source         TEXT NOT NULL DEFAULT 'both',
    total_transcripts         INTEGER NOT NULL DEFAULT 0,
    last_ingestion_date       TEXT,
    extraction_status         TEXT NOT NULL DEFAULT 'pending',
    outcome_resolution_status TEXT NOT NULL DEFAULT 'pending',
    updated_at                TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_CHUNK_CLASSIFICATIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS chunk_classifications (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker              TEXT    NOT NULL,
    transcript_date     TEXT,
    chunk_index         INTEGER NOT NULL,
    category            TEXT    NOT NULL,
    keyword_matched     INTEGER NOT NULL DEFAULT 0,
    keyword_confidence  REAL    NOT NULL DEFAULT 0,
    finbert_confidence  REAL    NOT NULL DEFAULT 0,
    finbert_direction   TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_chunk_class_ticker ON chunk_classifications(ticker);
CREATE INDEX IF NOT EXISTS idx_chunk_class_cat ON chunk_classifications(category);
"""

_PENDING_APPROVALS_SCHEMA = """
CREATE TABLE IF NOT EXISTS pending_approvals (
    approval_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name     TEXT    NOT NULL,
    action_type    TEXT    NOT NULL,
    proposal_json  TEXT    NOT NULL,
    evidence_json  TEXT,
    status         TEXT    NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending','approved','rejected')),
    created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    resolved_at    TEXT,
    resolution_note TEXT
);

CREATE INDEX IF NOT EXISTS idx_approvals_status ON pending_approvals(status);
"""

_CHUNK_REJECTIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS chunk_rejections (
    rejection_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker           TEXT,
    transcript_date  TEXT,
    chunk_index      INTEGER,
    reason           TEXT NOT NULL,
    token_count      INTEGER,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

DB_MAP: dict[str, str] = {
    "signals": _SIGNALS_SCHEMA,
    "outcomes": _OUTCOMES_SCHEMA,
    "agents": (
        _AGENTS_SCHEMA
        + _FILE_METADATA_SCHEMA
        + _TICKERS_SCHEMA
        + _CHUNK_CLASSIFICATIONS_SCHEMA
        + _PENDING_APPROVALS_SCHEMA
        + _CHUNK_REJECTIONS_SCHEMA
    ),
    "checkpoints": _CHECKPOINTS_SCHEMA,
}


def _db_path(name: str) -> Path:
    return settings.db_dir / f"{name}.db"


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def migrate_schema(conn: sqlite3.Connection, name: str) -> None:
    """Apply additive migrations to an existing database."""
    if name == "signals":
        try:
            _ensure_column(conn, "signals", "llm_model", "llm_model TEXT")
            _ensure_column(conn, "signals", "content_hash", "content_hash TEXT")
            _ensure_column(conn, "signals", "retry_count", "retry_count INTEGER NOT NULL DEFAULT 0")
            _ensure_column(conn, "signals", "provenance", "provenance TEXT")
            _ensure_column(conn, "signals", "raw_llm_output", "raw_llm_output TEXT")
            _ensure_column(conn, "signals", "low_confidence", "low_confidence INTEGER NOT NULL DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            pass
    elif name == "outcomes":
        try:
            _ensure_column(conn, "outcomes", "transcript_date", "transcript_date TEXT")
            _ensure_column(conn, "outcomes", "split_adjusted", "split_adjusted INTEGER NOT NULL DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            pass
    elif name == "agents":
        conn.executescript(_TICKERS_SCHEMA)
        conn.executescript(_CHUNK_CLASSIFICATIONS_SCHEMA)
        conn.executescript(_PENDING_APPROVALS_SCHEMA)
        conn.executescript(_CHUNK_REJECTIONS_SCHEMA)
        try:
            _ensure_column(conn, "file_metadata", "period_of_report", "period_of_report TEXT")
        except sqlite3.OperationalError:
            pass
        conn.commit()


_MIGRATED_PATHS: set[str] = set()


def init_database(name: str) -> None:
    path = _db_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.executescript(DB_MAP[name])
    migrate_schema(conn, name)
    conn.close()


def init_all() -> None:
    settings.ensure_dirs()
    _MIGRATED_PATHS.clear()
    for name in DB_MAP:
        init_database(name)
        print(f"  ✓ {_db_path(name)}")


def get_connection(name: str) -> sqlite3.Connection:
    path = _db_path(name)
    if not path.exists():
        init_database(name)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    key = str(path)
    if key not in _MIGRATED_PATHS:
        migrate_schema(conn, name)
        _MIGRATED_PATHS.add(key)
    return conn


def log_agent_action(
    agent_name: str,
    observation: str,
    action_taken: str,
    result: str | None = None,
) -> None:
    """Append a row to the agent audit log."""
    conn = get_connection("agents")
    conn.execute(
        """INSERT INTO agent_actions (agent_name, observation, action_taken, result)
           VALUES (?, ?, ?, ?)""",
        (agent_name, observation, action_taken, result),
    )
    conn.commit()
    conn.close()


def insert_default_weights() -> None:
    conn = get_connection("agents")
    defaults = [
        ("keyword", settings.weight_keyword),
        ("finbert", settings.weight_finbert),
        ("llm", settings.weight_llm),
        ("llm_llama", settings.weight_llm_llama),
        ("llm_mistral", settings.weight_llm_mistral),
        ("llm_qwen", settings.weight_llm_qwen),
        ("agreement", settings.weight_agreement),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO reader_weights (reader_name, weight) VALUES (?, ?)",
        defaults,
    )
    threshold_defaults = [
        ("finbert_confidence_min", 0.6),
        ("keyword_confidence_min", 0.5),
        ("escalation_agreement_threshold", 0.7),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO escalation_thresholds (param_name, value) VALUES (?, ?)",
        threshold_defaults,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Initialising ECIS databases…")
    init_all()
    insert_default_weights()
    print("Done.")

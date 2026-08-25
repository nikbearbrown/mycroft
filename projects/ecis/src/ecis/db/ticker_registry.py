"""Structured ticker registry"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from ecis.config.settings import settings
from ecis.db.init_db import get_connection, log_agent_action

logger = logging.getLogger(__name__)


def upsert_ticker(
    ticker: str,
    *,
    company_name: str | None = None,
    sector: str | None = None,
    fiscal_calendar: str | None = None,
    transcript_source: str | None = None,
    total_transcripts: int | None = None,
    last_ingestion_date: str | None = None,
    extraction_status: str | None = None,
    outcome_resolution_status: str | None = None,
) -> None:
    ticker = ticker.upper().strip()
    if not ticker:
        return

    conn = get_connection("agents")
    existing = conn.execute(
        "SELECT ticker FROM tickers WHERE ticker = ?", (ticker,)
    ).fetchone()

    if existing is None:
        conn.execute(
            """INSERT INTO tickers
               (ticker, company_name, sector, fiscal_calendar, transcript_source,
                total_transcripts, last_ingestion_date, extraction_status,
                outcome_resolution_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ticker,
                company_name or ticker,
                sector or "AI",
                fiscal_calendar or "calendar",
                transcript_source or "both",
                total_transcripts if total_transcripts is not None else 0,
                last_ingestion_date,
                extraction_status or "pending",
                outcome_resolution_status or "pending",
            ),
        )
    else:
        sets: list[str] = ["updated_at = datetime('now')"]
        params: list[object] = []
        updates = {
            "company_name": company_name,
            "sector": sector,
            "fiscal_calendar": fiscal_calendar,
            "transcript_source": transcript_source,
            "total_transcripts": total_transcripts,
            "last_ingestion_date": last_ingestion_date,
            "extraction_status": extraction_status,
            "outcome_resolution_status": outcome_resolution_status,
        }
        for col, value in updates.items():
            if value is not None:
                sets.append(f"{col} = ?")
                params.append(value)
        params.append(ticker)
        conn.execute(f"UPDATE tickers SET {', '.join(sets)} WHERE ticker = ?", params)

    conn.commit()
    conn.close()


def get_ticker(ticker: str) -> dict | None:
    conn = get_connection("agents")
    row = conn.execute(
        "SELECT * FROM tickers WHERE ticker = ?", (ticker.upper(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_tickers() -> list[dict]:
    conn = get_connection("agents")
    rows = conn.execute("SELECT * FROM tickers ORDER BY ticker").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_ticker_symbols() -> list[str]:
    return [r["ticker"] for r in list_tickers()]


def _count_raw_files(ticker: str) -> tuple[int, str | None, str]:
    """Return (count, latest date-ish name, sources present)."""
    sources: list[str] = []
    files: list[Path] = []
    for source, root in (
        ("edgar", settings.raw_edgar_dir / ticker),
        ("fmp", settings.raw_fmp_dir / ticker),
    ):
        if root.exists():
            found = [p for p in root.iterdir() if p.is_file()]
            if found:
                sources.append(source)
                files.extend(found)
    if not files:
        return 0, None, "both"
    latest = max(files, key=lambda p: p.stat().st_mtime)
    date_guess = latest.stem[:10] if len(latest.stem) >= 10 else str(date.today())
    source_label = "both" if len(sources) > 1 else (sources[0] if sources else "both")
    return len(files), date_guess, source_label


def migrate_from_directories() -> int:
    """Populate the ticker table from existing raw transcript directories."""
    seen: set[str] = set()
    for root in (settings.raw_edgar_dir, settings.raw_fmp_dir):
        if not root.exists():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir() and child.name.isalpha():
                seen.add(child.name.upper())

    try:
        conn = get_connection("signals")
        rows = conn.execute("SELECT DISTINCT ticker FROM signals").fetchall()
        conn.close()
        for row in rows:
            seen.add(row["ticker"].upper())
    except Exception:
        pass

    for ticker in sorted(seen):
        count, last_date, source = _count_raw_files(ticker)
        upsert_ticker(
            ticker,
            company_name=ticker,
            transcript_source=source,
            total_transcripts=count,
            last_ingestion_date=last_date,
        )

    log_agent_action(
        "ticker_registry",
        f"Scanned raw directories ({len(seen)} tickers)",
        "migrate_from_directories",
        f"{len(seen)} rows upserted",
    )
    logger.info("Migrated %d tickers into registry", len(seen))
    return len(seen)


def refresh_transcript_counts(ticker: str | None = None) -> None:
    symbols = [ticker.upper()] if ticker else list_ticker_symbols()
    if ticker and not get_ticker(ticker):
        symbols = [ticker.upper()]
        upsert_ticker(ticker)
    for sym in symbols:
        count, last_date, source = _count_raw_files(sym)
        upsert_ticker(
            sym,
            total_transcripts=count,
            last_ingestion_date=last_date,
            transcript_source=source,
        )


def mark_extraction(ticker: str, status: str = "complete") -> None:
    upsert_ticker(ticker, extraction_status=status)


def mark_outcomes(ticker: str, status: str = "complete") -> None:
    upsert_ticker(ticker, outcome_resolution_status=status)

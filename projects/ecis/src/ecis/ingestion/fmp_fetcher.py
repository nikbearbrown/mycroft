"""Financial Modeling Prep earnings call transcript fetcher with daily limit tracking."""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

import requests

from ecis.config.settings import settings
from ecis.db.init_db import get_connection

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"


class DailyLimitTracker:
    def __init__(self, daily_limit: int = 250):
        self._limit = daily_limit
        self._count = 0
        self._date = date.today()

    def _reset_if_new_day(self) -> None:
        if date.today() != self._date:
            self._count = 0
            self._date = date.today()

    @property
    def remaining(self) -> int:
        self._reset_if_new_day()
        return self._limit - self._count

    def consume(self) -> bool:
        self._reset_if_new_day()
        if self._count >= self._limit:
            return False
        self._count += 1
        return True


_tracker = DailyLimitTracker(settings.fmp_daily_limit)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    return s


def fetch_transcript_list(ticker: str) -> list[dict]:
    if not settings.fmp_api_key:
        logger.error("FMP_API_KEY not configured")
        return []

    if not _tracker.consume():
        logger.warning("FMP daily limit (%d) exhausted", settings.fmp_daily_limit)
        return []

    session = _session()
    url = f"{FMP_BASE_URL}/earning_call_transcript"
    params = {"symbol": ticker, "apikey": settings.fmp_api_key}

    try:
        resp = session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error("FMP transcript list failed for %s: %s", ticker, exc)
        return []

    if isinstance(data, list):
        return data
    return []


def download_transcript(ticker: str, quarter: int, year: int) -> Path | None:
    """Download a single earnings call transcript from FMP."""
    if not settings.fmp_api_key:
        logger.error("FMP_API_KEY not configured")
        return None

    if not _tracker.consume():
        logger.warning("FMP daily limit (%d) exhausted", settings.fmp_daily_limit)
        return None

    out_dir = settings.raw_fmp_dir / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{year}_Q{quarter}.json"

    if out_path.exists():
        logger.debug("Already cached: %s", out_path)
        return out_path

    session = _session()
    url = f"{FMP_BASE_URL}/earning_call_transcript/{ticker}"
    params = {"quarter": quarter, "year": year, "apikey": settings.fmp_api_key}

    try:
        resp = session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error("FMP download failed for %s Q%d %d: %s", ticker, quarter, year, exc)
        return None

    if not data:
        logger.warning("Empty transcript for %s Q%d %d", ticker, quarter, year)
        return None

    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    transcript_date = f"{year}-{quarter * 3:02d}-01"
    _record_metadata(ticker, transcript_date, str(out_path), "fmp")
    logger.info("Downloaded FMP transcript → %s", out_path)
    return out_path


def _record_metadata(ticker: str, filing_date: str, file_path: str, source: str) -> None:
    conn = get_connection("agents")
    conn.execute(
        """INSERT OR IGNORE INTO file_metadata (ticker, filing_date, source, file_path)
           VALUES (?, ?, ?, ?)""",
        (ticker, filing_date, source, file_path),
    )
    conn.commit()
    conn.close()


def fetch_transcripts(
    tickers: list[str],
    *,
    years: list[int] | None = None,
    quarters: list[int] | None = None,
) -> list[Path]:
    """Fetch all available transcripts for a list of tickers.

    Returns paths to successfully downloaded files.
    """
    settings.ensure_dirs()
    if years is None:
        years = [2023, 2024, 2025]
    if quarters is None:
        quarters = [1, 2, 3, 4]

    downloaded: list[Path] = []

    for ticker in tickers:
        logger.info("Fetching FMP transcripts for %s …", ticker)
        for year in years:
            for quarter in quarters:
                if _tracker.remaining <= 0:
                    logger.warning("Daily limit reached, stopping")
                    return downloaded
                path = download_transcript(ticker, quarter, year)
                if path:
                    downloaded.append(path)

    return downloaded

"""Thin, polite EDGAR client with on-disk caching (standard library only).

Reflects the project's "evidence before interpretation" principle:
  * Every raw SEC response is cached verbatim in data/raw/ with a fetch
    timestamp, so any downstream number can be traced back to exactly what
    the SEC returned and re-derived offline.
  * Requests are rate-limited and carry the SEC-required User-Agent.
"""
from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config


class EdgarClient:
    def __init__(self, user_agent: str | None = None) -> None:
        self.user_agent = user_agent or config.USER_AGENT
        self._last_request_ts = 0.0

    # -- low-level -----------------------------------------------------------
    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_ts
        wait = config.MIN_REQUEST_INTERVAL - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_ts = time.monotonic()

    def _fetch(self, url: str) -> Any:
        self._throttle()
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _get_json(self, url: str, cache_path: Path | None = None) -> Any:
        if cache_path and cache_path.exists() and self._cache_fresh(cache_path):
            with cache_path.open() as fh:
                return json.load(fh)["data"]
        data = self._fetch(url)
        if cache_path is not None:
            envelope = {
                "_provenance": {
                    "source_url": url,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                },
                "data": data,
            }
            cache_path.write_text(json.dumps(envelope))
        return data

    @staticmethod
    def _cache_fresh(path: Path) -> bool:
        if config.CACHE_TTL_HOURS <= 0:
            return True
        age_hours = (time.time() - path.stat().st_mtime) / 3600
        return age_hours <= config.CACHE_TTL_HOURS

    # -- public API ----------------------------------------------------------
    def ticker_to_cik(self, ticker: str) -> str:
        """Resolve a ticker to a 10-digit zero-padded CIK string."""
        cache = config.RAW_DIR / "company_tickers.json"
        data = self._get_json(config.TICKER_MAP_URL, cache)
        wanted = ticker.upper().strip()
        for row in data.values():
            if str(row["ticker"]).upper() == wanted:
                return f"{int(row['cik_str']):010d}"
        raise ValueError(f"Ticker {ticker!r} not found in SEC ticker map")

    def company_facts(self, cik10: str) -> dict[str, Any]:
        cache = config.RAW_DIR / f"companyfacts_CIK{cik10}.json"
        return self._get_json(config.COMPANY_FACTS_URL.format(cik10=cik10), cache)

    def submissions(self, cik10: str) -> dict[str, Any]:
        cache = config.RAW_DIR / f"submissions_CIK{cik10}.json"
        return self._get_json(config.SUBMISSIONS_URL.format(cik10=cik10), cache)

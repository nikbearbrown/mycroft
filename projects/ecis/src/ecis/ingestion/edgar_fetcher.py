from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from ecis.config.settings import settings
from ecis.db.init_db import get_connection

logger = logging.getLogger(__name__)

EFTS_URL = "https://efts.sec.gov/LATEST/search-index"
SUBMISSIONS_URL = "https://data.sec.gov/submissions"
ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"


class RateLimiter:
    def __init__(self, max_per_second: int = 10):
        self._interval = 1.0 / max_per_second
        self._last_call = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_call
        if elapsed < self._interval:
            time.sleep(self._interval - elapsed)
        self._last_call = time.monotonic()


_limiter = RateLimiter(settings.edgar_requests_per_second)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": settings.edgar_user_agent,
        "Accept-Encoding": "gzip, deflate",
        "Accept": "application/json",
    })
    return s


_TICKER_CIK_CACHE: dict[str, str] = {}


def _load_ticker_map() -> dict[str, str]:
    if _TICKER_CIK_CACHE:
        return _TICKER_CIK_CACHE

    session = _session()
    _limiter.wait()
    try:
        resp = session.get("https://www.sec.gov/files/company_tickers.json", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for entry in data.values():
            ticker = entry.get("ticker", "").upper()
            cik = str(entry.get("cik_str", ""))
            if ticker and cik:
                _TICKER_CIK_CACHE[ticker] = cik.zfill(10)
    except requests.RequestException as exc:
        logger.error("Failed to load ticker→CIK map: %s", exc)

    return _TICKER_CIK_CACHE


def ticker_to_cik(ticker: str) -> str | None:
    mapping = _load_ticker_map()
    return mapping.get(ticker.upper())


def get_8k_filings(ticker: str, *, max_results: int = 40) -> list[dict]:
    cik = ticker_to_cik(ticker)
    if not cik:
        logger.error("Could not resolve CIK for ticker %s", ticker)
        return []

    session = _session()
    _limiter.wait()
    try:
        resp = session.get(f"{SUBMISSIONS_URL}/CIK{cik}.json", timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error("Submissions API failed for %s: %s", ticker, exc)
        return []

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    descriptions = recent.get("primaryDocDescription", [])

    results = []
    for i in range(min(len(forms), max_results * 5)):
        if forms[i] != "8-K":
            continue
        report_date = report_dates[i] if i < len(report_dates) and report_dates[i] else dates[i]
        results.append({
            "filing_date": dates[i],
            "report_date": report_date,
            "accession": accessions[i],
            "primary_doc": primary_docs[i],
            "description": descriptions[i] if i < len(descriptions) else "",
            "ticker": ticker,
            "cik": cik.lstrip("0"),
        })
        if len(results) >= max_results:
            break

    return results


def _filing_index_url(cik: str, accession: str) -> str:
    accession_clean = accession.replace("-", "")
    return f"{ARCHIVES_URL}/{cik}/{accession_clean}"


def _download_filing_exhibits(filing: dict) -> list[Path]:
    ticker = filing["ticker"]
    cik = filing["cik"]
    accession = filing["accession"]
    filing_date = filing["filing_date"]
    report_date = filing.get("report_date") or filing_date
    primary_doc = filing["primary_doc"]

    out_dir = settings.raw_edgar_dir / ticker
    out_dir.mkdir(parents=True, exist_ok=True)

    base_url = _filing_index_url(cik, accession)
    session = _session()
    downloaded = []

    primary_path = out_dir / f"{filing_date}_{primary_doc}"
    if not primary_path.exists():
        _limiter.wait()
        try:
            url = f"{base_url}/{primary_doc}"
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            primary_path.write_text(resp.text, encoding="utf-8")
            downloaded.append(primary_path)
            logger.info("Downloaded %s → %s", url, primary_path)
        except requests.RequestException as exc:
            logger.error("Failed to download primary doc %s: %s", primary_doc, exc)
    else:
        downloaded.append(primary_path)

    try:
        html = primary_path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()

            is_exhibit = (
                "exhibit" in link_text
                or "press release" in link_text
                or "commentary" in link_text
                or "transcript" in link_text
                or "ex99" in href.lower()
                or "exhibit" in href.lower()
            )
            if not is_exhibit:
                continue

            filename = href.split("/")[-1] if "/" in href else href
            if not filename.endswith((".htm", ".html", ".txt")):
                continue

            exhibit_path = out_dir / f"{filing_date}_{filename}"
            if exhibit_path.exists():
                downloaded.append(exhibit_path)
                continue

            exhibit_url = f"{base_url}/{filename}" if not href.startswith("http") else href
            _limiter.wait()
            try:
                resp = session.get(exhibit_url, timeout=30)
                resp.raise_for_status()
                exhibit_path.write_text(resp.text, encoding="utf-8")
                downloaded.append(exhibit_path)
                logger.info("Downloaded exhibit %s → %s", exhibit_url, exhibit_path)
            except requests.RequestException:
                pass

    except Exception as exc:
        logger.debug("Could not parse exhibits from %s: %s", primary_path, exc)

    for p in downloaded:
        _record_metadata(ticker, filing_date, str(p), "edgar", period_of_report=report_date)

    return downloaded


def search_efts(
    query: str,
    *,
    forms: str = "8-K",
    start_date: str | None = None,
    end_date: str | None = None,
    cik: str | None = None,
    max_results: int = 100,
) -> list[dict]:
    """Search EDGAR full-text search index.

    Returns list of dicts with: file_date, form, display_name, accession, file_id, cik.
    """
    session = _session()
    results = []
    offset = 0

    while offset < max_results:
        params: dict = {"q": query, "from": offset}
        if forms:
            params["forms"] = forms
        if start_date and end_date:
            params["dateRange"] = "custom"
            params["startdt"] = start_date
            params["enddt"] = end_date
        if cik:
            params["ciks"] = cik

        _limiter.wait()
        try:
            resp = session.get(EFTS_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.error("EFTS search failed: %s", exc)
            break

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break

        for hit in hits:
            src = hit.get("_source", {})
            file_id = hit.get("_id", "")
            results.append({
                "file_date": src.get("file_date", ""),
                "form": src.get("form", ""),
                "display_name": (src.get("display_names") or ["Unknown"])[0],
                "accession": src.get("adsh", ""),
                "file_id": file_id,
                "cik": (src.get("ciks") or [""])[0].lstrip("0"),
            })

        offset += len(hits)
        if len(hits) < 10:
            break

    logger.info("EFTS search '%s': %d results", query[:50], len(results))
    return results[:max_results]


def download_efts_result(result: dict, ticker: str) -> Path | None:
    file_id = result.get("file_id", "")
    if ":" not in file_id:
        return None

    accession, filename = file_id.split(":", 1)
    cik = result.get("cik", "").lstrip("0")
    filing_date = result.get("file_date", "unknown")

    if not cik or not filename:
        return None

    out_dir = settings.raw_edgar_dir / ticker
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{filing_date}_{filename}"

    if out_path.exists():
        return out_path

    accession_clean = accession.replace("-", "")
    url = f"{ARCHIVES_URL}/{cik}/{accession_clean}/{filename}"

    session = _session()
    _limiter.wait()
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Download failed for %s: %s", url, exc)
        return None

    out_path.write_text(resp.text, encoding="utf-8")
    _record_metadata(
        ticker,
        filing_date,
        str(out_path),
        "edgar",
        period_of_report=filing_date,
    )
    logger.info("Downloaded %s → %s", url, out_path)
    return out_path


def _record_metadata(
    ticker: str,
    filing_date: str,
    file_path: str,
    source: str,
    period_of_report: str | None = None,
) -> None:
    try:
        conn = get_connection("agents")
        conn.execute(
            """INSERT INTO file_metadata (ticker, filing_date, source, file_path, period_of_report)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(file_path) DO UPDATE SET
                 period_of_report = COALESCE(excluded.period_of_report, file_metadata.period_of_report)""",
            (ticker, filing_date, source, file_path, period_of_report),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.debug("Metadata recording failed: %s", exc)


def fetch_transcripts(
    tickers: list[str],
    *,
    max_per_ticker: int = 20,
) -> list[Path]:
    """Fetch earnings-related filings for a list of tickers.

    Strategy:
      1. For each ticker, get their 8-K filings via the submissions API
      2. Download the 8-K and its exhibits (press releases, CFO commentary, transcripts)
      3. Also search EFTS for any full-text matches for "[ticker] earnings call"

    Returns paths to all successfully downloaded files.
    """
    settings.ensure_dirs()
    downloaded: list[Path] = []

    for ticker in tickers:
        logger.info("Fetching EDGAR filings for %s …", ticker)

        filings = get_8k_filings(ticker, max_results=max_per_ticker)
        logger.info("  Found %d 8-K filings for %s via submissions API", len(filings), ticker)

        for filing in filings:
            paths = _download_filing_exhibits(filing)
            downloaded.extend(paths)

        efts_results = search_efts(
            f'"{ticker}" "earnings call"',
            forms="8-K",
            max_results=max_per_ticker,
        )
        logger.info("  Found %d EFTS results for %s", len(efts_results), ticker)

        for result in efts_results:
            path = download_efts_result(result, ticker)
            if path:
                downloaded.append(path)

    seen = set()
    unique = []
    for p in downloaded:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    logger.info("Total: %d unique files downloaded", len(unique))
    return unique

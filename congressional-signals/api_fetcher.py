"""
api_fetcher.py — Fetch congressional trading data via Financial Modeling Prep API
Outputs: data/trades.csv  (same format as scraper.py)

FMP has free Senate + House trading endpoints requiring a free API key.
Get one at: https://financialmodelingprep.com/developer/docs (free tier = 250 req/day)

Usage:
    export FMP_API_KEY=your_key_here        # or set in .env
    python api_fetcher.py                   # fetch recent trades (all tickers)
    python api_fetcher.py --ticker AAPL     # trades for a specific stock
    python api_fetcher.py --pages 5         # how many pages to fetch per chamber

Why use this over the scraper?
  - No Selenium / Chrome required
  - Structured JSON (no brittle CSS selectors)
  - Includes both Senate and House trades
  - Rate-limit safe with built-in backoff
"""

import argparse
import csv
import logging
import os
import time
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
OUTPUT = DATA_DIR / "trades.csv"

FMP_BASE = "https://financialmodelingprep.com/api/v4"

COLUMNS = [
    "politician",
    "ticker",
    "asset_name",
    "trade_type",
    "transaction_date",
    "disclosure_date",
    "amount_range",
    "chamber",   # extra: "senate" or "house"
    "party",     # extra: D / R / I
    "state",     # extra: state code
]

# FMP field name → our field name for Senate endpoint
SENATE_MAP = {
    "senator":          "politician",
    "asset":            "ticker",
    "assetDescription": "asset_name",
    "type":             "trade_type",
    "transactionDate":  "transaction_date",
    "disclosureDate":   "disclosure_date",
    "amount":           "amount_range",
    "party":            "party",
    "state":            "state",
}

# FMP field name → our field name for House endpoint
HOUSE_MAP = {
    "representative":   "politician",
    "ticker":           "ticker",
    "assetDescription": "asset_name",
    "type":             "trade_type",
    "transactionDate":  "transaction_date",
    "disclosureDate":   "disclosure_date",
    "amount":           "amount_range",
    "party":            "party",
    "state":            "state",
}


def get_api_key() -> str:
    key = os.environ.get("FMP_API_KEY", "").strip()
    if not key:
        # Try loading from a local .env file
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("FMP_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        raise EnvironmentError(
            "FMP_API_KEY not set.\n"
            "  1. Get a free key at https://financialmodelingprep.com/developer/docs\n"
            "  2. Set it:  export FMP_API_KEY=your_key\n"
            "     OR create a .env file with:  FMP_API_KEY=your_key"
        )
    return key


def _get(url: str, params: dict, retries: int = 3) -> list[dict]:
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 429:
                wait = 60 * (attempt + 1)
                log.warning("Rate limited — waiting %ds", wait)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            # FMP wraps results in different shapes depending on endpoint
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return []
        except requests.RequestException as e:
            log.warning("Request error (attempt %d/%d): %s", attempt + 1, retries, e)
            time.sleep(2 ** attempt)
    return []


def fetch_senate(api_key: str, ticker: str = "", page: int = 0) -> list[dict]:
    params = {"apikey": api_key, "page": page}
    if ticker:
        params["symbol"] = ticker.upper()
    url = f"{FMP_BASE}/senate-trading"
    return _get(url, params)


def fetch_house(api_key: str, ticker: str = "", page: int = 0) -> list[dict]:
    params = {"apikey": api_key, "page": page}
    if ticker:
        params["symbol"] = ticker.upper()
    url = f"{FMP_BASE}/house-trading"
    return _get(url, params)


def normalize_senate(raw: dict) -> dict:
    row = {col: "" for col in COLUMNS}
    row["chamber"] = "senate"
    for src, dst in SENATE_MAP.items():
        row[dst] = str(raw.get(src, "") or "")
    # Senator field may include title: "Sen. John Smith (D-CA)" — clean it
    row["politician"] = _clean_name(row["politician"])
    # Ticker in senate endpoint is in 'asset' which might be a company name
    # FMP sometimes returns a description; try the 'symbol' field too
    if not _looks_like_ticker(row["ticker"]):
        row["ticker"] = str(raw.get("symbol", "") or "")
    return row


def normalize_house(raw: dict) -> dict:
    row = {col: "" for col in COLUMNS}
    row["chamber"] = "house"
    for src, dst in HOUSE_MAP.items():
        row[dst] = str(raw.get(src, "") or "")
    row["politician"] = _clean_name(row["politician"])
    return row


def _looks_like_ticker(s: str) -> bool:
    s = s.strip()
    return bool(s) and len(s) <= 5 and s.isalpha()


def _clean_name(name: str) -> str:
    """Remove titles like 'Sen.' / 'Rep.' and party/state suffixes."""
    import re
    name = re.sub(r"^(Sen\.|Rep\.|Senator|Representative)\s+", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*\([A-Z]-[A-Z]{2}\)$", "", name)  # e.g. (D-CA)
    return name.strip()


def fetch_all(api_key: str, ticker: str = "", max_pages: int = 10) -> list[dict]:
    all_trades: list[dict] = []
    seen: set[tuple] = set()

    for chamber, fetch_fn, norm_fn in [
        ("Senate", fetch_senate, normalize_senate),
        ("House",  fetch_house,  normalize_house),
    ]:
        log.info("Fetching %s trades...", chamber)
        for page in range(max_pages):
            raw_rows = fetch_fn(api_key, ticker=ticker, page=page)
            if not raw_rows:
                log.info("  %s page %d: no data — stopping", chamber, page)
                break

            new = 0
            for raw in raw_rows:
                row = norm_fn(raw)
                key = (row["politician"], row["ticker"], row["transaction_date"])
                if key not in seen:
                    seen.add(key)
                    all_trades.append(row)
                    new += 1

            log.info("  %s page %d: %d new trades (total %d)", chamber, page, new, len(all_trades))
            if new == 0:
                break
            time.sleep(0.3)  # be polite to the API

    return all_trades


def save(trades: list[dict], path: Path = OUTPUT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(trades)
    log.info("Saved %d trades → %s", len(trades), path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch congressional trades via FMP API")
    parser.add_argument("--ticker", default="", help="Filter by stock ticker (e.g. AAPL)")
    parser.add_argument("--pages", type=int, default=10, help="Max pages per chamber (default 10)")
    parser.add_argument("--out", default=str(OUTPUT), help="Output CSV path")
    args = parser.parse_args()

    api_key = get_api_key()
    trades = fetch_all(api_key, ticker=args.ticker, max_pages=args.pages)

    if not trades:
        log.error("No trades fetched. Check your API key and network connection.")
        return

    save(trades, Path(args.out))
    log.info("Done. Run enricher.py next to add price data.")

    # Quick preview
    log.info("\nSample trades:")
    for t in trades[:5]:
        log.info(
            "  %s | %s | %s | %s | %s",
            t["politician"], t["ticker"], t["trade_type"],
            t["transaction_date"], t["amount_range"],
        )


if __name__ == "__main__":
    main()

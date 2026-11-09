# =============================================================================
# Week 6 deliverable (part 1 of 2) — price history for the signal-validation
# backtest.
#
# Pulls daily closing prices from Alpha Vantage for every watchlist entity that
# has a public ticker (9 of 12; the 3 private comparables have ticker=null and
# are non-investable, so there is no price to fetch). The backtest only needs a
# price at each of the 13 weekly backfill run_dates, so daily bars with
# outputsize=compact (~100 trading days, back to ~Feb 2026) more than cover the
# 2026-04-11 -> 2026-07-03 window.
#
# WHY Alpha Vantage free tier is handled carefully:
#   - Free tier caps at ~25 requests/day and ~5 requests/minute. We make only 9
#     calls, but we still throttle (default 15s apart) so a single run stays
#     under 5/min, and we CACHE per-ticker so re-runs (or a run that dies mid-way)
#     never re-spend the daily budget on tickers already fetched.
#   - Alpha Vantage signals throttling/errors in the JSON body (keys "Note",
#     "Information", or "Error Message") with an HTTP 200, so we inspect the body
#     rather than trusting the status code.
#
# Run: python fetch_prices.py [--delay 15] [--force] [--outputsize compact|full]
# Needs ALPHA_VANTAGE_API_KEY in .env. Writes backfill_output/prices_v1.json:
#   { "NVDA": { "2026-04-10": 118.42, ... }, ... }  (date -> adjusted-agnostic close)
# =============================================================================

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

AV_URL = "https://www.alphavantage.co/query"
DEFAULT_DELAY_SEC = 15  # keeps 9 calls under the 5-requests/minute free-tier cap

load_dotenv()
BASE_DIR = Path(__file__).parent
WATCHLIST_PATH = BASE_DIR / "watchlist.json"
OUTPUT_DIR = BASE_DIR / "backfill_output"
OUTPUT_PATH = OUTPUT_DIR / "prices_v1.json"


def public_tickers():
    """Return the sorted list of tickers for watchlist entities that have one."""
    watchlist = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
    return sorted({e["ticker"] for e in watchlist if e.get("ticker")})


def fetch_daily(ticker, api_key, outputsize):
    """Fetch {date: close} for one ticker, raising on any Alpha Vantage error."""
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": outputsize,
        "apikey": api_key,
    }
    resp = requests.get(AV_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Alpha Vantage reports problems in the body with HTTP 200 — inspect it.
    if "Error Message" in data:
        raise RuntimeError(f"{ticker}: {data['Error Message']}")
    if "Note" in data:
        raise RuntimeError(f"{ticker}: rate-limited — {data['Note']}")
    if "Information" in data:
        raise RuntimeError(f"{ticker}: {data['Information']}")

    series = data.get("Time Series (Daily)")
    if not series:
        raise RuntimeError(f"{ticker}: unexpected response shape — keys={list(data)}")

    return {date: float(bar["4. close"]) for date, bar in series.items()}


def main():
    ap = argparse.ArgumentParser(description="Fetch daily prices for public-ticker watchlist entities.")
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY_SEC,
                    help="seconds between API calls (default 15, to respect 5 req/min free tier)")
    ap.add_argument("--outputsize", choices=["compact", "full"], default="compact",
                    help="compact=~100 trading days (enough for the 13-week window); full=20+ years")
    ap.add_argument("--force", action="store_true",
                    help="re-fetch every ticker even if already cached in prices_v1.json")
    args = ap.parse_args()

    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        sys.exit("ERROR: ALPHA_VANTAGE_API_KEY not set in .env")

    tickers = public_tickers()
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load any prior cache so a resumed run never re-spends the daily API budget.
    prices = {}
    if OUTPUT_PATH.exists() and not args.force:
        prices = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    to_fetch = [t for t in tickers if args.force or t not in prices]
    print(f"{len(tickers)} public tickers; {len(to_fetch)} to fetch "
          f"({len(tickers) - len(to_fetch)} already cached).")

    for i, ticker in enumerate(to_fetch):
        try:
            prices[ticker] = fetch_daily(ticker, api_key, args.outputsize)
            print(f"  [{i + 1}/{len(to_fetch)}] {ticker}: {len(prices[ticker])} daily closes")
        except Exception as exc:  # noqa: BLE001 — surface any failure, keep prior cache
            print(f"  [{i + 1}/{len(to_fetch)}] {ticker}: FAILED — {exc}")
            # Persist whatever we have so far so partial progress is not lost.
            OUTPUT_PATH.write_text(json.dumps(prices, indent=2), encoding="utf-8")
            sys.exit(f"Stopping — resolve the error above and re-run (cache preserved). ")

        # Throttle between successful calls (skip the wait after the last one).
        if i < len(to_fetch) - 1:
            time.sleep(args.delay)

    OUTPUT_PATH.write_text(json.dumps(prices, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} ({len(prices)} tickers).")


if __name__ == "__main__":
    main()

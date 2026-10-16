"""
enricher.py — Enrich trades.csv with Yahoo Finance price data
Outputs: data/enriched_trades.csv

For each trade with a valid ticker:
  - price_30d_pre_trade:        close 30 calendar days before transaction
  - price_at_trade:             close on transaction date (or nearest prior trading day)
  - pct_change_pre_trade:       % change from 30d-pre to trade date
  - price_at_disclosure:        close on disclosure date
  - price_30d_post_disclosure:  close 30 calendar days after disclosure
  - pct_change_post_disclosure: % change from disclosure date to 30d-post
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
INPUT = DATA_DIR / "trades.csv"
OUTPUT = DATA_DIR / "enriched_trades.csv"

# Try these date formats in order when parsing scraped date strings
DATE_FORMATS = [
    "%Y-%m-%d",
    "%b %d, %Y",    # Jan 15, 2024
    "%B %d, %Y",    # January 15, 2024
    "%m/%d/%Y",     # 01/15/2024
    "%m/%d/%y",     # 01/15/24
    "%d %b %Y",     # 15 Jan 2024
]

PRICE_COLS = [
    "price_30d_pre_trade",
    "price_at_trade",
    "pct_change_pre_trade",
    "price_at_disclosure",
    "price_30d_post_disclosure",
    "pct_change_post_disclosure",
]

# In-memory cache: (ticker, date_str) -> float | None
_price_cache: dict[tuple[str, str], float | None] = {}


def parse_date(s: str) -> datetime | None:
    s = s.strip()
    if not s:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    log.debug("Could not parse date: %r", s)
    return None


def clean_ticker(ticker: str) -> str:
    """Strip exchange suffixes like ':US', ':XNYS', '.US' and whitespace."""
    import re
    ticker = ticker.strip().upper()
    ticker = re.sub(r"[:.][A-Z]{2,4}$", "", ticker)
    return ticker


def is_valid_equity_ticker(ticker: str) -> bool:
    """
    Rough filter: skip options (contain '/'), crypto-like symbols (>5 chars
    with digits), blank, or common non-stock prefixes.
    """
    if not ticker:
        return False
    if "/" in ticker:        # options (e.g. AAPL/Jan25...)
        return False
    if len(ticker) > 5:
        return False
    if any(c.isdigit() for c in ticker):
        return False
    return True


def get_close(ticker: str, date: datetime) -> float | None:
    """
    Fetch the closing price on `date` or the nearest prior trading day
    (looks back up to 7 calendar days to skip weekends/holidays).
    Returns None on any error or if no data is available.
    """
    key = (ticker, date.strftime("%Y-%m-%d"))
    if key in _price_cache:
        return _price_cache[key]

    start = (date - timedelta(days=7)).strftime("%Y-%m-%d")
    end = (date + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        df = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=True,
        )
        if df.empty:
            _price_cache[key] = None
            return None
        price = float(df["Close"].iloc[-1])
        _price_cache[key] = price
        return price
    except Exception as exc:
        log.debug("yfinance error %s @ %s: %s", ticker, date.date(), exc)
        _price_cache[key] = None
        return None


def pct(before: float | None, after: float | None) -> float | None:
    if before is None or after is None or before == 0.0:
        return None
    return round((after - before) / before * 100, 4)


def enrich_row(row: dict) -> dict:
    out = {**row, **{col: None for col in PRICE_COLS}}

    ticker = clean_ticker(row.get("ticker", ""))
    out["ticker"] = ticker  # write cleaned ticker back
    if not is_valid_equity_ticker(ticker):
        return out

    t_date = parse_date(row.get("transaction_date", ""))
    d_date = parse_date(row.get("disclosure_date", ""))

    if t_date:
        p_pre   = get_close(ticker, t_date - timedelta(days=30))
        p_trade = get_close(ticker, t_date)
        out["price_30d_pre_trade"] = p_pre
        out["price_at_trade"]      = p_trade
        out["pct_change_pre_trade"] = pct(p_pre, p_trade)

    if d_date:
        p_disc = get_close(ticker, d_date)
        p_post = get_close(ticker, d_date + timedelta(days=30))
        out["price_at_disclosure"]        = p_disc
        out["price_30d_post_disclosure"]  = p_post
        out["pct_change_post_disclosure"] = pct(p_disc, p_post)

    return out


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(
            f"{INPUT} not found — run scraper.py first"
        )

    raw = pd.read_csv(INPUT, dtype=str, encoding="utf-8", on_bad_lines="skip").fillna("")
    log.info("Loaded %d rows from %s", len(raw), INPUT)

    records = raw.to_dict("records")
    enriched = []
    skip_count = 0

    for i, row in enumerate(records, 1):
        ticker = clean_ticker(row.get("ticker", ""))
        label = ticker or "(no ticker)"
        if not is_valid_equity_ticker(ticker):
            skip_count += 1
        else:
            log.info("[%d/%d] %s — %s", i, len(records), label, row.get("politician", ""))

        enriched.append(enrich_row(row))

    log.info("Skipped %d rows with invalid/missing tickers", skip_count)

    df_out = pd.DataFrame(enriched)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUTPUT, index=False)
    log.info("Saved enriched data → %s", OUTPUT)

    # Quick summary stats
    numeric_cols = [c for c in PRICE_COLS if c in df_out.columns]
    if numeric_cols:
        summary = df_out[numeric_cols].describe().round(2)
        log.info("Price enrichment summary:\n%s", summary.to_string())


if __name__ == "__main__":
    main()

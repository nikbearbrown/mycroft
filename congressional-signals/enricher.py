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

# Write to disk every N rows so an interruption loses at most this many.
CHECKPOINT_EVERY = 200

# In-memory cache: (ticker, date_str) -> float | None
_price_cache: dict[tuple[str, str], float | None] = {}


def _row_key(row: dict) -> str:
    """Stable identity for a trade, used to detect already-enriched rows on resume.
    Prefers the unique trade_url; falls back to a composite of core fields."""
    url = str(row.get("trade_url", "")).strip()
    if url:
        return url
    return "|".join(str(row.get(k, "")) for k in
                    ("politician", "ticker", "trade_type",
                     "transaction_date", "disclosure_date", "amount_range"))


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


# Per-ticker full-history cache. We download each ticker ONCE over the whole
# study window, then answer every date lookup locally. This turns ~4 API calls
# per trade (tens of thousands total -> instant rate-limit) into ~1 call per
# unique ticker (a few hundred total), which yfinance tolerates.
import time
_ticker_hist: dict[str, "pd.Series | None"] = {}
_HIST_START = "2023-01-01"


def _load_ticker(ticker: str) -> "pd.Series | None":
    if ticker in _ticker_hist:
        return _ticker_hist[ticker]
    end = (datetime.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    series = None
    for attempt in range(3):
        try:
            df = yf.download(ticker, start=_HIST_START, end=end,
                             progress=False, auto_adjust=True)
            if not df.empty:
                s = df["Close"]
                if hasattr(s, "columns"):        # flatten multiindex
                    s = s.iloc[:, 0]
                s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
                series = s.sort_index()
                break
        except Exception as exc:
            log.debug("yfinance error %s (attempt %d): %s", ticker, attempt + 1, exc)
        time.sleep(1.0 * (attempt + 1))          # backoff on empty/error
    _ticker_hist[ticker] = series
    return series


def get_close(ticker: str, date: datetime) -> float | None:
    """Closing price on `date` or the nearest prior trading day. Local lookup
    against the ticker's cached full history (downloaded once)."""
    s = _load_ticker(ticker)
    if s is None or len(s) == 0:
        return None
    dt = pd.Timestamp(date).normalize()
    sub = s[s.index <= dt]
    if sub.empty:
        return None
    return round(float(sub.iloc[-1]), 4)


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

    # Resume: load already-enriched rows and skip them this run.
    # A row counts as "done" only if it was actually priced OR is genuinely
    # unpriceable (non-equity ticker). A valid-equity row left blank is a
    # rate-limit casualty — drop it from the base so it gets re-enriched.
    def _priced(r: dict) -> bool:
        return (str(r.get("price_at_disclosure", "")).strip() != "" or
                str(r.get("price_at_trade", "")).strip() != "")

    def _retryable(r: dict) -> bool:
        tk = clean_ticker(r.get("ticker", ""))
        return is_valid_equity_ticker(tk) and not _priced(r)

    existing_records: list[dict] = []
    done_keys: set[str] = set()
    if OUTPUT.exists():
        ex = pd.read_csv(OUTPUT, dtype=str, on_bad_lines="skip").fillna("")
        all_existing = ex.to_dict("records")
        retry = [r for r in all_existing if _retryable(r)]
        existing_records = [r for r in all_existing if not _retryable(r)]  # base we keep
        done_keys = {_row_key(r) for r in existing_records}
        log.info("Resume: %d kept, %d valid-but-unpriced rows will be RE-enriched",
                 len(done_keys), len(retry))

    todo = [r for r in records if _row_key(r) not in done_keys]
    log.info("Total=%d  already-done=%d  to-enrich=%d", len(records), len(done_keys), len(todo))

    if not todo:
        log.info("All rows already enriched — nothing to do.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    new_enriched: list[dict] = []
    skip_count = 0

    def flush() -> None:
        # Rewrite full file (existing + new); concat aligns differing columns.
        pd.DataFrame(existing_records + new_enriched).to_csv(OUTPUT, index=False)

    for i, row in enumerate(todo, 1):
        ticker = clean_ticker(row.get("ticker", ""))
        label = ticker or "(no ticker)"
        if not is_valid_equity_ticker(ticker):
            skip_count += 1
        else:
            log.info("[%d/%d] %s — %s", i, len(todo), label, row.get("politician", ""))

        new_enriched.append(enrich_row(row))

        if i % CHECKPOINT_EVERY == 0:
            flush()
            log.info("  ...checkpoint saved — %d new rows (%d total)",
                     len(new_enriched), len(existing_records) + len(new_enriched))

    flush()
    log.info("Skipped %d rows with invalid/missing tickers", skip_count)
    log.info("Saved enriched data → %s (%d total rows)",
             OUTPUT, len(existing_records) + len(new_enriched))

    # Quick summary stats
    df_out = pd.DataFrame(existing_records + new_enriched)
    numeric_cols = [c for c in PRICE_COLS if c in df_out.columns]
    if numeric_cols:
        for c in numeric_cols:
            df_out[c] = pd.to_numeric(df_out[c], errors="coerce")
        summary = df_out[numeric_cols].describe().round(2)
        log.info("Price enrichment summary:\n%s", summary.to_string())


if __name__ == "__main__":
    main()

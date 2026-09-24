"""
server.py — FastMCP server for Congressional Trading Analysis

Tools:
  get_price_history(ticker, period) → daily closes from yfinance
  get_recent_trades(limit)          → rows from enriched_trades.csv as JSON

Run:
  python server.py
  (or via MCP client pointing to this file)
"""

import json
import logging
import os
import sys
import threading
from pathlib import Path

import pandas as pd
import yfinance as yf
from fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
ENRICHED_CSV = DATA_DIR / "enriched_trades.csv"
TRADES_CSV   = DATA_DIR / "trades.csv"

mcp = FastMCP(
    name="Congressional Trading Analysis",
    instructions=(
        "Provides tools to explore U.S. congressional stock trade disclosures "
        "and related equity price history. Use get_recent_trades to browse trades "
        "and get_price_history to pull market data for any ticker."
    ),
)


@mcp.tool()
def get_price_history(ticker: str, period: str = "3mo") -> dict:
    """
    Fetch daily OHLCV data for a given stock ticker using Yahoo Finance.

    Args:
        ticker: Stock ticker symbol, e.g. "AAPL", "NVDA", "MSFT".
        period: Data window — one of: 1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max.
                Defaults to "3mo".

    Returns:
        {
          "ticker":  str,
          "period":  str,
          "dates":   [str, ...],   # YYYY-MM-DD
          "opens":   [float, ...],
          "highs":   [float, ...],
          "lows":    [float, ...],
          "closes":  [float, ...],
          "volumes": [int, ...]
        }
        On failure returns {"error": "<message>"}.
    """
    ticker = ticker.strip().upper()
    log.info("get_price_history ticker=%s period=%s", ticker, period)

    valid_periods = {"1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"}
    if period not in valid_periods:
        return {"error": f"Invalid period '{period}'. Choose from: {sorted(valid_periods)}"}

    try:
        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
    except Exception as exc:
        log.warning("yfinance error: %s", exc)
        return {"error": str(exc)}

    if hist.empty:
        return {"error": f"No price data found for ticker '{ticker}'"}

    def _f(v) -> float | None:
        return None if pd.isna(v) else round(float(v), 4)

    return {
        "ticker":  ticker,
        "period":  period,
        "dates":   hist.index.strftime("%Y-%m-%d").tolist(),
        "opens":   [_f(v) for v in hist["Open"]],
        "highs":   [_f(v) for v in hist["High"]],
        "lows":    [_f(v) for v in hist["Low"]],
        "closes":  [_f(v) for v in hist["Close"]],
        "volumes": [None if pd.isna(v) else int(v) for v in hist["Volume"]],
    }


@mcp.tool()
def get_recent_trades(limit: int = 20) -> list[dict]:
    """
    Return recent U.S. congressional trade disclosures with enriched price data.

    Reads enriched_trades.csv if available, otherwise falls back to trades.csv.
    Records are returned in file order (most recently scraped first).

    Args:
        limit: Number of records to return. Clamped to [1, 500]. Default 20.

    Returns:
        List of trade dicts. Price/pct fields are numeric where data was available,
        null where a ticker could not be looked up.
        On missing data returns [{"error": "<message>"}].

    Fields per record (enriched):
        politician, ticker, asset_name, trade_type,
        transaction_date, disclosure_date, amount_range,
        price_30d_pre_trade, price_at_trade, pct_change_pre_trade,
        price_at_disclosure, price_30d_post_disclosure, pct_change_post_disclosure
    """
    limit = max(1, min(limit, 500))
    log.info("get_recent_trades limit=%d", limit)

    source = ENRICHED_CSV if ENRICHED_CSV.exists() else TRADES_CSV
    if not source.exists():
        return [{"error": (
            "No trade data found. Run scraper.py first, "
            "then enricher.py to add price columns."
        )}]

    log.info("Reading from %s", source)
    df = pd.read_csv(source, dtype=str)

    price_cols = [
        "price_30d_pre_trade", "price_at_trade", "pct_change_pre_trade",
        "price_at_disclosure", "price_30d_post_disclosure", "pct_change_post_disclosure",
    ]
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # to_json converts NaN/NaT → null and handles all numpy scalar types;
    # avoids ValueError that json.dumps raises for float NaN.
    return json.loads(df.head(limit).to_json(orient="records"))


def _load_trades() -> pd.DataFrame:
    """Load trades CSV (enriched if available, raw otherwise). Returns empty DataFrame on missing file."""
    source = ENRICHED_CSV if ENRICHED_CSV.exists() else TRADES_CSV
    if not source.exists():
        return pd.DataFrame()
    df = pd.read_csv(source, dtype=str).fillna("")
    for col in ["price_30d_pre_trade", "price_at_trade", "pct_change_pre_trade",
                "price_at_disclosure", "price_30d_post_disclosure", "pct_change_post_disclosure"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@mcp.tool()
def get_buy_signals(days: int = 30, min_politicians: int = 2) -> list[dict]:
    """
    Find stocks that multiple Congress members have BOUGHT recently — the core signal.

    When 2+ members buy the same ticker in a short window (especially cross-party),
    it often precedes a price move driven by privileged information about legislation,
    contracts, or regulatory decisions.

    Args:
        days: Look-back window in calendar days (default 30).
        min_politicians: Minimum distinct politicians who must have bought (default 2).

    Returns:
        List of signal dicts sorted by conviction (number of buyers desc), each with:
          ticker, asset_name, buy_count, politicians (list), total_amount_hint,
          latest_transaction_date, latest_disclosure_date
        Returns [{"error": "..."}] if no data available yet.
    """
    df = _load_trades()
    if df.empty:
        return [{"error": "No trade data yet — scraper still running."}]

    buys = df[df["trade_type"].str.upper() == "BUY"].copy()
    buys = buys[buys["ticker"].str.len().between(1, 5)]
    buys = buys[buys["ticker"].str.isalpha()]

    # Filter by date window if dates are available
    if "transaction_date" in buys.columns and buys["transaction_date"].str.len().gt(0).any():
        from datetime import datetime, timedelta
        cutoff = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
        dated = buys[buys["transaction_date"] >= cutoff]
        if not dated.empty:
            buys = dated

    if buys.empty:
        return [{"message": "No BUY trades found in window.", "days": days}]

    grouped = (
        buys.groupby("ticker")
        .agg(
            asset_name=("asset_name", "first"),
            buy_count=("politician", "count"),
            politicians=("politician", lambda x: sorted(x.unique().tolist())),
            latest_transaction_date=("transaction_date", "max"),
            latest_disclosure_date=("disclosure_date", "max"),
        )
        .reset_index()
    )

    signals = grouped[grouped["buy_count"] >= min_politicians].sort_values("buy_count", ascending=False)
    log.info("get_buy_signals: %d signals (days=%d, min_pol=%d)", len(signals), days, min_politicians)
    return json.loads(signals.to_json(orient="records"))


@mcp.tool()
def get_stock_activity(ticker: str) -> dict:
    """
    Show all congressional trades for a specific stock ticker.

    Use this to research whether Congress is bullish or bearish on a stock,
    who is trading it, and when.

    Args:
        ticker: Stock ticker symbol, e.g. "NVDA", "AAPL", "MSFT".

    Returns:
        {
          ticker, total_trades, buys, sells,
          politicians: [list of names who traded it],
          trades: [full trade records sorted newest first]
        }
    """
    ticker = ticker.strip().upper()
    df = _load_trades()
    if df.empty:
        return {"error": "No trade data yet — scraper still running."}

    match = df[df["ticker"].str.upper() == ticker].copy()
    if match.empty:
        return {"ticker": ticker, "total_trades": 0, "message": "No congressional trades found for this ticker."}

    match_sorted = match.sort_values("transaction_date", ascending=False)
    buys  = int((match["trade_type"].str.upper() == "BUY").sum())
    sells = int((match["trade_type"].str.upper() == "SELL").sum())
    politicians = sorted(match["politician"].unique().tolist())

    log.info("get_stock_activity %s: %d trades (%d buys, %d sells)", ticker, len(match), buys, sells)
    return {
        "ticker": ticker,
        "asset_name": match["asset_name"].iloc[0],
        "total_trades": len(match),
        "buys": buys,
        "sells": sells,
        "sentiment": "BULLISH" if buys > sells else "BEARISH" if sells > buys else "NEUTRAL",
        "politicians": politicians,
        "trades": json.loads(match_sorted.to_json(orient="records")),
    }


@mcp.tool()
def get_politician_activity(politician_name: str = "", limit: int = 10) -> list[dict]:
    """
    Show the most active Congress members and their recent trading patterns.

    Use with no arguments to see the top traders overall.
    Pass a name to drill into a specific politician's recent trades.

    Args:
        politician_name: Partial or full name (case-insensitive). Empty = show top traders.
        limit: Max results (default 10).

    Returns:
        If name given: their recent trades (newest first).
        If no name: leaderboard of most active traders with buy/sell breakdown.
    """
    df = _load_trades()
    if df.empty:
        return [{"error": "No trade data yet — scraper still running."}]

    if politician_name.strip():
        mask = df["politician"].str.contains(politician_name.strip(), case=False, na=False)
        subset = df[mask].sort_values("transaction_date", ascending=False).head(limit)
        if subset.empty:
            return [{"message": f"No trades found for '{politician_name}'"}]
        return json.loads(subset.to_json(orient="records"))

    # Leaderboard mode
    leaderboard = (
        df.groupby("politician")
        .agg(
            total_trades=("ticker", "count"),
            buys=("trade_type", lambda x: (x.str.upper() == "BUY").sum()),
            sells=("trade_type", lambda x: (x.str.upper() == "SELL").sum()),
            unique_tickers=("ticker", lambda x: x[x.str.isalpha() & x.str.len().between(1,5)].nunique()),
            latest_trade=("transaction_date", "max"),
        )
        .reset_index()
        .sort_values("total_trades", ascending=False)
        .head(limit)
    )
    return json.loads(leaderboard.to_json(orient="records"))


def _install_stdin_newline_filter() -> None:
    """
    Some MCP clients send bare '\\n' keepalives between JSON-RPC messages.
    The mcp package's stdio reader passes every line to the JSON parser without
    skipping blanks, which raises a pydantic ValidationError and sends back an
    'Internal Server Error' notification on every heartbeat.

    Fix: replace fd 0 with a pipe whose write-end is fed by a background thread
    that drops blank lines. Rebuilding sys.stdin ensures both Python-level
    readline() and anyio's async file wrappers see the filtered stream.
    """
    read_fd, write_fd = os.pipe()
    orig_fd = os.dup(0)          # preserve original stdin fd
    os.dup2(read_fd, 0)          # fd 0 → pipe read end
    os.close(read_fd)            # drop redundant reference

    enc = getattr(sys.stdin, "encoding", None) or "utf-8"
    err = getattr(sys.stdin, "errors",   None) or "replace"
    sys.stdin = open(0, mode="r", encoding=enc, errors=err, closefd=False)

    def _pump() -> None:
        with open(orig_fd, "rb") as src, open(write_fd, "wb") as dst:
            for raw_line in src:
                if raw_line.strip():   # forward only non-blank lines
                    dst.write(raw_line)
                    dst.flush()

    threading.Thread(target=_pump, daemon=True, name="stdin-filter").start()


if __name__ == "__main__":
    _install_stdin_newline_filter()
    mcp.run()

import pandas as pd
import yfinance as yf
from fredapi import Fred
import os
from datetime import date, timedelta
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()
fred = Fred(api_key=os.getenv("FRED_API_KEY"))


# ── yfinance: sector / mktcap ────────────────────────────────────────────────

@lru_cache(maxsize=256)
def _get_ticker_meta(ticker: str) -> dict:
    empty = {"sector": None, "industry": None, "market_cap": None, "market_cap_raw": None}
    try:
        info = yf.Ticker(ticker).fast_info  # avoids quoteSummary for ETFs
        raw_cap = getattr(info, "market_cap", None)

        # Fall back to full info only for stocks (ETFs will have no market_cap)
        if raw_cap is None:
            full = yf.Ticker(ticker).info
            # If yfinance returns an error dict, bail out
            if not full or full.get("trailingPegRatio") is None and full.get("sector") is None:
                return empty
            raw_cap = full.get("marketCap")
            sector   = full.get("sector")
            industry = full.get("industry")
        else:
            full     = yf.Ticker(ticker).info
            sector   = full.get("sector")
            industry = full.get("industry")

        if raw_cap:
            if raw_cap >= 10e9:    cap_bucket = "large"
            elif raw_cap >= 2e9:   cap_bucket = "mid"
            elif raw_cap >= 300e6: cap_bucket = "small"
            else:                  cap_bucket = "micro"
        else:
            cap_bucket = None

        return {
            "sector":         sector,
            "industry":       industry,
            "market_cap":     cap_bucket,
            "market_cap_raw": raw_cap,
        }
    except Exception:
        return empty


@lru_cache(maxsize=256)
def _get_earnings_dates(ticker: str) -> list[date]:
    try:
        cal = yf.Ticker(ticker).calendar
        if cal is None or cal.empty:
            return []
        if "Earnings Date" in cal.columns:
            return [d.date() if hasattr(d, "date") else d for d in cal["Earnings Date"]]
        return []
    except Exception:
        return []


def _days_to_nearest_earnings(trade_date: date, ticker: str) -> int | None:
    dates = _get_earnings_dates(ticker)
    if not dates:
        return None
    diffs = [abs((trade_date - d).days) for d in dates]
    return min(diffs)


# ── FRED: macro regime ───────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_fred_series() -> pd.DataFrame:
    """Load VIX, fed funds rate, and recession indicator once."""
    vix   = fred.get_series("VIXCLS").rename("vix")
    ffr   = fred.get_series("DFF").rename("fed_funds_rate")
    rec   = fred.get_series("USREC").rename("in_recession")

    df = pd.concat([vix, ffr, rec], axis=1)
    df.index = pd.to_datetime(df.index)
    df = df.resample("D").ffill()
    return df


def _get_macro_on_date(trade_date: date) -> dict:
    try:
        macro = _load_fred_series()
        ts    = pd.Timestamp(trade_date)
        # Walk back up to 7 days to handle weekends/holidays
        for delta in range(7):
            key = ts - pd.Timedelta(days=delta)
            if key in macro.index:
                row = macro.loc[key]
                vix = row.get("vix")
                if pd.isna(vix):
                    vix = None

                if vix is None:       vix_regime = None
                elif vix < 15:        vix_regime = "low"
                elif vix < 25:        vix_regime = "elevated"
                elif vix < 35:        vix_regime = "high"
                else:                 vix_regime = "extreme"

                return {
                    "vix_level":       round(float(vix), 2) if vix else None,
                    "vix_regime":      vix_regime,
                    "fed_funds_rate":  round(float(row.get("fed_funds_rate") or 0), 2),
                    "in_recession":    bool(row.get("in_recession") == 1),
                }
    except Exception:
        pass
    return {"vix_level": None, "vix_regime": None, "fed_funds_rate": None, "in_recession": None}


# ── Market regime (SPY rolling trend) ───────────────────────────────────────

@lru_cache(maxsize=1)
def _load_spy_regimes() -> pd.Series:
    """
    Classify each trading day as bull/bear/choppy using SPY 50d vs 200d SMA.
    bull  = 50d > 200d and SPY above 50d
    bear  = 50d < 200d
    choppy = otherwise
    """
    spy = yf.download("SPY", start="2010-01-01", auto_adjust=True, progress=False)["Close"]
    sma50  = spy.rolling(50).mean()
    sma200 = spy.rolling(200).mean()

    regime = pd.Series("choppy", index=spy.index)
    regime[sma50 > sma200] = "bull"
    regime[(sma50 < sma200)] = "bear"
    return regime.resample("D").ffill()


def _get_market_regime(trade_date: date) -> str | None:
    try:
        regimes = _load_spy_regimes()
        ts = pd.Timestamp(trade_date)
        for delta in range(7):
            key = ts - pd.Timedelta(days=delta)
            if key in regimes.index:
                return regimes.loc[key]
    except Exception:
        pass
    return None


# ── Main enrichment function ─────────────────────────────────────────────────

def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the parsed trade DataFrame and adds all enrichment columns.
    Operates in-place on a copy. Returns the enriched DataFrame.
    """
    df = df.copy()

    # -- Ticker-level metadata (batched by unique ticker)
    unique_tickers = df["ticker"].unique()
    meta_map = {t: _get_ticker_meta(t) for t in unique_tickers}

    df["sector"]         = df["ticker"].map(lambda t: meta_map[t]["sector"])
    df["industry"]       = df["ticker"].map(lambda t: meta_map[t]["industry"])
    df["market_cap"]     = df["ticker"].map(lambda t: meta_map[t]["market_cap"])
    df["market_cap_raw"] = df["ticker"].map(lambda t: meta_map[t]["market_cap_raw"])

    # -- Macro context per trade date
    unique_dates = df["date"].unique()
    macro_map = {d: _get_macro_on_date(d) for d in unique_dates}

    df["vix_level"]      = df["date"].map(lambda d: macro_map[d]["vix_level"])
    df["vix_regime"]     = df["date"].map(lambda d: macro_map[d]["vix_regime"])
    df["fed_funds_rate"] = df["date"].map(lambda d: macro_map[d]["fed_funds_rate"])
    df["in_recession"]   = df["date"].map(lambda d: macro_map[d]["in_recession"])

    # -- Market regime per trade date
    df["market_regime"] = df["date"].map(_get_market_regime)

    # -- Earnings proximity (only on SELL rows with pnl populated)
    df["days_to_earnings"] = df.apply(
        lambda r: _days_to_nearest_earnings(r["date"], r["ticker"]), axis=1
    )
    df["earnings_trade"] = df["days_to_earnings"].apply(
        lambda d: d is not None and d <= 5
    )

    return df
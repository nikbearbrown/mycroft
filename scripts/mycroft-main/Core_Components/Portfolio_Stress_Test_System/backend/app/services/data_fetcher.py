import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("portfolio_analysis.data_fetcher")


class DataFetchError(Exception):
    pass


class DataFetcher:
    """Market data """

    @staticmethod
    def fetch_price_data(
        tickers: List[str],
        lookback_days: int
    ) -> Dict[str, pd.DataFrame]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        logger.info(f"Fetching price data for {len(tickers)} tickers from {start_date.date()} to {end_date.date()}")

        price_data, failed = {}, []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(start=start_date, end=end_date)
                if hist.empty:
                    failed.append(ticker)
                    logger.warning(f"No data for {ticker}")
                    continue
                price_data[ticker] = hist[['Close']].copy()
                logger.info(f"  {ticker}: {len(hist)} days")
            except Exception as e:
                failed.append(ticker)
                logger.error(f"Error fetching {ticker}: {e}")

        if len(price_data) < 2:
            raise DataFetchError(
                f"Insufficient data — got {len(price_data)} tickers. Failed: {failed}"
            )
        return price_data

    @staticmethod
    def fetch_vix_data(lookback_days: int, use_5day_avg: bool = True) -> pd.Series:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        try:
            hist = yf.Ticker("^VIX").history(start=start_date, end=end_date)
            if hist.empty:
                raise DataFetchError("No VIX data found")
            vix = hist['Close']
            if use_5day_avg:
                vix = vix.rolling(window=5, min_periods=1).mean()
            logger.info(f"Fetched {len(vix)} days of VIX data")
            return vix
        except Exception as e:
            raise DataFetchError(f"Error fetching VIX: {e}")


    @staticmethod
    def fetch_crash_period_data(
        tickers: List[str],
        start: str,
        end: str,
        benchmark_ticker: str = "SPY"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch price data for a specific crash window.

        Returns dict mapping ticker -> DataFrame(Close) for the period,
        including the benchmark. Adds a small pre-period buffer (5 days
        before start) so we can compute the first day's return cleanly.

        Raises DataFetchError if fewer than 2 portfolio tickers succeed.
        """
        # 5-day buffer before the window for return calculation
        start_dt = datetime.strptime(start, "%Y-%m-%d") - timedelta(days=7)
        end_dt   = datetime.strptime(end,   "%Y-%m-%d") + timedelta(days=1)

        all_tickers = list(set(tickers + [benchmark_ticker]))
        logger.info(
            f"Fetching crash period data for {all_tickers} "
            f"from {start} to {end} (buffer: {start_dt.date()})"
        )

        price_data, failed = {}, []
        for ticker in all_tickers:
            try:
                hist = yf.Ticker(ticker).history(
                    start=start_dt.strftime("%Y-%m-%d"),
                    end=end_dt.strftime("%Y-%m-%d")
                )
                if hist.empty:
                    failed.append(ticker)
                    logger.warning(f"No data for {ticker} in crash window")
                    continue
                price_data[ticker] = hist[['Close']].copy()
                logger.info(f"  {ticker}: {len(hist)} rows in crash window")
            except Exception as e:
                failed.append(ticker)
                logger.error(f"  {ticker} error: {e}")

        portfolio_fetched = [t for t in tickers if t in price_data]
        if len(portfolio_fetched) < 2:
            raise DataFetchError(
                f"Insufficient crash data — got {len(portfolio_fetched)} tickers. "
                f"Failed: {failed}"
            )

        return price_data

    @staticmethod
    def fetch_recovery_data(
        tickers: List[str],
        crash_end: str,
        benchmark_ticker: str = "SPY",
        max_recovery_days: int = 504     # look up to 2 years post-crash
    ) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Fetch post-crash price data to measure recovery time.
        Returns None if fetch fails (non-fatal — recovery shown as None).
        """
        start_dt = datetime.strptime(crash_end, "%Y-%m-%d")
        end_dt   = start_dt + timedelta(days=max_recovery_days)

        # Don't look into the future
        today = datetime.now()
        if end_dt > today:
            end_dt = today

        if start_dt >= end_dt:
            return None

        all_tickers = list(set(tickers + [benchmark_ticker]))
        try:
            price_data = {}
            for ticker in all_tickers:
                hist = yf.Ticker(ticker).history(
                    start=crash_end,
                    end=end_dt.strftime("%Y-%m-%d")
                )
                if not hist.empty:
                    price_data[ticker] = hist[['Close']].copy()
            return price_data if price_data else None
        except Exception as e:
            logger.warning(f"Recovery data fetch failed (non-fatal): {e}")
            return None
import io
import zipfile
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging

from app.core.config import settings

logger = logging.getLogger("portfolio_analysis.factor_fetcher")

FACTORS = ["MKT", "SMB", "HML", "RMW", "CMA", "UMD"]


class FactorFetchError(Exception):
    pass


class FactorFetcher:
    """
    Downloads and caches Fama-French 5-factor + Momentum daily data.

    Cache strategy:
      - On first call, download both ZIPs, parse, merge, save as parquet.
      - On subsequent calls, load from parquet if < FACTOR_CACHE_MAX_AGE_DAYS old.
      - Otherwise re-download and overwrite.

    Returned DataFrame has a tz-naive DatetimeIndex and columns:
      MKT, SMB, HML, RMW, CMA, UMD, RF
    All values are in decimal form (divided by 100 from the raw % CSV).
    """

    @staticmethod
    def _cache_dir() -> Path:
        d = settings.FACTOR_CACHE_DIR
        d.mkdir(parents=True, exist_ok=True)
        return d

    @staticmethod
    def _cache_path() -> Path:
        return FactorFetcher._cache_dir() / "factor_data.parquet"

    @staticmethod
    def _cache_is_fresh() -> bool:
        p = FactorFetcher._cache_path()
        if not p.exists():
            return False
        age = datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)
        return age < timedelta(days=settings.FACTOR_CACHE_MAX_AGE_DAYS)

    # ── Parsers ───────────────────────────────────────────────────────────

    @staticmethod
    def _download_zip(url: str) -> bytes:
        logger.info(f"Downloading {url}")
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            raise FactorFetchError(f"HTTP {resp.status_code} fetching {url}")
        return resp.content

    @staticmethod
    def _parse_ff5(raw: bytes) -> pd.DataFrame:
        """
        Parse the FF5 daily zip.
        The CSV inside has a variable-length header; data starts after
        the first line that begins with a date (8 digits YYYYMMDD).
        Returns DataFrame(Date, MKT, SMB, HML, RMW, CMA, RF).
        """
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            fname = [n for n in z.namelist() if n.endswith(".CSV") or n.endswith(".csv")][0]
            text = z.read(fname).decode("utf-8", errors="ignore")

        lines = text.splitlines()
        # Find first data line (starts with 8-digit date)
        start = next(
            i for i, ln in enumerate(lines)
            if ln.strip() and ln.strip()[0].isdigit() and len(ln.strip().split(",")[0]) == 8
        )
        # Find end of daily section (next blank or header-like line after data)
        end = len(lines)
        for i in range(start + 1, len(lines)):
            tok = lines[i].strip()
            if not tok:
                end = i
                break
            if tok[0].isalpha():
                end = i
                break

        csv_block = "\n".join(lines[start:end])
        df = pd.read_csv(
            io.StringIO(csv_block),
            header=None,
            names=["Date", "MKT-RF", "SMB", "HML", "RMW", "CMA", "RF"],
            skipinitialspace=True
        )
        df = df[df["Date"].astype(str).str.match(r"^\d{8}$")].copy()
        df["Date"] = pd.to_datetime(df["Date"].astype(str), format="%Y%m%d")
        df.set_index("Date", inplace=True)
        df = df.apply(pd.to_numeric, errors="coerce").dropna()
        df = df / 100                        # % → decimal
        df.rename(columns={"MKT-RF": "MKT"}, inplace=True)
        return df[["MKT", "SMB", "HML", "RMW", "CMA", "RF"]]

    @staticmethod
    def _parse_momentum(raw: bytes) -> pd.Series:
        """
        Parse the Momentum daily zip.
        Returns Series(Date) named 'UMD' in decimal form.
        """
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            fname = [n for n in z.namelist() if n.endswith(".CSV") or n.endswith(".csv")][0]
            text = z.read(fname).decode("utf-8", errors="ignore")

        lines = text.splitlines()
        start = next(
            i for i, ln in enumerate(lines)
            if ln.strip() and ln.strip()[0].isdigit() and len(ln.strip().split(",")[0]) == 8
        )
        end = len(lines)
        for i in range(start + 1, len(lines)):
            tok = lines[i].strip()
            if not tok or tok[0].isalpha():
                end = i
                break

        csv_block = "\n".join(lines[start:end])
        df = pd.read_csv(
            io.StringIO(csv_block),
            header=None,
            names=["Date", "UMD"],
            skipinitialspace=True
        )
        df = df[df["Date"].astype(str).str.match(r"^\d{8}$")].copy()
        df["Date"] = pd.to_datetime(df["Date"].astype(str), format="%Y%m%d")
        df.set_index("Date", inplace=True)
        df = df.apply(pd.to_numeric, errors="coerce").dropna()
        df["UMD"] = df["UMD"] / 100
        return df["UMD"]

    # ── Public API ────────────────────────────────────────────────────────

    @staticmethod
    def fetch(force_refresh: bool = False) -> pd.DataFrame:
        """
        Return merged daily factor DataFrame with columns:
          MKT, SMB, HML, RMW, CMA, UMD, RF
        Index: tz-naive DatetimeIndex.
        """
        cache_path = FactorFetcher._cache_path()

        if not force_refresh and FactorFetcher._cache_is_fresh():
            logger.info(f"Loading factor data from cache: {cache_path}")
            df = pd.read_parquet(cache_path)
            logger.info(f"Loaded {len(df)} rows from cache "
                        f"({df.index.min().date()} – {df.index.max().date()})")
            return df

        logger.info("Cache stale or missing — downloading factor data")
        try:
            ff5_raw  = FactorFetcher._download_zip(settings.FF5_URL)
            mom_raw  = FactorFetcher._download_zip(settings.MOMENTUM_URL)
        except Exception as e:
            # If download fails but cache exists, use stale cache rather than crash
            if cache_path.exists():
                logger.warning(f"Download failed ({e}), falling back to stale cache")
                return pd.read_parquet(cache_path)
            raise FactorFetchError(f"Factor data unavailable: {e}")

        ff5 = FactorFetcher._parse_ff5(ff5_raw)
        mom = FactorFetcher._parse_momentum(mom_raw)

        merged = ff5.join(mom, how="inner")
        merged = merged[FACTORS + ["RF"]].dropna()
        merged.index = pd.to_datetime(merged.index).tz_localize(None)

        merged.to_parquet(cache_path)
        logger.info(f"Factor cache saved: {len(merged)} rows "
                    f"({merged.index.min().date()} – {merged.index.max().date()})")
        return merged

    @staticmethod
    def get_factors_for_period(
        start: str,
        end: str,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Convenience: fetch and slice to [start, end] window.
        Returns DataFrame with columns MKT, SMB, HML, RMW, CMA, UMD, RF.
        """
        df = FactorFetcher.fetch(force_refresh=force_refresh)
        mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
        sliced = df.loc[mask]
        if sliced.empty:
            raise FactorFetchError(
                f"No factor data found for {start} – {end}. "
                "The French library may not have data this recent yet."
            )
        return sliced
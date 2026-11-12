"""
enrich.py — ENRICH stage (gate G3) of the insider-signal-agent recipe.

Reads data/verified/insider_buys.csv (G2-verified), prices every buy with daily adjusted closes
from Yahoo Finance (yfinance) and writes data/verified/enriched_buys.csv: one row per verified
buy, with its entry price and, for each registered window, the exit price, stock_return,
spy_return and abnormal_return.

Rules applied (PRE_REGISTRATION.md Rules 7, 8 and 9, registered 2026-11-09):
    entry   adjusted close on the first trading day after FILING_DATE
    exit    adjusted close 21 (primary) and 63 (secondary) trading days after entry
    returns stock_return = exit / entry − 1; spy_return over the identical dates;
            abnormal_return = stock_return − spy_return
    G3      at least 80% of verified buys priced
    Rule 9  the filed price must be within 25% of the stock's unadjusted close on TRANS_DATE (or
            the last bar before it): Yahoo's Close (split-adjusted) × every split ratio after
            TRANS_DATE, through the price fetch date. Otherwise price_status =
            price_mismatch_vs_filing and the buy has no prices or returns. No bar on or before
            TRANS_DATE → filing_price_check = not_checkable (the buy stays priced).
A "trading day" is a day with a SPY bar in the price data. A window whose exit day is after
the last SPY bar is `not_yet_closed` and has no return.

Missing prices are never filled in and no buy is dropped. Every buy gets a `price_status`:
    priced                     entry price found (both the stock and SPY on the entry day)
    blank_symbol               ticker_as_filed is empty
    placeholder_symbol         NONE, N/A, NA, NULL, … (no listed security)
    multiple_symbols           several symbols in one field ("GEF, GEF-B")
    unparseable_symbol         not a plain US ticker ("NASDAQ:DHC", "AXIA3", "RANGER")
    no_data                    Yahoo has no price history for the symbol (unknown symbol, or
                               delisted and dropped by Yahoo; yfinance cannot tell which)
    fetch_error                the request failed for another reason (retried on the next run)
    not_fetched                --offline and the symbol is not in the cache
    series_ends_before_entry   the symbol's prices stop before the entry day (consistent with a
                               delisting, merger or symbol change; not confirmed)
    series_starts_after_entry  the symbol's prices start after the entry day (e.g. a symbol
                               later reused or a listing that came later)
    no_bar_on_entry_date       the series spans the entry day but has no bar on it
    entry_after_market_data    the entry day is after the last SPY bar
    invalid_entry_price        the entry price is not a positive number
    price_mismatch_vs_filing   Rule 9: filed price more than 25% from the market close
and each window a `window_status_<N>d`: closed · not_yet_closed · no_entry_price ·
series_ends_before_exit · no_bar_on_exit_date · invalid_exit_price.

Symbols are used as filed, with only mechanical normalization: surrounding spaces removed,
upper case, and a share-class separator written the Yahoo way ("BRK.B" → "BRK-B"). Nothing is
guessed: an unusual symbol is reported, not mapped.

Prices are cached in data/raw/prices/ (one CSV per symbol, plus prices_manifest.json with the
requested range, fetched_at and SHA-256), so a re-run makes no requests. Split histories for
Rule 9 are cached in splits_manifest.json and fetched only for symbols with a priced buy. A symbol Yahoo had no
data for is recorded too and not asked for again. `--refresh` re-downloads everything (to close
windows that were still open). Requests go out in batches (default 40 symbols, threads off)
with a pause between batches (default 3 s), and every batch is logged in
data/raw/prices/fetch_log.jsonl. If Yahoo refuses (rate limit, 401/403/429, or a whole batch
failing at once), the batch is retried once after a back-off; a second refusal halts the run
(exit 3). Batches already fetched stay cached; nothing is promoted.

Halting checks (any failure → exit 1, nothing in data/verified/ changes; the failure audit goes
to data/raw/enrich/):
    input_hash        insider_buys.csv matches insider_buys_sha256 in conformance_summary.json
    spy_present       SPY is in the cache and covers the first entry day
    cache_consistent  every cached symbol was fetched for the same date range as SPY
    status_complete   every buy has a known price_status and window statuses; unpriced buys and
                      open windows carry no prices or returns; closed windows carry all of them
    lookahead         entry is the first SPY day after FILING_DATE; exit is exactly N SPY days
                      after entry; returns recompute from the stored prices
    filing_price_check  every buy priced at entry has split data and its Rule 9 fields and
                      verdict recompute; mismatches carry no prices
    coverage          priced buys ÷ verified buys ≥ 80% (Rule 8)

The audit reports coverage, price_status and window status, by quarter. It reports no return
statistics: averages are not computed before the signals are registered.

Exit codes: 0 promoted (or --check passed) · 1 halting check failed · 2 configuration refused ·
3 halted by the price source.

Usage
    python enrich.py                     # fetch what is not cached, then enrich and promote
    python enrich.py --offline           # cache only; uncached symbols → not_fetched
    python enrich.py --check             # G3: re-verify data/verified/enriched_buys.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import sys
import time
from bisect import bisect_right
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterable, Protocol

import conformance
import ingest

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
DEFAULT_VERIFIED_DIR = ROOT / "data" / "verified"
DEFAULT_PRICES_DIR = ROOT / "data" / "raw" / "prices"
DEFAULT_STAGING_DIR = ROOT / "data" / "raw" / "enrich"

BUYS_NAME = conformance.BUYS_NAME
CONFORMANCE_SUMMARY = conformance.SUMMARY_NAME
ENRICHED_NAME = "enriched_buys.csv"
AUDIT_NAME = "enrich-audit.md"
SUMMARY_NAME = "enrich_summary.json"
PRICES_MANIFEST = "prices_manifest.json"
FETCH_LOG = "fetch_log.jsonl"
SPLITS_MANIFEST = "splits_manifest.json"

MARKET = "SPY"
WINDOWS = (21, 63)                 # PRE_REGISTRATION.md Rule 7: primary, secondary
MIN_COVERAGE = 0.80                # PRE_REGISTRATION.md Rule 8
MISMATCH_TOLERANCE = 0.25          # PRE_REGISTRATION.md Rule 9: |filed / reference − 1| > 0.25
START_PAD_DAYS = 10                # fetch from a little before the earliest filing date
BATCH_SIZE = 40
PAUSE_S = 3.0
BACKOFF_S = 60.0

BUY_STATUSES = ("priced", "blank_symbol", "placeholder_symbol", "multiple_symbols",
                "unparseable_symbol", "no_data", "fetch_error", "not_fetched",
                "series_ends_before_entry", "series_starts_after_entry", "no_bar_on_entry_date",
                "entry_after_market_data", "invalid_entry_price", "price_mismatch_vs_filing")
FILING_CHECKS = ("ok", "mismatch", "not_checkable")
WINDOW_STATUSES = ("closed", "not_yet_closed", "no_entry_price", "series_ends_before_exit",
                   "no_bar_on_exit_date", "invalid_exit_price")
HALTING_CHECKS = ("input_hash", "spy_present", "cache_consistent", "status_complete",
                  "lookahead", "filing_price_check", "coverage")

_TICKER = re.compile(r"^[A-Z]{1,5}$")
_CLASS_TICKER = re.compile(r"^([A-Z]{1,4})[.\-]([A-Z]{1,2})$")
_PLACEHOLDERS = {"NONE", "NA", "N/A", "N.A.", "N.A", "NULL", "-", "--", "NOTAPPLICABLE"}
_REFUSAL = re.compile(r"rate.?limit|too many requests|\b429\b|\b403\b|\b401\b|forbidden|"
                      r"unauthori[sz]ed|crumb", re.I)
_NO_DATA = re.compile(r"delisted|no price data|no data found|quote not found|no timezone|"
                      r"symbol may be delisted|not found", re.I)


def window_columns(n: int) -> list[str]:
    return [f"exit_date_{n}d", f"exit_price_{n}d", f"spy_exit_price_{n}d", f"stock_return_{n}d",
            f"spy_return_{n}d", f"abnormal_return_{n}d", f"window_status_{n}d"]


ENRICH_COLUMNS = ["symbol_used", "price_status", "trade_ref_date", "trade_ref_close_unadjusted",
                  "split_factor", "filed_vs_close_ratio", "filing_price_check",
                  "entry_date", "entry_price", "spy_entry_price"]
CHECK_COLUMNS = ENRICH_COLUMNS[2:7]
ENRICHED_COLUMNS = (conformance.VERIFIED_COLUMNS + ENRICH_COLUMNS +
                    [c for n in WINDOWS for c in window_columns(n)])


class EnrichError(Exception):
    """Configuration refused (exit 2)."""


class PriceSourceRefused(Exception):
    """The price source refused requests twice in a row (exit 3)."""


# --------------------------------------------------------------------------- symbols

def normalize_symbol(raw: str | None) -> tuple[str | None, str | None]:
    """ticker_as_filed → (symbol to request, None) or (None, price_status). Nothing is guessed."""
    s = (raw or "").strip()
    if not s:
        return None, "blank_symbol"
    up = s.upper()
    if re.sub(r"[\s\[\]()]", "", up) in _PLACEHOLDERS:
        return None, "placeholder_symbol"
    if re.search(r"[,;]", up):
        return None, "multiple_symbols"
    if _TICKER.match(up):
        return up, None
    m = _CLASS_TICKER.match(up)
    if m:
        return f"{m.group(1)}-{m.group(2)}", None
    return None, "unparseable_symbol"


# --------------------------------------------------------------------------- price cache

Bar = tuple[str, float, float, float]          # (ISO date, close, adj_close, volume)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write_json_atomic(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


class PriceCache:
    """data/raw/prices/: <SYMBOL>.csv per symbol with data, and a manifest entry for every
    symbol requested (data or not)."""

    def __init__(self, prices_dir: Path):
        self.dir = prices_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / PRICES_MANIFEST
        self.manifest = (json.loads(path.read_text(encoding="utf-8")) if path.exists()
                         else {"source": "Yahoo Finance via yfinance", "symbols": {}})
        self._series: dict[str, dict[str, float]] = {}
        self._close: dict[str, dict[str, float]] = {}
        self._dates: dict[str, list[str]] = {}

    def entry(self, symbol: str) -> dict | None:
        return self.manifest["symbols"].get(symbol)

    def is_final(self, symbol: str, start: str, end: str) -> bool:
        """Cached with a final answer (data or no_data) for this exact range."""
        e = self.entry(symbol)
        return bool(e and e["status"] in ("ok", "no_data")
                    and e["requested_start"] == start and e["requested_end"] == end)

    def record(self, symbol: str, status: str, start: str, end: str, bars: list[Bar] | None,
               error: str = "", fetched_at: str | None = None) -> None:
        e = {"status": status, "requested_start": start, "requested_end": end,
             "fetched_at": fetched_at or _utc_now(), "error": error[:300]}
        path = self.dir / f"{symbol}.csv"
        if status == "ok":
            bars = sorted(bars or [])
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh, lineterminator="\n")
                w.writerow(["date", "close", "adj_close", "volume"])
                for d, c, a, v in bars:
                    w.writerow([d, _fmt(c, 6), _fmt(a, 6), _fmt(v, 0)])
            e.update(rows=len(bars), first_date=bars[0][0], last_date=bars[-1][0],
                     sha256=ingest.sha256_file(path))
        self.manifest["symbols"][symbol] = e
        for memo in (self._series, self._close, self._dates):
            memo.pop(symbol, None)

    def save(self) -> None:
        _write_json_atomic(self.dir / PRICES_MANIFEST, self.manifest)

    def series(self, symbol: str) -> dict[str, float] | None:
        """date → adjusted close, exactly as stored (so --check recomputes the same numbers)."""
        e = self.entry(symbol)
        if not e or e["status"] != "ok":
            return None
        if symbol not in self._series:
            out: dict[str, float] = {}
            close: dict[str, float] = {}
            with open(self.dir / f"{symbol}.csv", newline="", encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    out[r["date"]] = float(r["adj_close"])
                    close[r["date"]] = float(r["close"]) if r["close"] else float("nan")
            self._series[symbol], self._close[symbol] = out, close
            self._dates[symbol] = sorted(out)
        return self._series[symbol]

    def close_on_or_before(self, symbol: str, day: str) -> tuple[str, float] | None:
        """Yahoo's Close (split-adjusted, not dividend-adjusted) on the last bar ≤ day."""
        if self.series(symbol) is None:
            return None
        dates = self._dates[symbol]
        i = bisect_right(dates, day)
        if i == 0:
            return None
        d = dates[i - 1]
        return d, self._close[symbol][d]


class SplitCache:
    """data/raw/prices/splits_manifest.json: split history per symbol (Rule 9)."""

    def __init__(self, prices_dir: Path):
        self.dir = prices_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / SPLITS_MANIFEST
        self.manifest = (json.loads(path.read_text(encoding="utf-8")) if path.exists()
                         else {"source": "Yahoo Finance via yfinance (Stock Splits)", "symbols": {}})

    def entry(self, symbol: str) -> dict | None:
        return self.manifest["symbols"].get(symbol)

    def is_final(self, symbol: str, start: str, end: str) -> bool:
        e = self.entry(symbol)
        return bool(e and e["status"] in ("ok", "no_data")
                    and e["requested_start"] == start and e["requested_end"] == end)

    def record(self, symbol: str, status: str, start: str, end: str, splits: list | None,
               error: str = "", fetched_at: str | None = None) -> None:
        e = {"status": status, "requested_start": start, "requested_end": end,
             "fetched_at": fetched_at or _utc_now(), "error": error[:300]}
        if status == "ok":
            e["splits"] = sorted([d, float(r)] for d, r in (splits or []))
        self.manifest["symbols"][symbol] = e

    def save(self) -> None:
        _write_json_atomic(self.dir / SPLITS_MANIFEST, self.manifest)

    def factor_after(self, symbol: str, day: str, through: str) -> float | None:
        """Product of split ratios with day < split date ≤ through; None without split data."""
        e = self.entry(symbol)
        if not e or e["status"] != "ok":
            return None
        f = 1.0
        for d, r in e["splits"]:
            if day < d <= through and r > 0:
                f *= r
        return f


def _fmt(x: float | None, places: int) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return f"{x:.{places}f}"


# --------------------------------------------------------------------------- price source

class PriceSource(Protocol):
    def download(self, symbols: list[str], start: str, end: str
                 ) -> tuple[dict[str, list[Bar]], dict[str, str]]:
        """→ (bars per symbol with data, error message per symbol without). May raise."""


class YFinanceSource:
    """Live source. yfinance (and pandas) are imported only here, so tests need neither."""

    def __init__(self):
        try:
            import yfinance  # noqa: F401
        except ImportError as exc:  # pragma: no cover - environment
            raise EnrichError("yfinance is not installed (see requirements.txt).") from exc
        import yfinance as yf
        self.yf = yf

    def download(self, symbols, start, end):  # pragma: no cover - network
        yf = self.yf
        df = yf.download(symbols, start=start, end=end, auto_adjust=False, actions=False,
                         group_by="ticker", threads=False, progress=False,
                         multi_level_index=True)
        errors = {k: str(v) for k, v in getattr(yf.shared, "_ERRORS", {}).items()}
        bars: dict[str, list[Bar]] = {}
        if df is None or df.empty:
            return bars, {s: errors.get(s, "empty response") for s in symbols}
        tickers = set(df.columns.get_level_values(0))
        for s in symbols:
            if s not in tickers:
                errors.setdefault(s, "not in response")
                continue
            sub = df[s].dropna(subset=["Adj Close"])
            if sub.empty:
                errors.setdefault(s, "no price data found")
                continue
            bars[s] = [(ts.date().isoformat(), float(r["Close"]), float(r["Adj Close"]),
                        float(r["Volume"]) if r["Volume"] == r["Volume"] else float("nan"))
                       for ts, r in sub.iterrows()]
            errors.pop(s, None)
        return bars, errors


    def download_splits(self, symbols, start, end):  # pragma: no cover - network
        yf = self.yf
        df = yf.download(symbols, start=start, end=end, auto_adjust=False, actions=True,
                         group_by="ticker", threads=False, progress=False,
                         multi_level_index=True)
        errors = {k: str(v) for k, v in getattr(yf.shared, "_ERRORS", {}).items()}
        out: dict[str, list] = {}
        if df is None or df.empty:
            return out, {s: errors.get(s, "empty response") for s in symbols}
        tickers = set(df.columns.get_level_values(0))
        for s in symbols:
            if s not in tickers or df[s]["Adj Close"].dropna().empty:
                errors.setdefault(s, "no price data found")
                continue
            col = df[s]["Stock Splits"] if "Stock Splits" in df[s].columns else None
            out[s] = ([] if col is None else
                      [(ts.date().isoformat(), float(v)) for ts, v in col.items()
                       if v == v and v not in (0, 1)])
            errors.pop(s, None)
        return out, errors


def _is_refusal(exc_or_msg) -> bool:
    if isinstance(exc_or_msg, BaseException):
        return ("RateLimit" in type(exc_or_msg).__name__) or bool(_REFUSAL.search(str(exc_or_msg)))
    return bool(_REFUSAL.search(str(exc_or_msg)))


def fetch_missing(symbols: Iterable[str], cache: PriceCache, source: PriceSource, start: str,
                  end: str, *, batch_size: int = BATCH_SIZE, pause_s: float = PAUSE_S,
                  backoff_s: float = BACKOFF_S, refresh: bool = False,
                  sleep: Callable[[float], None] = time.sleep,
                  clock: Callable[[], float] = time.monotonic,
                  log: Callable[[str], None] = print, kind: str = "prices") -> dict:
    """Request every symbol not cached for [start, end). Saves the manifest after each batch.
    kind = "prices" (source.download → PriceCache) or "splits" (source.download_splits →
    SplitCache)."""
    download = source.download if kind == "prices" else source.download_splits
    todo = sorted(s for s in set(symbols) if refresh or not cache.is_final(s, start, end))
    if kind == "prices" and MARKET in todo:  # SPY first: nothing can be priced without it
        todo.remove(MARKET)
        todo.insert(0, MARKET)
    stats = Counter(requested=len(todo))
    log_path = cache.dir / FETCH_LOG
    batches = [todo[i:i + batch_size] for i in range(0, len(todo), batch_size)]
    for b, batch in enumerate(batches):
        if b:
            sleep(pause_s)
        for attempt in (1, 2):
            t0 = clock()
            refused, why = False, ""
            try:
                bars, errors = download(batch, start, end)
            except Exception as exc:  # noqa: BLE001 - any failure is logged; refusals halt
                bars, errors = {}, {s: f"{type(exc).__name__}: {exc}" for s in batch}
                refused, why = _is_refusal(exc), f"{type(exc).__name__}: {exc}"
            if not refused:
                refusals = [m for m in errors.values() if _is_refusal(m)]
                if refusals:
                    refused, why = True, refusals[0]
                elif len(batch) >= 10 and not bars:
                    refused, why = True, "every symbol in the batch failed"
            line = {"ts": _utc_now(), "kind": kind, "batch": b + 1, "of": len(batches), "attempt": attempt,
                    "symbols": batch, "ok": len(bars), "failed": len(errors),
                    "refused": refused, "reason": why[:300],
                    "elapsed_ms": round((clock() - t0) * 1000)}
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(line) + "\n")
            stats["requests"] += len(batch)
            if not refused:
                break
            stats["refusals"] += 1
            if attempt == 1:
                log(f"enrich: batch {b + 1}/{len(batches)} refused ({why[:120]}); "
                    f"backing off {backoff_s:.0f} s, then one retry")
                sleep(backoff_s)
            else:
                cache.save()
                raise PriceSourceRefused(
                    f"Price source refused batch {b + 1}/{len(batches)} twice: {why[:200]}. "
                    f"{stats['ok'] + stats['no_data'] + stats['fetch_error']} symbols done and "
                    "cached; nothing promoted.")
        fetched_at = _utc_now()
        for s in batch:
            if s in bars and (bars[s] or kind == "splits"):
                cache.record(s, "ok", start, end, bars[s], fetched_at=fetched_at)
                stats["ok"] += 1
            else:
                msg = errors.get(s, "no price data found")
                status = "no_data" if _NO_DATA.search(msg) else "fetch_error"
                cache.record(s, status, start, end, None, error=msg, fetched_at=fetched_at)
                stats[status] += 1
        cache.save()
        if (b + 1) % 10 == 0 or b + 1 == len(batches):
            log(f"enrich: {kind}: fetched {b + 1}/{len(batches)} batches "
                f"(ok {stats['ok']}, no data {stats['no_data']}, errors {stats['fetch_error']})")
    stats["batches"] = len(batches)
    return dict(stats)


# --------------------------------------------------------------------------- enrichment

def _ret(exit_p: float, entry_p: float) -> float:
    return exit_p / entry_p - 1.0


def _r(x: float) -> str:
    return f"{x:.8f}"


def filing_price_check(row: dict, cache: PriceCache, splits: SplitCache | None) -> dict | None:
    """Rule 9 for one buy whose symbol has prices. → the CHECK_COLUMNS values, or None when the
    symbol has no split data (a halting failure, never a pass)."""
    symbol = normalize_symbol(row.get("ticker_as_filed"))[0]
    ref = cache.close_on_or_before(symbol, row["trans_date"])
    if ref is None:
        return {"trade_ref_date": "", "trade_ref_close_unadjusted": "", "split_factor": "",
                "filed_vs_close_ratio": "", "filing_price_check": "not_checkable"}
    if splits is None:
        return None
    through = cache.entry(symbol)["fetched_at"][:10]
    factor = splits.factor_after(symbol, row["trans_date"], through)
    if factor is None:
        return None
    ref_d, close = ref
    unadj = close * factor
    filed = float(row["price"])
    if not unadj > 0:
        return {"trade_ref_date": ref_d, "trade_ref_close_unadjusted": _fmt(unadj, 6),
                "split_factor": _fmt(factor, 6), "filed_vs_close_ratio": "",
                "filing_price_check": "not_checkable"}
    ratio = filed / unadj
    verdict = "mismatch" if abs(ratio - 1.0) > MISMATCH_TOLERANCE else "ok"
    return {"trade_ref_date": ref_d, "trade_ref_close_unadjusted": _fmt(unadj, 6),
            "split_factor": _fmt(factor, 6), "filed_vs_close_ratio": _fmt(ratio, 6),
            "filing_price_check": verdict}


def enrich_row(row: dict, cache: PriceCache, cal: list[str], spy: dict[str, float],
               windows: Iterable[int] = WINDOWS, offline: bool = False,
               splits: SplitCache | None = None, apply_rule_9: bool = True) -> dict:
    """One verified buy → the same row plus ENRICH_COLUMNS and the window columns."""
    out = {c: row.get(c, "") for c in conformance.VERIFIED_COLUMNS}
    out.update({c: "" for c in ENRICHED_COLUMNS if c not in out})
    windows = tuple(windows)
    symbol, status = normalize_symbol(row.get("ticker_as_filed"))
    out["symbol_used"] = symbol or ""
    entry_i = bisect_right(cal, row["filing_date"])      # first SPY day strictly after filing
    entry_d = cal[entry_i] if entry_i < len(cal) else None
    series = None
    if status is None:
        e = cache.entry(symbol)
        if e is None:
            status = "not_fetched" if offline else "fetch_error"
        elif e["status"] != "ok":
            status = e["status"]
        else:
            series = cache.series(symbol)
            if entry_d is None:
                status = "entry_after_market_data"
            elif e["last_date"] < entry_d:
                status = "series_ends_before_entry"
            elif e["first_date"] > entry_d:
                status = "series_starts_after_entry"
            elif entry_d not in series:
                status = "no_bar_on_entry_date"
            elif not series[entry_d] > 0 or not spy.get(entry_d, 0) > 0:
                status = "invalid_entry_price"
            else:
                status = "priced"
    if status == "priced" and apply_rule_9:
        chk = filing_price_check(row, cache, splits)
        if chk is None:
            out["filing_price_check"] = ""          # no split data: caught by the halting check
        else:
            out.update(chk)
            if chk["filing_price_check"] == "mismatch":
                status = "price_mismatch_vs_filing"
    out["price_status"] = status
    for n in windows:
        out[f"window_status_{n}d"] = "no_entry_price"
    if status != "priced":
        return out
    entry_p, spy_entry = series[entry_d], spy[entry_d]
    out.update(entry_date=entry_d, entry_price=_fmt(entry_p, 6), spy_entry_price=_fmt(spy_entry, 6))
    last_d = cache.entry(symbol)["last_date"]
    for n in windows:
        k = f"{n}d"
        if entry_i + n >= len(cal):
            out[f"window_status_{k}"] = "not_yet_closed"
            continue
        exit_d = cal[entry_i + n]
        out[f"exit_date_{k}"] = exit_d
        if last_d < exit_d:
            out[f"window_status_{k}"] = "series_ends_before_exit"
        elif exit_d not in series:
            out[f"window_status_{k}"] = "no_bar_on_exit_date"
        elif not series[exit_d] > 0:
            out[f"window_status_{k}"] = "invalid_exit_price"
        else:
            sr, mr = _ret(series[exit_d], entry_p), _ret(spy[exit_d], spy_entry)
            out.update({f"exit_price_{k}": _fmt(series[exit_d], 6),
                        f"spy_exit_price_{k}": _fmt(spy[exit_d], 6),
                        f"stock_return_{k}": _r(sr), f"spy_return_{k}": _r(mr),
                        f"abnormal_return_{k}": _r(sr - mr), f"window_status_{k}": "closed"})
    return out


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def splits_range(cache: PriceCache, start: str) -> tuple[str, str]:
    """Splits from the price range start through the latest price fetch date (inclusive)."""
    fetched = [e["fetched_at"][:10] for e in cache.manifest["symbols"].values() if e["status"] == "ok"]
    last = max(fetched) if fetched else date.today().isoformat()
    return start, (date.fromisoformat(last) + timedelta(days=1)).isoformat()


def fetch_range(rows: list[dict], end: date) -> tuple[str, str]:
    first = min(date.fromisoformat(r["filing_date"]) for r in rows)
    return (first - timedelta(days=START_PAD_DAYS)).isoformat(), end.isoformat()


# --------------------------------------------------------------------------- checks

def fetch_log_totals(prices_dir: Path) -> dict:
    """Every batch ever logged (all runs), so the audit shows the full fetch history."""
    path = prices_dir / FETCH_LOG
    if not path.exists():
        return {"batch_requests": 0}
    lines = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {"batch_requests": len(lines),
            "by_kind": dict(Counter(l.get("kind", "prices") for l in lines)),
            "symbol_requests": sum(len(l["symbols"]) for l in lines),
            "refused": sum(bool(l["refused"]) for l in lines),
            "first_ts": lines[0]["ts"] if lines else None,
            "last_ts": lines[-1]["ts"] if lines else None}


def _check(name: str, problems: list[str], detail: str = "") -> dict:
    return {"check": name, "passed": not problems, "violations": len(problems),
            "detail": detail, "examples": problems[:10]}


def run_checks(rows: list[dict], enriched: list[dict], cache: PriceCache, cal: list[str],
               spy: dict[str, float] | None, input_sha: str, expected_sha: str, start: str,
               end: str, windows: Iterable[int] = WINDOWS,
               splits: SplitCache | None = None) -> list[dict]:
    windows = tuple(windows)
    checks = [_check("input_hash", [] if input_sha and input_sha == expected_sha else
                     [f"insider_buys.csv {input_sha[:12]}… ≠ conformance summary "
                      f"{(expected_sha or 'missing')[:12]}…"],
                     "insider_buys.csv SHA-256 = insider_buys_sha256 (G2)")]
    first_filing = min((r["filing_date"] for r in rows), default="")
    spy_problems = []
    if not spy:
        spy_problems.append("SPY not in the price cache")
    elif not cal or cal[0] > first_filing:
        spy_problems.append(f"SPY starts {cal[0] if cal else '—'}, after the first filing {first_filing}")
    checks.append(_check("spy_present", spy_problems, "SPY cached and covering the first entry day"))

    used = {e["symbol_used"] for e in enriched if e["symbol_used"]}
    stale = [s for s in sorted(used | {MARKET}) if cache.entry(s) and
             (cache.entry(s)["requested_start"], cache.entry(s)["requested_end"]) != (start, end)]
    checks.append(_check("cache_consistent", stale,
                         f"every symbol fetched for [{start}, {end}) like SPY"))

    bad = []
    price_cols = ["entry_date", "entry_price", "spy_entry_price"]
    for e in enriched:
        key = f"{e['accession_number']}#{e['nonderiv_trans_sk']}"
        if e["price_status"] not in BUY_STATUSES:
            bad.append(f"{key}: price_status {e['price_status']!r}")
            continue
        priced = e["price_status"] == "priced"
        if priced != all(e[c] for c in price_cols):
            bad.append(f"{key}: entry fields do not match price_status {e['price_status']}")
        for n in windows:
            k, ws = f"{n}d", e[f"window_status_{n}d"]
            filled = [bool(e[c]) for c in window_columns(n)[1:6]]
            if ws not in WINDOW_STATUSES:
                bad.append(f"{key}: window_status_{k} {ws!r}")
            elif (ws == "no_entry_price") == priced:
                bad.append(f"{key}: window_status_{k} {ws} with price_status {e['price_status']}")
            elif (ws == "closed") != all(filled) or (ws != "closed" and any(filled)):
                bad.append(f"{key}: window {k} {ws} but return fields "
                           f"{'missing' if ws == 'closed' else 'present'}")
    checks.append(_check("status_complete", bad,
                         "every buy has a known status; no number without a closed window"))

    look = []
    for e in enriched:
        if e["price_status"] != "priced":
            continue
        key = f"{e['accession_number']}#{e['nonderiv_trans_sk']}"
        i = bisect_right(cal, e["filing_date"])
        if i >= len(cal) or e["entry_date"] != cal[i] or e["entry_date"] <= e["filing_date"]:
            look.append(f"{key}: entry {e['entry_date']} is not the first trading day after "
                        f"{e['filing_date']}")
            continue
        series = cache.series(e["symbol_used"]) or {}
        if _fmt(series.get(e["entry_date"]), 6) != e["entry_price"] or \
                _fmt((spy or {}).get(e["entry_date"]), 6) != e["spy_entry_price"]:
            look.append(f"{key}: entry price differs from the cache")
        for n in windows:
            k = f"{n}d"
            if e[f"exit_date_{k}"] and (i + n >= len(cal) or e[f"exit_date_{k}"] != cal[i + n]):
                look.append(f"{key}: exit {e[f'exit_date_{k}']} is not {n} trading days after entry")
            if (i + n < len(cal)) == (e[f"window_status_{k}"] == "not_yet_closed"):
                look.append(f"{key}: window {k} closed-ness disagrees with the calendar")
            if e[f"window_status_{k}"] == "closed":
                if _fmt(series.get(e[f"exit_date_{k}"]), 6) != e[f"exit_price_{k}"] or \
                        _fmt((spy or {}).get(e[f"exit_date_{k}"]), 6) != e[f"spy_exit_price_{k}"]:
                    look.append(f"{key}: window {k} exit prices differ from the cache")
                sr = _ret(float(e[f"exit_price_{k}"]), float(e["entry_price"]))
                mr = _ret(float(e[f"spy_exit_price_{k}"]), float(e["spy_entry_price"]))
                if (_r(sr), _r(mr), _r(sr - mr)) != (e[f"stock_return_{k}"], e[f"spy_return_{k}"],
                                                     e[f"abnormal_return_{k}"]):
                    look.append(f"{key}: window {k} returns do not recompute")
    checks.append(_check("lookahead", look,
                         "entry = first SPY day after FILING_DATE; exit = entry + N SPY days"))

    fp = []
    for e in enriched:
        key = f"{e['accession_number']}#{e['nonderiv_trans_sk']}"
        st = e["price_status"]
        if st in ("priced", "price_mismatch_vs_filing"):
            want = filing_price_check(e, cache, splits)
            if want is None:
                fp.append(f"{key}: no split data for {e['symbol_used']}")
                continue
            got = {c: e[c] for c in CHECK_COLUMNS}
            if got != want:
                fp.append(f"{key}: Rule 9 fields do not recompute ({got['filing_price_check']} vs "
                          f"{want['filing_price_check']})")
            elif (st == "price_mismatch_vs_filing") != (want["filing_price_check"] == "mismatch"):
                fp.append(f"{key}: price_status {st} disagrees with the Rule 9 verdict")
        elif any(e[c] for c in CHECK_COLUMNS):
            fp.append(f"{key}: Rule 9 fields on a buy with price_status {st}")
    checks.append(_check("filing_price_check", fp,
                         f"filed price within {MISMATCH_TOLERANCE:.0%} of the split-adjusted "
                         "unadjusted close on TRANS_DATE, else price_mismatch_vs_filing (Rule 9)"))

    priced = sum(e["price_status"] == "priced" for e in enriched)
    cov = priced / len(enriched) if enriched else 0.0
    checks.append(_check("coverage", [] if enriched and cov >= MIN_COVERAGE else
                         [f"{priced:,} of {len(enriched):,} priced = {cov:.2%} < {MIN_COVERAGE:.0%}"],
                         f"priced ÷ verified buys = {cov:.2%} (minimum {MIN_COVERAGE:.0%}, Rule 8)"))
    return checks


# --------------------------------------------------------------------------- findings

def findings(enriched: list[dict], cache: PriceCache, windows: Iterable[int] = WINDOWS) -> dict:
    windows = tuple(windows)
    by_q: dict[str, Counter] = defaultdict(Counter)
    win: dict[int, dict[str, Counter]] = {n: defaultdict(Counter) for n in windows}
    for e in enriched:
        q = e["source_quarter"]
        by_q[q][e["price_status"]] += 1
        for n in windows:
            win[n][q][e[f"window_status_{n}d"]] += 1
    total = Counter()
    for c in by_q.values():
        total.update(c)
    n_all = sum(total.values())

    coverage = {q: {"buys": sum(c.values()), "priced": c["priced"],
                    "pct": round(100 * c["priced"] / sum(c.values()), 2)}
                for q, c in sorted(by_q.items())}
    coverage["all"] = {"buys": n_all, "priced": total["priced"],
                       "pct": round(100 * total["priced"] / n_all, 2) if n_all else 0.0}

    windows_out = {}
    for n in windows:
        tot = Counter()
        for c in win[n].values():
            tot.update(c)
        windows_out[f"{n}d"] = {"by_quarter": {q: dict(c) for q, c in sorted(win[n].items())},
                                "total": dict(tot)}

    raw_unusual = Counter()
    for e in enriched:
        if e["price_status"] in ("blank_symbol", "placeholder_symbol", "multiple_symbols",
                                 "unparseable_symbol"):
            raw_unusual[(e["ticker_as_filed"], e["price_status"])] += 1
    unpriced_issuers = Counter()
    for e in enriched:
        if e["price_status"] in ("no_data", "series_ends_before_entry",
                                 "series_starts_after_entry", "fetch_error"):
            unpriced_issuers[(e["issuer_cik"], e["issuer_name"], e["symbol_used"],
                              e["price_status"])] += 1
    sym_issuers: dict[str, set] = defaultdict(set)
    for e in enriched:
        if e["symbol_used"]:
            sym_issuers[e["symbol_used"]].add(e["issuer_cik"])
    shared = {s: sorted(c) for s, c in sym_issuers.items() if len(c) > 1}
    issuer_syms: dict[str, set] = defaultdict(set)
    for e in enriched:
        if e["symbol_used"]:
            issuer_syms[e["issuer_cik"]].add(e["symbol_used"])

    cached = Counter(v["status"] for v in cache.manifest["symbols"].values())
    return {
        "filing_price_check": rule9_findings(enriched),
        "coverage": coverage,
        "price_status": {"by_quarter": {q: dict(c) for q, c in sorted(by_q.items())},
                         "total": dict(total)},
        "windows": windows_out,
        "unusual_symbols": [{"ticker_as_filed": t, "price_status": s, "buys": k}
                            for (t, s), k in raw_unusual.most_common()],
        "unpriced_issuers_top": [{"issuer_cik": c, "issuer_name": n, "symbol": s,
                                  "price_status": st, "buys": k}
                                 for (c, n, s, st), k in unpriced_issuers.most_common(25)],
        "symbols_shared_by_issuers": {"count": len(shared),
                                      "buys": sum(1 for e in enriched if e["symbol_used"] in shared),
                                      "examples": dict(list(sorted(shared.items()))[:15])},
        "issuers_with_several_symbols": sum(1 for v in issuer_syms.values() if len(v) > 1),
        "distinct_symbols": len(sym_issuers),
        "cache_status": dict(cached),
    }


def _band(x: float, edges: list[tuple[float, str]], last: str) -> str:
    for edge, label in edges:
        if x < edge:
            return label
    return last


def _truthy(v: str) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes")


def rule9_findings(enriched: list[dict]) -> dict:
    """What kinds of buys fail Rule 9 (counts only; no returns)."""
    checked = [e for e in enriched if e["filing_price_check"]]
    mism = [e for e in checked if e["filing_price_check"] == "mismatch"]
    kinds: dict[str, Counter] = {k: Counter() for k in
                                 ("filed_price", "direction", "flags", "split_applied",
                                  "ref_gap_days", "document_type", "quarter")}
    for e in mism:
        filed, ratio = float(e["price"]), float(e["filed_vs_close_ratio"])
        kinds["filed_price"][_band(filed, [(1, "< $1"), (5, "$1–5"), (20, "$5–20")], "≥ $20")] += 1
        kinds["direction"][_band(ratio, [(0.1, "filed < 10% of close"),
                                         (0.5, "filed 10–50% of close"),
                                         (0.75, "filed 50–75% of close"),
                                         (2.0, "filed 125–200% of close"),
                                         (10.0, "filed 2–10× close")], "filed > 10× close")] += 1
        flags = [n for n, c in (("private", "private_purchase_flag"), ("espp_or_drip", "espp_or_drip_flag"))
                 if _truthy(e[c])]
        kinds["flags"]["+".join(flags) or "no flag"] += 1
        kinds["split_applied"]["yes" if float(e["split_factor"]) != 1.0 else "no"] += 1
        gap = (date.fromisoformat(e["trans_date"]) - date.fromisoformat(e["trade_ref_date"])).days
        kinds["ref_gap_days"][_band(gap, [(1, "same day"), (4, "1–3 days"), (31, "4–30 days")],
                                    "> 30 days")] += 1
        kinds["document_type"][e["document_type"]] += 1
        kinds["quarter"][e["source_quarter"]] += 1
    by_issuer = Counter((e["issuer_cik"], e["issuer_name"], e["symbol_used"]) for e in mism)
    return {
        "checked": len(checked),
        "verdicts": dict(Counter(e["filing_price_check"] for e in checked)),
        "split_applied_in_checked": sum(1 for e in checked
                                        if e["split_factor"] and float(e["split_factor"]) != 1.0),
        "mismatch_kinds": {k: dict(c.most_common()) for k, c in kinds.items()},
        "mismatch_issuers_top": [{"issuer_cik": c, "issuer_name": n, "symbol": s, "buys": k}
                                 for (c, n, s), k in by_issuer.most_common(20)],
        "mismatch_issuers": len(by_issuer),
    }


# --------------------------------------------------------------------------- run

def run(verified_dir: Path, prices_dir: Path, staging_dir: Path, source: PriceSource | None,
        end: date, *, offline: bool = False, refresh: bool = False,
        batch_size: int = BATCH_SIZE, pause_s: float = PAUSE_S, backoff_s: float = BACKOFF_S,
        sleep: Callable[[float], None] = time.sleep, clock: Callable[[], float] = time.monotonic,
        log: Callable[[str], None] = print) -> int:
    buys_path = verified_dir / BUYS_NAME
    if not buys_path.exists():
        raise EnrichError(f"{buys_path} not found: run parse.py and conformance.py first (G2).")
    rows = read_csv(buys_path)
    input_sha = ingest.sha256_file(buys_path)
    csum_path = verified_dir / CONFORMANCE_SUMMARY
    expected_sha = (json.loads(csum_path.read_text(encoding="utf-8")).get("insider_buys_sha256", "")
                    if csum_path.exists() else "")
    start, end_s = fetch_range(rows, end)
    cache = PriceCache(prices_dir)

    symbols = {s for s, _ in (normalize_symbol(r["ticker_as_filed"]) for r in rows) if s}
    fetch_stats: dict = {"requested": 0}
    if not offline:
        if source is None:
            source = YFinanceSource()
        try:
            fetch_stats = fetch_missing(symbols | {MARKET}, cache, source, start, end_s,
                                        batch_size=batch_size, pause_s=pause_s,
                                        backoff_s=backoff_s, refresh=refresh, sleep=sleep,
                                        clock=clock, log=log)
        except PriceSourceRefused as exc:
            log(f"enrich: HALT — {exc}")
            return 3

    spy = cache.series(MARKET)
    cal = sorted(spy) if spy else []
    # Rule 9 needs split histories: only for symbols with at least one buy priced at entry.
    pre = [enrich_row(r, cache, cal, spy or {}, offline=offline, apply_rule_9=False) for r in rows]
    split_symbols = {e["symbol_used"] for e in pre if e["price_status"] == "priced"}
    s_start, s_end = splits_range(cache, start)
    splits = SplitCache(prices_dir)
    split_stats: dict = {"requested": 0}
    if not offline and split_symbols:
        try:
            split_stats = fetch_missing(split_symbols, splits, source, s_start, s_end,
                                        batch_size=batch_size, pause_s=pause_s,
                                        backoff_s=backoff_s, refresh=refresh, sleep=sleep,
                                        clock=clock, log=log, kind="splits")
        except PriceSourceRefused as exc:
            log(f"enrich: HALT — {exc}")
            return 3
    enriched = [enrich_row(r, cache, cal, spy or {}, offline=offline, splits=splits)
                for r in rows]
    checks = run_checks(rows, enriched, cache, cal, spy, input_sha, expected_sha, start, end_s,
                        splits=splits)
    failed = [c["check"] for c in checks if not c["passed"]]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary = {
        "run_at": _utc_now(), "script": "enrich.py", "promoted": not failed,
        "failed_checks": failed, "halting_checks": checks,
        "rules": {"windows_trading_days": list(WINDOWS), "min_coverage": MIN_COVERAGE,
                  "entry": "adjusted close, first SPY trading day after FILING_DATE",
                  "filing_price_tolerance": MISMATCH_TOLERANCE,
                  "registered": "PRE_REGISTRATION.md Rules 7-9 (2026-11-09)"},
        "input": {"file": f"data/verified/{BUYS_NAME}", "sha256": input_sha, "rows": len(rows)},
        "prices": {"source": "Yahoo Finance via yfinance (adjusted close, auto_adjust=False)",
                   "requested_start": start, "requested_end_exclusive": end_s,
                   "market_symbol": MARKET, "market_as_of": cal[-1] if cal else None,
                   "manifest_sha256": (ingest.sha256_file(prices_dir / PRICES_MANIFEST)
                                       if (prices_dir / PRICES_MANIFEST).exists() else None),
                   "fetch": fetch_stats, "fetch_log_totals": fetch_log_totals(prices_dir),
                   "splits": {"requested_start": s_start, "requested_end_exclusive": s_end,
                              "symbols": len(split_symbols), "fetch": split_stats,
                              "manifest_sha256": (ingest.sha256_file(prices_dir / SPLITS_MANIFEST)
                                                  if (prices_dir / SPLITS_MANIFEST).exists()
                                                  else None)},
                   "offline": offline},
        "findings": findings(enriched, cache),
    }
    if failed:
        staging_dir.mkdir(parents=True, exist_ok=True)
        (staging_dir / f"enrich-audit-FAILED-{stamp}.md").write_text(render_audit(summary),
                                                                     encoding="utf-8")
        (staging_dir / f"enrich_summary-FAILED-{stamp}.json").write_text(
            json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
        log(f"enrich: HALT — failed {', '.join(failed)}; data/verified/ unchanged; audit in "
            f"{staging_dir.name}/")
        return 1
    _promote(verified_dir, staging_dir, stamp, enriched, summary)
    cov = summary["findings"]["coverage"]["all"]
    log(f"enrich: promoted {len(enriched):,} rows → data/verified/{ENRICHED_NAME}; "
        f"priced {cov['priced']:,} ({cov['pct']}%)")
    return 0


def _promote(verified_dir: Path, staging_dir: Path, stamp: str, enriched: list[dict],
             summary: dict) -> None:
    stage = staging_dir / f"stage-{stamp}"
    stage.mkdir(parents=True, exist_ok=True)
    enriched = sorted(enriched, key=lambda r: (r["filing_date"], r["accession_number"],
                                               int(r["nonderiv_trans_sk"])))
    with open(stage / ENRICHED_NAME, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ENRICHED_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(enriched)
    summary["enriched_buys_sha256"] = ingest.sha256_file(stage / ENRICHED_NAME)
    (stage / AUDIT_NAME).write_text(render_audit(summary), encoding="utf-8")
    (stage / SUMMARY_NAME).write_text(json.dumps(summary, indent=2, default=str) + "\n",
                                      encoding="utf-8")
    verified_dir.mkdir(parents=True, exist_ok=True)
    for name in (SUMMARY_NAME, AUDIT_NAME, ENRICHED_NAME):
        os.replace(stage / name, verified_dir / name)
    shutil.rmtree(stage)


def check(verified_dir: Path, prices_dir: Path, log: Callable[[str], None] = print) -> int:
    """G3: re-verify the promoted file against the cache and the input, without any request."""
    path = verified_dir / ENRICHED_NAME
    spath = verified_dir / SUMMARY_NAME
    if not path.exists() or not spath.exists():
        log("enrich --check: no promoted enriched_buys.csv")
        return 1
    summary = json.loads(spath.read_text(encoding="utf-8"))
    rows = read_csv(verified_dir / BUYS_NAME)
    enriched = read_csv(path)
    cache = PriceCache(prices_dir)
    spy = cache.series(MARKET)
    cal = sorted(spy) if spy else []
    p = summary["prices"]
    csum = json.loads((verified_dir / CONFORMANCE_SUMMARY).read_text(encoding="utf-8"))
    checks = run_checks(rows, enriched, cache, cal, spy, ingest.sha256_file(verified_dir / BUYS_NAME),
                        csum.get("insider_buys_sha256", ""), p["requested_start"],
                        p["requested_end_exclusive"], splits=SplitCache(prices_dir))
    keys_in = sorted(f"{r['accession_number']}#{r['nonderiv_trans_sk']}" for r in rows)
    keys_out = sorted(f"{r['accession_number']}#{r['nonderiv_trans_sk']}" for r in enriched)
    checks.append(_check("rows_match_input", [] if keys_in == keys_out else
                         [f"{len(keys_in):,} verified buys vs {len(keys_out):,} enriched rows"],
                         "one enriched row per verified buy, none dropped"))
    sha_ok = ingest.sha256_file(path) == summary.get("enriched_buys_sha256")
    checks.append(_check("output_hash", [] if sha_ok else ["enriched_buys.csv hash changed"],
                         "enriched_buys.csv matches enrich_summary.json"))
    for c in checks:
        log(f"  {'PASS' if c['passed'] else 'FAIL'}  {c['check']:<17} {c['detail']}"
            + ("" if c["passed"] else f" — {c['examples'][:2]}"))
    return 0 if all(c["passed"] for c in checks) else 1


# --------------------------------------------------------------------------- audit

def _n(v) -> str:
    return f"{v:,}" if isinstance(v, int) else str(v)


def _md(text) -> str:
    return str(text).replace("|", "\\|")


def render_audit(s: dict) -> str:
    f = s["findings"]
    title = "Enrich audit (G3)" if s["promoted"] else "Enrich audit (G3) — NOT PROMOTED"
    p = s["prices"]
    L = [f"# {title}", "",
         f"Run at {s['run_at']} by `enrich.py`. This audit reports what was found. The halting "
         "checks decide promotion; clearing G3 is the owner's logged decision.", "",
         f"- Input: `{s['input']['file']}`, {s['input']['rows']:,} buys, SHA-256 `{s['input']['sha256']}`",
         f"- Prices: {p['source']}; requested {p['requested_start']} to {p['requested_end_exclusive']} "
         f"(end exclusive); market calendar = {p['market_symbol']} bars, last bar **{p['market_as_of']}**",
         f"- Rules: windows {', '.join(str(n) for n in s['rules']['windows_trading_days'])} trading days; "
         f"minimum coverage {s['rules']['min_coverage']:.0%} ({s['rules']['registered']})"]
    if s["promoted"]:
        L.append(f"- **Promoted:** `data/verified/{ENRICHED_NAME}` "
                 f"(SHA-256 `{s.get('enriched_buys_sha256', '')}`)")
    else:
        L.append(f"- **Not promoted.** Failed: {', '.join(s['failed_checks'])}. "
                 "Nothing in `data/verified/` was changed.")
    L += ["", "**Returns are computed per buy in the enriched file but not summarized here:** no "
          "averages or other return statistics are reported before the signals are registered.", "",
          "## Halting checks", "", "| Check | Result | Violations | Detail |", "|---|---|---:|---|"]
    for c in s["halting_checks"]:
        L.append(f"| {c['check']} | {'PASS' if c['passed'] else '**FAIL**'} | {c['violations']:,} "
                 f"| {_md(c['detail'])} |")
        for ex in c["examples"][:3]:
            L.append(f"| | | | ↳ {_md(ex)} |")

    L += ["", "## Price coverage (priced ÷ verified buys)", "",
          "| Quarter | Buys | Priced | Coverage |", "|---|---:|---:|---:|"]
    for q, c in f["coverage"].items():
        label = "**All**" if q == "all" else q
        L.append(f"| {label} | {c['buys']:,} | {c['priced']:,} | {c['pct']:.2f}% |")

    statuses = [st for st in BUY_STATUSES if f["price_status"]["total"].get(st)]
    L += ["", "## price_status", "", "| Status | Buys | Share |", "|---|---:|---:|"]
    n_all = f["coverage"]["all"]["buys"]
    for st in statuses:
        k = f["price_status"]["total"][st]
        L.append(f"| {st} | {k:,} | {100 * k / n_all:.2f}% |")
    L += ["", "By quarter:", "", "| Quarter | " + " | ".join(statuses) + " |",
          "|---|" + "---:|" * len(statuses)]
    for q, c in f["price_status"]["by_quarter"].items():
        L.append(f"| {q} | " + " | ".join(_n(c.get(st, 0)) for st in statuses) + " |")

    for wk, w in f["windows"].items():
        ws = [st for st in WINDOW_STATUSES if w["total"].get(st)]
        L += ["", f"## Window {wk}: window status", "",
              "| Quarter | " + " | ".join(ws) + " |", "|---|" + "---:|" * len(ws)]
        for q, c in w["by_quarter"].items():
            L.append(f"| {q} | " + " | ".join(_n(c.get(st, 0)) for st in ws) + " |")
        L.append("| **All** | " + " | ".join(f"**{w['total'].get(st, 0):,}**" for st in ws) + " |")

    r9 = f.get("filing_price_check")
    if r9:
        v = r9["verdicts"]
        L += ["", "## Filed price vs market close (Rule 9)", "",
              f"Checked {r9['checked']:,} buys priced at entry: ok {v.get('ok', 0):,} · "
              f"**mismatch {v.get('mismatch', 0):,}** (→ `price_mismatch_vs_filing`, no returns) · "
              f"not checkable {v.get('not_checkable', 0):,} (no bar on or before the trade date). "
              f"A split adjustment was applied to {r9['split_applied_in_checked']:,} checked buys. "
              f"Mismatches come from {r9['mismatch_issuers']:,} issuers.", ""]
        titles = {"filed_price": "Filed price", "direction": "Filed price ÷ reference close",
                  "flags": "PARSE flags (Rule 1)", "split_applied": "Split adjustment applied",
                  "ref_gap_days": "Reference bar before the trade date",
                  "document_type": "Document type", "quarter": "Quarter"}
        for k, title in titles.items():
            c = r9["mismatch_kinds"].get(k, {})
            if not c:
                continue
            L += [f"Mismatches by {title.lower()}:", "", f"| {title} | Buys |", "|---|---:|"]
            items = sorted(c.items()) if k == "quarter" else c.items()
            L += [f"| {_md(a)} | {b:,} |" for a, b in items] + [""]
        L += ["Issuers with the most mismatches:", "", "| Issuer CIK | Issuer | Symbol | Buys |",
              "|---|---|---|---:|"]
        L += [f"| {u['issuer_cik']} | {_md(u['issuer_name'])} | {u['symbol']} | {u['buys']:,} |"
              for u in r9["mismatch_issuers_top"]]

    L += ["", "## Symbols", "",
          f"- Distinct symbols requested from the buys: {f['distinct_symbols']:,}; price cache: "
          + ", ".join(f"{k} {v:,}" for k, v in sorted(f["cache_status"].items())),
          f"- Symbols used by more than one issuer CIK: {f['symbols_shared_by_issuers']['count']:,} "
          f"({f['symbols_shared_by_issuers']['buys']:,} buys). The symbol is as filed and is not "
          "checked against the issuer; a shared symbol may be a reuse after a rename or a filing error.",
          f"- Issuers filing under more than one symbol: {f['issuers_with_several_symbols']:,}",
          "", "Unusual symbols as filed (not priced; not mapped):", "",
          "| ticker_as_filed | price_status | Buys |", "|---|---|---:|"]
    for u in f["unusual_symbols"]:
        L.append(f"| `{_md(u['ticker_as_filed']) or '(blank)'}` | {u['price_status']} | {u['buys']:,} |")
    L += ["", "Issuers with the most unpriced buys (no data or a series that does not cover entry):",
          "", "| Issuer CIK | Issuer | Symbol | price_status | Buys |", "|---|---|---|---|---:|"]
    for u in f["unpriced_issuers_top"]:
        L.append(f"| {u['issuer_cik']} | {_md(u['issuer_name'])} | {u['symbol']} | "
                 f"{u['price_status']} | {u['buys']:,} |")
    fs = p["fetch"]
    sp = p.get("splits", {})
    spf = sp.get("fetch", {})
    L += ["", "## Fetch", "",
          f"- Splits (Rule 9): {sp.get('symbols', 0):,} symbols with a priced buy; range "
          f"{sp.get('requested_start')} to {sp.get('requested_end_exclusive')} (end exclusive). "
          f"This run requested {spf.get('requested', 0):,} (ok {spf.get('ok', 0):,}, no data "
          f"{spf.get('no_data', 0):,}, errors {spf.get('fetch_error', 0):,}, refusals "
          f"{spf.get('refusals', 0):,}).",
          f"- This run: {fs.get('requested', 0):,} symbols requested in {fs.get('batches', 0):,} "
          f"batches; ok {fs.get('ok', 0):,}, no data {fs.get('no_data', 0):,}, errors "
          f"{fs.get('fetch_error', 0):,}, refusals {fs.get('refusals', 0):,}. Every batch is in "
          f"`data/raw/prices/{FETCH_LOG}`." + (" Offline run: no requests." if p["offline"] else ""),
          "- All runs (`fetch_log.jsonl`): {batch_requests:,} batch requests, {symbol_requests:,} "
          "symbol requests, {refused:,} refused; {first_ts} to {last_ts}.".format(
              **{"symbol_requests": 0, "refused": 0, "first_ts": "—", "last_ts": "—",
                 **p.get("fetch_log_totals", {})}),
          "- Yahoo Finance is not an authoritative source; adjusted closes reflect Yahoo's "
          "adjustments as of the fetch date (`prices_manifest.json`, `fetched_at`).", ""]
    return "\n".join(L)


# --------------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--verified-dir", type=Path, default=DEFAULT_VERIFIED_DIR)
    ap.add_argument("--prices-dir", type=Path, default=DEFAULT_PRICES_DIR)
    ap.add_argument("--staging-dir", type=Path, default=DEFAULT_STAGING_DIR)
    ap.add_argument("--end", type=date.fromisoformat, default=None,
                    help="last fetch date, exclusive (default: today, so the last bar is a full close)")
    ap.add_argument("--offline", action="store_true", help="use the cache only; no requests")
    ap.add_argument("--refresh", action="store_true", help="re-download every symbol")
    ap.add_argument("--check", action="store_true", help="G3: re-verify the promoted file")
    ap.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    ap.add_argument("--pause", type=float, default=PAUSE_S, help="seconds between batches")
    a = ap.parse_args(argv)
    if a.check:
        return check(a.verified_dir, a.prices_dir)
    if a.batch_size < 1 or a.batch_size > 100 or a.pause < 1.0:
        print("enrich: refused — batch size must be 1–100 and the pause at least 1 s",
              file=sys.stderr)
        return 2
    end = a.end
    if end is None:
        if a.offline:
            m = PriceCache(a.prices_dir).entry(MARKET)
            end = date.fromisoformat(m["requested_end"]) if m else date.today()
        else:
            end = date.today()
    try:
        return run(a.verified_dir, a.prices_dir, a.staging_dir, None, end, offline=a.offline,
                   refresh=a.refresh, batch_size=a.batch_size, pause_s=a.pause)
    except EnrichError as exc:
        print(f"enrich: refused — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

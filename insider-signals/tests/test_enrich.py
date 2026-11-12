"""
ENRICH / gate G3 (enrich.py): prices, windows, price_status, the cache and promotion.

What is pinned here:
  - entry is the adjusted close on the first trading day (SPY bar) strictly after FILING_DATE;
    exits are exactly 21 and 63 trading days after entry; spy_return uses the identical dates and
    abnormal_return = stock_return − spy_return (PRE_REGISTRATION.md Rule 7);
  - a window whose exit is after the last SPY bar is not_yet_closed and carries no numbers;
  - every buy that cannot be priced keeps its row and gets a reason: blank / placeholder /
    multiple / unparseable symbol, no_data, fetch_error, series ending before entry or exit,
    series starting after entry, no bar on the entry or exit day. Nothing is filled in;
  - symbols are used as filed with mechanical normalization only;
  - the cache: a re-run makes no requests; a symbol with no data is not asked again; a fetch
    error is retried; --refresh re-asks;
  - requests go in batches with a pause between them, SPY first; a refusal backs off and retries
    once, a second refusal halts (exit 3) with nothing promoted and finished batches cached;
  - coverage below 80% (Rule 8) or an input hash mismatch halts (exit 1) and writes nothing to
    data/verified/; the failure audit goes to the staging folder;
  - Rule 9: the filed price is compared with the unadjusted close on the trade date (or the
    prior trading day): forward and reverse splits after the trade are undone, a split on the
    trade day or after the price fetch is not; more than 25% off → price_mismatch_vs_filing with
    no prices or returns; exactly 25% passes; no bar on or before the trade → not_checkable;
    missing split data halts; split histories are cached; mismatches count against coverage;
  - --check re-verifies the promoted file and catches a tampered return or Rule 9 field;
  - the audit reports no return figures;
  - yfinance is never imported when a source is injected.

No network: the price source is a scripted fake. Prices are synthetic.
"""

from __future__ import annotations

import csv
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import conformance  # noqa: E402
import enrich  # noqa: E402
import ingest  # noqa: E402

CAL_START = date(2024, 1, 1)          # a Monday


def trading_days(n: int, start: date = CAL_START) -> list[str]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


CAL = trading_days(120)               # 2024-01-01 … about 2024-06-14


def bars(days: list[str], p0: float, step: float) -> list[tuple]:
    return [(d, p0 + i * step, p0 + i * step, 1000.0) for i, d in enumerate(days)]


class FakeSource:
    """Scripted price source. `script` maps symbol → bars or an error message. `refuse` is a
    list of booleans consumed per call: True → that call answers with a rate-limit error."""

    def __init__(self, script: dict, refuse: list[bool] | None = None,
                 splits: dict | None = None):
        self.script, self.refuse, self.calls = script, list(refuse or []), []
        self.splits, self.split_calls = splits or {}, []

    def download_splits(self, symbols, start, end):
        self.split_calls.append(list(symbols))
        data, errors = {}, {}
        for s in symbols:
            if isinstance(self.script.get(s), list):
                data[s] = list(self.splits.get(s, []))
            else:
                errors[s] = "possibly delisted; no price data found"
        return data, errors

    def download(self, symbols, start, end):
        self.calls.append(list(symbols))
        if self.refuse and self.refuse.pop(0):
            return {}, {s: "YFRateLimitError('Too Many Requests. Rate limited.')" for s in symbols}
        data, errors = {}, {}
        for s in symbols:
            v = self.script.get(s, "possibly delisted; no price data found")
            if isinstance(v, str):
                errors[s] = v
            else:
                data[s] = v
        return data, errors


def vrow(i: int, filing_date: str, ticker: str, quarter: str = "2024q1") -> dict:
    r = {c: "" for c in conformance.VERIFIED_COLUMNS}
    r.update(accession_number=f"0000000000-24-{i:06d}", nonderiv_trans_sk=str(i),
             document_type="4", filing_date=filing_date, trans_date=filing_date,
             issuer_cik=str(1000 + i), issuer_name=f"Issuer {i}", ticker_as_filed=ticker,
             owner_count="1", rptowner_ciks=str(9000 + i), trans_code="P", shares="100",
             price="10.00", source_quarter=quarter)
    return r


def fill_filed_prices(rows: list[dict], script: dict) -> None:
    """Give each buy the market close on its trade date as its filed price, so Rule 9 passes
    unless a test says otherwise."""
    for r in rows:
        sym = enrich.normalize_symbol(r["ticker_as_filed"])[0]
        series = script.get(sym)
        if isinstance(series, list):
            before = [b for b in series if b[0] <= r["trans_date"]]
            if before and before[-1][1] > 0:
                r["price"] = f"{before[-1][1]:.2f}"


def write_verified(vdir: Path, rows: list[dict], script: dict | None = None,
                   bad_sha: bool = False) -> None:
    if script:
        fill_filed_prices(rows, script)
    vdir.mkdir(parents=True, exist_ok=True)
    with open(vdir / conformance.BUYS_NAME, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=conformance.VERIFIED_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    sha = "0" * 64 if bad_sha else ingest.sha256_file(vdir / conformance.BUYS_NAME)
    (vdir / conformance.SUMMARY_NAME).write_text(json.dumps({"insider_buys_sha256": sha}))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.vdir, self.pdir, self.sdir = self.tmp / "verified", self.tmp / "prices", self.tmp / "stage"
        self.sleeps: list[float] = []
        self.logs: list[str] = []

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_enrich(self, source, end=date(2024, 7, 1), **kw):
        kw.setdefault("pause_s", 1.0)
        kw.setdefault("backoff_s", 5.0)
        return enrich.run(self.vdir, self.pdir, self.sdir, source, end, sleep=self.sleeps.append,
                          clock=lambda: 0.0, log=self.logs.append, **kw)

    def enriched(self) -> dict[str, dict]:
        with open(self.vdir / enrich.ENRICHED_NAME, newline="", encoding="utf-8") as fh:
            return {r["ticker_as_filed"] + "|" + r["filing_date"]: r for r in csv.DictReader(fh)}


# --------------------------------------------------------------------------- symbols

class TestNormalizeSymbol(unittest.TestCase):
    def test_table(self):
        cases = {
            "AAPL": ("AAPL", None), " aapl ": ("AAPL", None), "fmbm": ("FMBM", None),
            "BRK.B": ("BRK-B", None), "HEI-A": ("HEI-A", None),
            "": (None, "blank_symbol"), "   ": (None, "blank_symbol"),
            "NONE": (None, "placeholder_symbol"), "none": (None, "placeholder_symbol"),
            "[ N/A ]": (None, "placeholder_symbol"), "N.A.": (None, "placeholder_symbol"),
            "NA": (None, "placeholder_symbol"), "[NONE": (None, "placeholder_symbol"),
            "GEF, GEF-B": (None, "multiple_symbols"), "BCDA;BCDAW": (None, "multiple_symbols"),
            "NASDAQ:DHC": (None, "unparseable_symbol"), "AXIA3": (None, "unparseable_symbol"),
            "RANGER": (None, "unparseable_symbol"), "WLY/WLYB": (None, "unparseable_symbol"),
            "(SIRI)": (None, "unparseable_symbol"), "SNV PRE": (None, "unparseable_symbol"),
        }
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(enrich.normalize_symbol(raw), want)


# --------------------------------------------------------------------------- windows

class TestWindows(Base):
    def setUp(self):
        super().setUp()
        self.spy = bars(CAL, 400.0, 1.0)
        self.script = {"SPY": self.spy, "AAA": bars(CAL, 10.0, 0.1)}

    def test_entry_is_first_trading_day_after_filing_and_exits_are_n_days_later(self):
        filed = {"2024-01-10": "2024-01-11",      # Wednesday → Thursday (not the same day)
                 "2024-01-12": "2024-01-15",      # Friday → Monday
                 "2024-01-13": "2024-01-15"}      # Saturday → Monday
        rows = [vrow(i, fd, "AAA") for i, fd in enumerate(filed)]
        write_verified(self.vdir, rows, getattr(self, "script", None))
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 0)
        out = self.enriched()
        for fd, entry in filed.items():
            r = out[f"AAA|{fd}"]
            with self.subTest(filing=fd):
                self.assertEqual(r["price_status"], "priced")
                self.assertEqual(r["entry_date"], entry)
                i = CAL.index(entry)
                self.assertEqual(r["exit_date_21d"], CAL[i + 21])
                self.assertEqual(r["exit_date_63d"], CAL[i + 63])
                e, x = 10.0 + 0.1 * i, 10.0 + 0.1 * (i + 21)
                se, sx = 400.0 + i, 400.0 + i + 21
                self.assertAlmostEqual(float(r["stock_return_21d"]), x / e - 1, places=7)
                self.assertAlmostEqual(float(r["spy_return_21d"]), sx / se - 1, places=7)
                self.assertAlmostEqual(float(r["abnormal_return_21d"]),
                                       (x / e - 1) - (sx / se - 1), places=7)
                self.assertEqual(r["window_status_21d"], "closed")
                self.assertEqual(r["window_status_63d"], "closed")

    def test_windows_after_last_market_day_are_not_yet_closed(self):
        # CAL has 120 days. Entry at index 70: 21d closes (91 < 120); 63d does not (133).
        # Entry at index 110: neither closes.
        rows = [vrow(1, CAL[69], "AAA"), vrow(2, CAL[109], "AAA")]
        write_verified(self.vdir, rows, getattr(self, "script", None))
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 0)
        out = self.enriched()
        a, b = out[f"AAA|{CAL[69]}"], out[f"AAA|{CAL[109]}"]
        self.assertEqual((a["window_status_21d"], a["window_status_63d"]), ("closed", "not_yet_closed"))
        self.assertEqual((b["window_status_21d"], b["window_status_63d"]),
                         ("not_yet_closed", "not_yet_closed"))
        for col in enrich.window_columns(63)[:6]:
            self.assertEqual(a[col], "", col)
        self.assertEqual(b["stock_return_21d"], "")
        self.assertEqual(b["price_status"], "priced")       # entry known; windows open

    def test_spy_return_uses_identical_dates_even_when_stock_has_gaps(self):
        gappy = [b for b in bars(CAL, 10.0, 0.1) if b[0] != CAL[30]]   # stock missing one day
        self.script["GAP"] = gappy
        rows = [vrow(1, CAL[4], "GAP")]    # entry CAL[5]; 21d exit CAL[26]; 63d exit CAL[68]
        write_verified(self.vdir, rows, getattr(self, "script", None))
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 0)
        r = self.enriched()[f"GAP|{CAL[4]}"]
        self.assertEqual(r["exit_date_21d"], CAL[26])
        self.assertAlmostEqual(float(r["spy_return_21d"]), (400 + 26) / (400 + 5) - 1, places=7)


# --------------------------------------------------------------------------- price_status

class TestPriceStatus(Base):
    def test_every_unpriceable_buy_is_kept_with_a_reason(self):
        early = CAL[:40]                    # ends before most exits
        script = {
            "SPY": bars(CAL, 400.0, 1.0),
            "OK": bars(CAL, 10.0, 0.1),
            "ENDS": bars(CAL[:20], 5.0, 0.0),             # ends before entry at CAL[30]
            "LATE": bars(CAL[50:], 5.0, 0.0),             # starts after entry at CAL[30]
            "HOLE": [b for b in bars(CAL, 5.0, 0.0) if b[0] != CAL[30]],
            "DIES": bars(early, 5.0, 0.0),                # entry CAL[30] ok; exit CAL[51] gone
            "XHOLE": [b for b in bars(CAL, 5.0, 0.0) if b[0] != CAL[51]],
            "ZERO": [(d, 0.0, 0.0, 0.0) for d in CAL],
            "FLAKY": "HTTPError: 500 Server Error",
        }
        filing = CAL[29]                                  # entry CAL[30], 21d exit CAL[51]
        tickers = {"OK": "priced", "": "blank_symbol", "NONE": "placeholder_symbol",
                   "GEF, GEF-B": "multiple_symbols", "NASDAQ:DHC": "unparseable_symbol",
                   "GONE": "no_data", "FLAKY": "fetch_error", "ENDS": "series_ends_before_entry",
                   "LATE": "series_starts_after_entry", "HOLE": "no_bar_on_entry_date",
                   "ZERO": "invalid_entry_price", "DIES": "priced", "XHOLE": "priced"}
        rows = [vrow(i, filing, t) for i, t in enumerate(tickers)]
        rows += [vrow(90 + i, filing, "OK") for i in range(40)]     # keep coverage ≥ 80%
        write_verified(self.vdir, rows, script)
        self.assertEqual(self.run_enrich(FakeSource(script)), 0, self.logs)
        out = self.enriched()
        with open(self.vdir / enrich.ENRICHED_NAME, newline="") as fh:
            self.assertEqual(len(list(csv.DictReader(fh))), len(rows))   # nothing dropped
        for t, st in tickers.items():
            r = out[f"{t}|{filing}"]
            with self.subTest(ticker=t):
                self.assertEqual(r["price_status"], st)
                if st != "priced":
                    self.assertEqual((r["entry_price"], r["stock_return_21d"]), ("", ""))
                    self.assertEqual(r["window_status_21d"], "no_entry_price")
        self.assertEqual(out[f"DIES|{filing}"]["window_status_21d"], "series_ends_before_exit")
        self.assertEqual(out[f"XHOLE|{filing}"]["window_status_21d"], "no_bar_on_exit_date")
        self.assertEqual(out[f"DIES|{filing}"]["abnormal_return_21d"], "")


# --------------------------------------------------------------------------- cache and fetching

class TestCacheAndFetch(Base):
    def setUp(self):
        super().setUp()
        self.script = {"SPY": bars(CAL, 400.0, 1.0), "AAA": bars(CAL, 10.0, 0.1),
                       "BBB": bars(CAL, 20.0, 0.1), "CCC": bars(CAL, 30.0, 0.1),
                       "DDD": bars(CAL, 40.0, 0.1)}
        rows = [vrow(i, CAL[5], t) for i, t in enumerate(["AAA", "BBB", "CCC", "DDD", "GONE"] * 4)]
        write_verified(self.vdir, rows, getattr(self, "script", None))

    def test_rerun_makes_no_requests_and_no_data_is_not_asked_again(self):
        src = FakeSource(self.script)
        self.assertEqual(self.run_enrich(src, batch_size=2), 0)
        first = sum(len(c) for c in src.calls)
        self.assertEqual(first, 6)                        # SPY + 4 + GONE
        src2 = FakeSource(self.script)
        self.assertEqual(self.run_enrich(src2, batch_size=2), 0)
        self.assertEqual(src2.calls, [])
        m = json.loads((self.pdir / enrich.PRICES_MANIFEST).read_text())
        self.assertEqual(m["symbols"]["GONE"]["status"], "no_data")
        self.assertTrue(m["symbols"]["AAA"]["sha256"])
        self.assertTrue(m["symbols"]["AAA"]["fetched_at"])

    def test_fetch_error_is_retried_and_refresh_re_asks_everything(self):
        self.script["DDD"] = "ConnectionError: timed out"
        self.run_enrich(FakeSource(self.script))       # 60% priced: halts at coverage
        m = json.loads((self.pdir / enrich.PRICES_MANIFEST).read_text())
        self.assertEqual(m["symbols"]["DDD"]["status"], "fetch_error")
        self.script["DDD"] = bars(CAL, 40.0, 0.1)
        src = FakeSource(self.script)
        self.run_enrich(src)
        self.assertEqual([s for c in src.calls for s in c], ["DDD"])
        src3 = FakeSource(self.script)
        self.run_enrich(src3, refresh=True)
        self.assertEqual(sum(len(c) for c in src3.calls), 6)

    def test_batches_spy_first_with_pause_between(self):
        src = FakeSource(self.script)
        self.run_enrich(src, batch_size=2, pause_s=3.0)
        self.assertEqual(src.calls[0][0], "SPY")
        self.assertEqual([len(c) for c in src.calls], [2, 2, 2])
        # prices: 3 batches, 2 pauses; then splits for the 4 priced symbols: 2 batches, 1 pause
        self.assertEqual(self.sleeps, [3.0, 3.0, 3.0])
        self.assertEqual([len(c) for c in src.split_calls], [2, 2])
        log = [json.loads(l) for l in (self.pdir / enrich.FETCH_LOG).read_text().splitlines()]
        self.assertEqual([l["kind"] for l in log], ["prices"] * 3 + ["splits"] * 2)
        self.assertEqual({k for k in log[0]} >= {"ts", "symbols", "ok", "failed", "refused"}, True)

    def test_one_refusal_backs_off_and_retries(self):
        src = FakeSource(self.script, refuse=[False, True])     # second batch refused once
        self.assertEqual(self.run_enrich(src, batch_size=2, pause_s=1.0, backoff_s=60.0), 0)
        self.assertIn(60.0, self.sleeps)
        self.assertEqual(len(src.calls), 4)

    def test_second_refusal_halts_exit_3_and_promotes_nothing(self):
        src = FakeSource(self.script, refuse=[False, True, True])
        self.assertEqual(self.run_enrich(src, batch_size=2), 3)
        self.assertFalse((self.vdir / enrich.ENRICHED_NAME).exists())
        m = json.loads((self.pdir / enrich.PRICES_MANIFEST).read_text())
        self.assertEqual(sorted(m["symbols"]), ["AAA", "SPY"])  # first batch kept in the cache
        self.assertTrue(any("HALT" in l for l in self.logs))
        # the next run resumes: only the remaining symbols are requested
        src2 = FakeSource(self.script)
        self.assertEqual(self.run_enrich(src2, batch_size=2), 0)
        self.assertNotIn("AAA", [s for c in src2.calls for s in c])

    def test_a_whole_batch_failing_counts_as_a_refusal(self):
        many = {f"Z{chr(65 + i)}{chr(65 + j)}" for i in range(4) for j in range(6)}   # 24 symbols
        rows = [vrow(i, CAL[5], t) for i, t in enumerate(sorted(many))]
        write_verified(self.vdir, rows, getattr(self, "script", None))
        src = FakeSource({"SPY": bars(CAL, 400.0, 1.0)})        # every Z… symbol fails
        rc = self.run_enrich(src, batch_size=12)
        self.assertEqual(rc, 3)

    def test_yfinance_is_not_imported_with_an_injected_source(self):
        self.run_enrich(FakeSource(self.script))
        self.assertNotIn("yfinance", sys.modules)


# --------------------------------------------------------------------------- Rule 9

def flat(days: list[str], p: float) -> list[tuple]:
    return [(d, p, p, 1000.0) for d in days]


class TestFiledPriceCheck(Base):
    """Rule 9: filed price vs the unadjusted close on the trade date, splits accounted for."""

    def setUp(self):
        super().setUp()
        self.script = {"SPY": bars(CAL, 400.0, 1.0)}
        self.splits: dict = {}
        self.filler = [vrow(900 + i, CAL[10], "FILL") for i in range(40)]   # keeps coverage ≥ 80%
        self.script["FILL"] = flat(CAL, 10.0)
        for r in self.filler:
            r["price"] = "10.00"

    def go(self, rows, expect_rc=0, source=None):
        write_verified(self.vdir, rows + self.filler)
        rc = self.run_enrich(source or FakeSource(self.script, splits=self.splits))
        self.assertEqual(rc, expect_rc, self.logs)
        if rc != 0:
            return None
        with open(self.vdir / enrich.ENRICHED_NAME, newline="") as fh:
            return {r["accession_number"]: r for r in csv.DictReader(fh)}

    def row(self, i, sym, trade, filing, price):
        r = vrow(i, filing, sym)
        r.update(trans_date=trade, price=price)
        return r

    def test_forward_split_after_trade_is_undone(self):
        # Yahoo's Close is split-adjusted: 50 throughout; a 2:1 split on CAL[20] means the
        # trade on CAL[5] really printed near 100.
        self.script["FWD"] = flat(CAL, 50.0)
        self.script["NOSP"] = flat(CAL, 50.0)
        self.splits["FWD"] = [(CAL[20], 2.0)]
        rows = [self.row(1, "FWD", CAL[5], CAL[6], "100.00"),
                self.row(2, "NOSP", CAL[5], CAL[6], "100.00")]
        out = self.go(rows)
        a, b = out[rows[0]["accession_number"]], out[rows[1]["accession_number"]]
        self.assertEqual((a["price_status"], a["filing_price_check"]), ("priced", "ok"))
        self.assertEqual(a["split_factor"], "2.000000")
        self.assertEqual(a["trade_ref_close_unadjusted"], "100.000000")
        # without a split the same filing is a mismatch: no prices, no returns
        self.assertEqual((b["price_status"], b["filing_price_check"]),
                         ("price_mismatch_vs_filing", "mismatch"))
        self.assertEqual(b["filed_vs_close_ratio"], "2.000000")
        for c in ("entry_date", "entry_price", "spy_entry_price", "exit_price_21d",
                  "stock_return_21d", "abnormal_return_21d", "abnormal_return_63d"):
            self.assertEqual(b[c], "", c)
        self.assertEqual(b["window_status_21d"], "no_entry_price")

    def test_reverse_split_and_split_on_trade_day(self):
        self.script["REV"] = flat(CAL, 10.0)
        self.splits["REV"] = [(CAL[30], 0.1)]          # 1-for-10 after the trade
        self.script["SAME"] = flat(CAL, 50.0)
        self.splits["SAME"] = [(CAL[5], 2.0)]          # split on the trade day: not applied
        rows = [self.row(1, "REV", CAL[5], CAL[6], "1.00"),
                self.row(2, "SAME", CAL[5], CAL[6], "50.00")]
        out = self.go(rows)
        rev, same = out[rows[0]["accession_number"]], out[rows[1]["accession_number"]]
        self.assertEqual((rev["filing_price_check"], rev["split_factor"]), ("ok", "0.100000"))
        self.assertEqual((same["filing_price_check"], same["split_factor"]), ("ok", "1.000000"))

    def test_split_after_the_price_fetch_is_not_applied(self):
        self.script["LATE"] = flat(CAL, 50.0)
        self.splits["LATE"] = [("2099-01-02", 2.0)]
        rows = [self.row(1, "LATE", CAL[5], CAL[6], "50.00")]
        out = self.go(rows)
        self.assertEqual(out[rows[0]["accession_number"]]["split_factor"], "1.000000")

    def test_weekend_trade_uses_the_prior_trading_day(self):
        days = [d for d in CAL]
        self.script["WK"] = [(d, 10.0 if d <= "2024-01-12" else 20.0, 10.0, 1.0) for d in days]
        rows = [self.row(1, "WK", "2024-01-13", "2024-01-16", "10.00")]   # Saturday trade
        r = self.go(rows)[rows[0]["accession_number"]]
        self.assertEqual((r["trade_ref_date"], r["filing_price_check"]), ("2024-01-12", "ok"))

    def test_25_percent_boundary(self):
        self.script["B"] = flat(CAL, 10.0)
        cases = {"12.50": "ok", "12.51": "mismatch", "7.50": "ok", "7.49": "mismatch"}
        rows = [self.row(i, "B", CAL[5], CAL[6], p) for i, p in enumerate(cases)]
        out = self.go(rows)
        for r, (p, want) in zip(rows, cases.items()):
            with self.subTest(filed=p):
                self.assertEqual(out[r["accession_number"]]["filing_price_check"], want)

    def test_no_bar_on_or_before_trade_date_is_not_checkable_and_stays_priced(self):
        self.script["NEW"] = flat(CAL[8:], 99.0)        # starts after the trade, before entry
        rows = [self.row(1, "NEW", CAL[5], CAL[9], "1.00")]
        r = self.go(rows)[rows[0]["accession_number"]]
        self.assertEqual((r["price_status"], r["filing_price_check"]), ("priced", "not_checkable"))
        self.assertEqual(r["window_status_21d"], "closed")

    def test_missing_split_data_halts_and_promotes_nothing(self):
        self.script["NS"] = flat(CAL, 10.0)

        class NoSplits(FakeSource):
            def download_splits(self, symbols, start, end):
                return {s: [] for s in symbols if s != "NS"}, {"NS": "HTTPError: 500 Server Error"}

        rows = [self.row(1, "NS", CAL[5], CAL[6], "10.00")]
        self.go(rows, expect_rc=1, source=NoSplits(self.script))
        self.assertFalse((self.vdir / enrich.ENRICHED_NAME).exists())
        failed = next(self.sdir.glob("enrich-audit-FAILED-*.md")).read_text()
        self.assertIn("filing_price_check | **FAIL**", failed)

    def test_mismatches_can_push_coverage_below_80_percent_and_halt(self):
        self.script["BAD"] = flat(CAL, 10.0)
        self.filler = self.filler[:4]
        rows = [self.row(i, "BAD", CAL[5], CAL[6], "50.00") for i in range(2)]   # 4 of 6 priced
        self.go(rows, expect_rc=1)
        failed = next(self.sdir.glob("enrich-audit-FAILED-*.md")).read_text()
        self.assertIn("coverage | **FAIL**", failed)
        self.assertIn("Filed price vs market close (Rule 9)", failed)
        self.assertIn("mismatch 2", failed)

    def test_splits_are_cached_and_check_catches_a_tampered_verdict(self):
        self.script["C"] = flat(CAL, 10.0)
        rows = [self.row(1, "C", CAL[5], CAL[6], "10.00")]
        self.go(rows)
        src = FakeSource(self.script, splits=self.splits)
        self.assertEqual(self.run_enrich(src), 0)
        self.assertEqual((src.calls, src.split_calls), ([], []))
        path = self.vdir / enrich.ENRICHED_NAME
        with open(path, newline="") as fh:
            rs = list(csv.DictReader(fh))
        rs[0]["filed_vs_close_ratio"] = "1.900000"
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=enrich.ENRICHED_COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(rs)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(enrich.check(self.vdir, self.pdir), 1)
        self.assertIn("FAIL  filing_price_check", out.getvalue())


# --------------------------------------------------------------------------- halting and promotion

class TestHaltingAndCheck(Base):
    def setUp(self):
        super().setUp()
        self.script = {"SPY": bars(CAL, 400.0, 1.0), "AAA": bars(CAL, 10.0, 0.1)}

    def _existing(self):
        self.vdir.mkdir(parents=True, exist_ok=True)
        (self.vdir / enrich.ENRICHED_NAME).write_text("old\n")
        return {p.name: p.read_bytes() for p in self.vdir.iterdir()}

    def test_coverage_below_80_percent_halts_and_verified_is_unchanged(self):
        rows = [vrow(i, CAL[5], "AAA") for i in range(7)] + [vrow(10 + i, CAL[5], "NONE")
                                                             for i in range(3)]   # 70%
        write_verified(self.vdir, rows, getattr(self, "script", None))
        before = self._existing()
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 1)
        self.assertEqual({p.name: p.read_bytes() for p in self.vdir.iterdir()}, before)
        failed = list(self.sdir.glob("enrich-audit-FAILED-*.md"))
        self.assertEqual(len(failed), 1)
        self.assertIn("coverage | **FAIL**", failed[0].read_text())

    def test_exactly_80_percent_passes(self):
        rows = [vrow(i, CAL[5], "AAA") for i in range(8)] + [vrow(10 + i, CAL[5], "")
                                                             for i in range(2)]
        write_verified(self.vdir, rows, getattr(self, "script", None))
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 0)

    def test_input_hash_mismatch_halts(self):
        write_verified(self.vdir, [vrow(1, CAL[5], "AAA")], self.script, bad_sha=True)
        before = self._existing()
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 1)
        self.assertEqual({p.name: p.read_bytes() for p in self.vdir.iterdir()}, before)

    def test_check_passes_then_catches_a_tampered_return(self):
        write_verified(self.vdir, [vrow(i, CAL[5], "AAA") for i in range(3)], self.script)
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 0)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(enrich.check(self.vdir, self.pdir), 0)
        path = self.vdir / enrich.ENRICHED_NAME
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        rows[0]["abnormal_return_21d"] = "0.50000000"
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=enrich.ENRICHED_COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(enrich.check(self.vdir, self.pdir), 1)
        self.assertIn("FAIL  lookahead", out.getvalue())

    def test_audit_reports_no_return_figures(self):
        write_verified(self.vdir, [vrow(i, CAL[5 + i], "AAA") for i in range(5)], self.script)
        self.assertEqual(self.run_enrich(FakeSource(self.script)), 0)
        audit = (self.vdir / enrich.AUDIT_NAME).read_text()
        rets = set()
        for r in self.enriched().values():
            for n in enrich.WINDOWS:
                for c in (f"stock_return_{n}d", f"spy_return_{n}d", f"abnormal_return_{n}d"):
                    if r[c]:
                        rets.add(r[c])
        self.assertTrue(rets)
        for v in rets:
            self.assertNotIn(v, audit)
        self.assertIn("## Price coverage", audit)
        summary = json.loads((self.vdir / enrich.SUMMARY_NAME).read_text())
        self.assertNotIn("return", json.dumps(summary["findings"]).replace("not_yet_closed", ""))


if __name__ == "__main__":
    unittest.main()

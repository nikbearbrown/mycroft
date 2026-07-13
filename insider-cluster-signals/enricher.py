"""Purpose: Join verified trades with local price history; compute 30-day SPY-adjusted returns.
Input: data/verified/trades.json + data/raw/prices/*.csv (fetched by price_fetcher.py).
Output: data/verified/enriched_trades.json + data/raw/enrichment-rejects.json (reasons, never dropped).
Side effects: Local file writes only; NO network (pure transform layer, P2).
Idempotent: Yes; same inputs yield same outputs except the generated timestamp.
Recipe: recipes/insider-cluster-signal-agent.md

Alpha methodology mirrors congressional-signals/market_adjusted.py (branch pr-3) for
cross-regime comparability:
    raw_return_30d = (close_+30d / close_t0 - 1) * 100      [nearest prior trading day]
    spy_return_30d = same formula on SPY over the same window
    alpha_30d      = raw_return_30d - spy_return_30d         [rounded to 4 decimals]
A window whose +30d date extends past the available price series is marked immature
(alpha null, reason recorded) rather than silently using a shorter window.
"""

from __future__ import annotations

import argparse
import json
from bisect import bisect_right
from datetime import datetime, timedelta, timezone
from pathlib import Path

WINDOW_DAYS = 30
BENCHMARK = "SPY"
# Codes enriched: only actual market transactions. Grants (A), gifts (G), exercises (M/X),
# tax withholding (F) etc. have no market-timing information in their price field.
MARKET_CODES = {"P", "S"}


def load_price_series(csv_path: Path) -> list[tuple[str, float]] | None:
    """Read a Stooq CSV into a sorted [(date, close)] list; None if malformed."""
    lines = csv_path.read_text().strip().splitlines()
    if not lines or not lines[0].startswith("Date,"):
        return None
    header = lines[0].split(",")
    try:
        close_idx = header.index("Close")
    except ValueError:
        return None
    series = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) <= close_idx:
            continue
        try:
            datetime.strptime(parts[0], "%Y-%m-%d")
            series.append((parts[0], float(parts[close_idx])))
        except ValueError:
            continue  # skip malformed rows; count is visible via manifest row count
    series.sort()
    return series or None


def close_on_or_before(series: list[tuple[str, float]], date: str) -> float | None:
    """Close on `date` or the nearest prior trading day (pr-3 lookup semantics)."""
    dates = [d for d, _ in series]
    idx = bisect_right(dates, date)
    return series[idx - 1][1] if idx else None


def window_return(series: list[tuple[str, float]], t0: str) -> tuple[float | None, str | None]:
    """(percent return over t0 -> t0+30d, reason-if-none). Immature if series ends before t0+30d."""
    t30 = (datetime.strptime(t0, "%Y-%m-%d") + timedelta(days=WINDOW_DAYS)).strftime("%Y-%m-%d")
    if series[-1][0] < t30:
        return None, f"window not matured (series ends {series[-1][0]}, needs {t30})"
    c0 = close_on_or_before(series, t0)
    c30 = close_on_or_before(series, t30)
    if c0 is None or c30 is None or c0 == 0:
        return None, f"no close available at window edge (t0={t0})"
    return round((c30 / c0 - 1) * 100, 4), None


def enrich(trades_path: Path, prices_dir: Path, verified_dir: Path, raw_dir: Path) -> dict:
    records = json.loads(trades_path.read_text())["records"]
    spy_series = load_price_series(prices_dir / f"{BENCHMARK}.csv") if (prices_dir / f"{BENCHMARK}.csv").exists() else None

    series_cache: dict[str, list | None] = {}
    enriched, rejects = [], []
    sells_out_of_scope = 0

    for r in records:
        if r["transaction_code"] not in MARKET_CODES:
            continue  # non-market codes are out of scope by design, not rejects
        ticker = r["ticker"]
        if ticker not in series_cache:
            csv_path = prices_dir / f"{ticker}.csv"
            series_cache[ticker] = load_price_series(csv_path) if csv_path.exists() else None
        series = series_cache[ticker]

        if series is None:
            if r["transaction_code"] == "S":
                # Price scope is P-tickers (the signal carriers); a sell on a ticker with no
                # requested series is out of scope, not a data defect.
                sells_out_of_scope += 1
                continue
            rejects.append({**r, "reject_reasons": ["non-priceable ticker (no usable price series)"]})
            continue
        if r["price_per_share"] == 0:
            rejects.append({**r, "reject_reasons": ["market-code trade with price 0 (implausible)"]})
            continue
        if spy_series is None:
            rejects.append({**r, "reject_reasons": ["benchmark series SPY missing"]})
            continue

        raw_return, raw_reason = window_return(series, r["transaction_date"])
        spy_return, spy_reason = window_return(spy_series, r["transaction_date"])
        alpha = round(raw_return - spy_return, 4) if raw_return is not None and spy_return is not None else None
        enriched.append(
            {
                **r,
                "close_t0": close_on_or_before(series, r["transaction_date"]),
                "raw_return_30d": raw_return,
                "spy_return_30d": spy_return,
                "alpha_30d": alpha,
                "alpha_unavailable_reason": raw_reason or spy_reason,
            }
        )

    verified_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "enriched_at": datetime.now(timezone.utc).isoformat(),
        "market_trades_in": len(enriched) + len(rejects) + sells_out_of_scope,
        "sells_out_of_scope": sells_out_of_scope,
        "enriched": len(enriched),
        "with_alpha": sum(1 for e in enriched if e["alpha_30d"] is not None),
        "immature_or_edge": sum(1 for e in enriched if e["alpha_30d"] is None),
        "rejected": len(rejects),
    }
    (verified_dir / "enriched_trades.json").write_text(
        json.dumps({"summary": summary, "records": enriched}, indent=2) + "\n"
    )
    (raw_dir / "enrichment-rejects.json").write_text(json.dumps({"rejects": rejects}, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich verified market trades with 30-day SPY-adjusted returns.")
    module_dir = Path(__file__).parent
    parser.add_argument("--trades", default=str(module_dir / "data" / "verified" / "trades.json"))
    parser.add_argument("--prices-dir", default=str(module_dir / "data" / "raw" / "prices"))
    parser.add_argument("--verified-dir", default=str(module_dir / "data" / "verified"))
    parser.add_argument("--raw-dir", default=str(module_dir / "data" / "raw"))
    args = parser.parse_args()
    print(json.dumps(enrich(Path(args.trades), Path(args.prices_dir), Path(args.verified_dir), Path(args.raw_dir)), indent=2))


if __name__ == "__main__":
    main()

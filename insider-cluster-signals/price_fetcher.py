"""Purpose: Fetch daily close prices for open-market-purchase tickers + SPY benchmark.
Input: data/verified/trades.json (code-P tickers) or --tickers override; --start/--end date range.
Output: data/raw/prices/{TICKER}.csv (Date,Close) + data/raw/price-manifest-*.json with SHA-256 provenance.
Side effects: HTTP GETs against query1.finance.yahoo.com (rate-limited, declared User-Agent).
Idempotent: Yes; re-fetching overwrites with current data, manifest records each run.
Recipe: recipes/insider-cluster-signal-agent.md

One of exactly two network callers in this module (with fetcher.py) — see DATA_CONTRACT.md (P2).
Provider decision history (DATA SOURCE TODO, human-closed):
  - 2026-07-13 Stooq CSV chosen by Sachin Vishaul Baskar (stdlib, keyless).
  - 2026-07-13 Stooq found to serve an anti-bot HTML wall for every programmatic request from
    this environment (evidence: price-manifest response_head entries). Decision re-made same
    day by Sachin Vishaul Baskar: Yahoo Finance v8 chart API via stdlib urllib — zero
    dependencies, same source yfinance wraps (methodological parity with the
    congressional-signals sibling). Research use, rate-limited.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Yahoo rejects default urllib UAs; a browser-style UA is required. Contact intent is
# documented here and in DATA_CONTRACT.md since the header can't carry it.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) mycroft-research"
RATE_LIMIT_SECONDS = 0.5
CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={p1}&period2={p2}&interval=1d"
BENCHMARK = "SPY"


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
    time.sleep(RATE_LIMIT_SECONDS)
    return data


def chart_to_csv(payload: dict) -> str | None:
    """Yahoo chart JSON -> 'Date,Close' CSV text; None if the payload has no usable series."""
    result = (payload.get("chart") or {}).get("result") or []
    if not result:
        return None
    timestamps = result[0].get("timestamp") or []
    closes = ((result[0].get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    rows = [
        f"{datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')},{close}"
        for ts, close in zip(timestamps, closes)
        if close is not None
    ]
    return "Date,Close\n" + "\n".join(rows) + "\n" if rows else None


def purchase_tickers(trades_path: Path) -> list[str]:
    """Tickers with at least one open-market purchase (code P) in the verified layer."""
    records = json.loads(trades_path.read_text())["records"]
    return sorted({r["ticker"] for r in records if r["transaction_code"] == "P"})


def fetch_prices(tickers: list[str], start: datetime, end: datetime, output_dir: Path) -> dict:
    prices_dir = output_dir / "prices"
    prices_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source": "Yahoo Finance v8 chart API (query1.finance.yahoo.com), daily closes",
        "range": {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")},
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "user_agent": USER_AGENT,
        "fetched": [],
        "non_priceable": [],
        "errors": [],
    }
    for ticker in [*tickers, BENCHMARK]:
        url = CHART_URL.format(
            symbol=ticker,
            p1=int(start.replace(tzinfo=timezone.utc).timestamp()),
            p2=int((end + timedelta(days=1)).replace(tzinfo=timezone.utc).timestamp()),
        )
        try:
            payload = json.loads(_get(url))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:  # unknown/delisted symbol
                manifest["non_priceable"].append({"ticker": ticker, "url": url, "response_head": "HTTP 404"})
            else:
                manifest["errors"].append({"ticker": ticker, "url": url, "error": f"HTTP {exc.code}"})
            continue
        except Exception as exc:
            manifest["errors"].append({"ticker": ticker, "url": url, "error": f"{type(exc).__name__}: {exc}"})
            continue

        csv_text = chart_to_csv(payload)
        if csv_text is None:
            manifest["non_priceable"].append({"ticker": ticker, "url": url, "response_head": str(payload)[:80]})
            continue
        out_path = prices_dir / f"{ticker}.csv"
        out_path.write_text(csv_text)
        manifest["fetched"].append(
            {
                "ticker": ticker,
                "url": url,
                "saved_to": str(out_path).replace("\\", "/"),
                "sha256": hashlib.sha256(csv_text.encode()).hexdigest(),
                "rows": len(csv_text.strip().splitlines()) - 1,
            }
        )

    manifest_path = output_dir / f"price-manifest-{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch daily prices for verified P-code tickers + SPY.")
    module_dir = Path(__file__).parent
    parser.add_argument("--trades", default=str(module_dir / "data" / "verified" / "trades.json"))
    parser.add_argument("--tickers", nargs="*", help="Override: explicit ticker list instead of trades.json.")
    parser.add_argument("--start", help="YYYY-MM-DD; default = 40 days before today.")
    parser.add_argument("--end", help="YYYY-MM-DD; default = today.")
    parser.add_argument("--output-dir", default=str(module_dir / "data" / "raw"))
    args = parser.parse_args()

    tickers = args.tickers if args.tickers else purchase_tickers(Path(args.trades))
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else datetime.now()
    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else end - timedelta(days=40)

    manifest = fetch_prices(tickers, start, end, Path(args.output_dir))
    print(
        json.dumps(
            {
                "tickers_requested": len(tickers) + 1,
                "fetched": len(manifest["fetched"]),
                "non_priceable": [t["ticker"] for t in manifest["non_priceable"]],
                "errors": len(manifest["errors"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

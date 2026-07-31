"""Purpose: Detect insider buy clusters — >=2 distinct insiders, same ticker, 30-day window.
Input: data/verified/enriched_trades.json (open-market purchases, code P, only).
Output: data/verified/cluster_signals.json — clusters with members, role-weighted conviction,
        mean 30d alpha, and the EDGAR accessions each conclusion traces to (P3).
Side effects: Local file writes only; no network.
Idempotent: Yes; deterministic given the same enriched input.
Recipe: recipes/insider-cluster-signal-agent.md

Cluster definition (Lakonishok & Lee 2001 lineage; window mirrors congressional-signals):
trades are grouped per ticker into greedy chronological windows — a window opens at the
first unassigned trade and absorbs every trade within WINDOW_DAYS of that open; a window
with >= MIN_INSIDERS distinct reporting owners is a cluster.

Role weights (DEFINE closure, recipe v0.2.0): officer 1.5, director 1.0, 10%-owner 0.75,
other 0.5 — officers trade closest to operating information, directors next, large holders
often rebalance mechanically (Cohen, Malloy & Pomorski 2012 distinguish exactly this
routine-vs-opportunistic gradient).
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

WINDOW_DAYS = 30
MIN_INSIDERS = 2
ROLE_WEIGHTS = {"officer": 1.5, "director": 1.0, "ten_percent_owner": 0.75, "other": 0.5}


def member_role(record: dict) -> str:
    """An insider's strongest role for weighting (officer > director > 10% > other)."""
    if record["is_officer"]:
        return "officer"
    if record["is_director"]:
        return "director"
    if record["is_ten_percent_owner"]:
        return "ten_percent_owner"
    return "other"


def windows_by_ticker(purchases: list[dict]) -> list[list[dict]]:
    """Greedy chronological 30-day windows per ticker (see module docstring)."""
    by_ticker: dict[str, list[dict]] = {}
    for r in purchases:
        by_ticker.setdefault(r["ticker"], []).append(r)

    windows = []
    for trades in by_ticker.values():
        trades.sort(key=lambda r: r["transaction_date"])
        current: list[dict] = []
        window_close = None
        for trade in trades:
            date = datetime.strptime(trade["transaction_date"], "%Y-%m-%d")
            if current and date <= window_close:
                current.append(trade)
            else:
                if current:
                    windows.append(current)
                current = [trade]
                window_close = date + timedelta(days=WINDOW_DAYS)
        if current:
            windows.append(current)
    return windows


def build_cluster(trades: list[dict]) -> dict:
    members: dict[str, dict] = {}
    for t in trades:
        m = members.setdefault(
            t["owner_cik"],
            {
                "owner_cik": t["owner_cik"],
                "owner_name": t["owner_name"],
                "role": member_role(t),
                "role_weight": ROLE_WEIGHTS[member_role(t)],
                "officer_title": t["officer_title"],
                "trades": 0,
                "shares": 0.0,
                "value_usd": 0.0,
            },
        )
        m["trades"] += 1
        m["shares"] += t["shares"]
        m["value_usd"] += t["shares"] * t["price_per_share"]

    alphas = [t["alpha_30d"] for t in trades if t["alpha_30d"] is not None]
    return {
        "ticker": trades[0]["ticker"],
        "issuer_name": trades[0]["issuer_name"],
        "window": {
            "start": min(t["transaction_date"] for t in trades),
            "end": max(t["transaction_date"] for t in trades),
        },
        "n_insiders": len(members),
        "n_trades": len(trades),
        "total_shares": round(sum(m["shares"] for m in members.values()), 2),
        "total_value_usd": round(sum(m["value_usd"] for m in members.values()), 2),
        "weighted_conviction": round(sum(m["role_weight"] for m in members.values()), 2),
        "mean_alpha_30d": round(sum(alphas) / len(alphas), 4) if alphas else None,
        "trades_with_alpha": len(alphas),
        "members": sorted(members.values(), key=lambda m: -m["role_weight"]),
        "accessions": sorted({t["accession"] for t in trades}),
    }


def analyze(enriched_path: Path, verified_dir: Path) -> dict:
    records = json.loads(enriched_path.read_text())["records"]
    purchases = [r for r in records if r["transaction_code"] == "P"]

    clusters = [
        build_cluster(w)
        for w in windows_by_ticker(purchases)
        if len({t["owner_cik"] for t in w}) >= MIN_INSIDERS
    ]
    clusters.sort(key=lambda c: -c["weighted_conviction"])

    summary = {
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "purchases_in": len(purchases),
        "tickers_seen": len({r["ticker"] for r in purchases}),
        "clusters_found": len(clusters),
        "window_days": WINDOW_DAYS,
        "min_insiders": MIN_INSIDERS,
        "role_weights": ROLE_WEIGHTS,
    }
    verified_dir.mkdir(parents=True, exist_ok=True)
    (verified_dir / "cluster_signals.json").write_text(
        json.dumps({"summary": summary, "clusters": clusters}, indent=2) + "\n"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect >=2-insider 30-day buy clusters in enriched trades.")
    module_dir = Path(__file__).parent
    parser.add_argument("--enriched", default=str(module_dir / "data" / "verified" / "enriched_trades.json"))
    parser.add_argument("--verified-dir", default=str(module_dir / "data" / "verified"))
    args = parser.parse_args()
    print(json.dumps(analyze(Path(args.enriched), Path(args.verified_dir)), indent=2))


if __name__ == "__main__":
    main()

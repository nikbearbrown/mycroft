"""
cluster_analyzer.py -- Cluster signal analysis and sector-level politician alpha profiles.

Produces two outputs:
  data/cluster_signals.json    -- all detected clusters with alpha, sector, politicians
  data/politician_profiles.json -- per-politician alpha broken down by sector

A cluster = 2+ politicians buying the same ticker within a 30-day rolling window.
Sector classification uses a 3-tier GICS-inspired map; tickers not in the map
fall back to 'general'.

Usage
-----
    python cluster_analyzer.py
    python cluster_analyzer.py --window 30 --min-pols 2
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"

# GICS-inspired sector map -- expand as dataset grows
SECTOR_MAP: dict[str, str] = {
    # Semiconductors
    "NVDA":"semiconductor","AMD":"semiconductor","INTC":"semiconductor",
    "MU":"semiconductor","MRVL":"semiconductor","AVGO":"semiconductor",
    "QCOM":"semiconductor","TSM":"semiconductor","AMAT":"semiconductor",
    "LRCX":"semiconductor","KLAC":"semiconductor","SNDK":"semiconductor",
    "TXN":"semiconductor","NXPI":"semiconductor","ON":"semiconductor",
    # Cybersecurity / AI infra
    "CRWD":"cybersecurity","FTNT":"cybersecurity","PANW":"cybersecurity",
    "DDOG":"cybersecurity","ZS":"cybersecurity","S":"cybersecurity",
    "OKTA":"cybersecurity","NET":"cybersecurity",
    # Cloud / AI platforms
    "MSFT":"ai_cloud","GOOGL":"ai_cloud","AMZN":"ai_cloud",
    "META":"ai_cloud","ORCL":"ai_cloud","CRM":"ai_cloud",
    # Healthcare / insurance
    "HUM":"healthcare","UNH":"healthcare","CVS":"healthcare",
    "ELV":"healthcare","MDT":"healthcare","BSX":"healthcare",
    "ABT":"healthcare","JNJ":"healthcare","PFE":"healthcare",
    "ABBV":"healthcare","LLY":"healthcare","MRK":"healthcare",
    # Defense / government contractors
    "LMT":"defense","RTX":"defense","NOC":"defense",
    "GD":"defense","BA":"defense","HII":"defense",
    # Energy
    "XOM":"energy","CVX":"energy","COP":"energy",
    "EOG":"energy","SLB":"energy","PSX":"energy",
    # Financials
    "JPM":"financials","BAC":"financials","GS":"financials",
    "MS":"financials","WFC":"financials","C":"financials",
    "BLK":"financials","SCHW":"financials",
    # Consumer / retail
    "AMZN":"consumer","COST":"consumer","WMT":"consumer",
    "TGT":"consumer","HD":"consumer","NKE":"consumer",
    "LULU":"consumer","DECK":"consumer","BKNG":"consumer",
}


def _load_enriched(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype=str)
    for col in ["price_at_trade", "price_at_disclosure",
                "price_30d_post_disclosure", "pct_change_post_disclosure",
                "spy_return_30d", "abnormal_return"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _valid_ticker(t: str) -> bool:
    t = str(t).strip()
    return bool(t) and t.replace("/","").replace("-","").isalpha() and len(t) <= 6


def detect_clusters(df: pd.DataFrame, window_days: int = 30, min_pols: int = 2) -> list[dict]:
    """Find every ticker bought by min_pols+ politicians within window_days."""
    buys = df[df["trade_type"].str.upper() == "BUY"].copy()
    buys = buys[buys["ticker"].apply(_valid_ticker)]
    buys["disc_dt"] = pd.to_datetime(buys["disclosure_date"], errors="coerce")
    buys = buys.dropna(subset=["disc_dt"])
    buys["ticker_up"] = buys["ticker"].str.upper()

    seen: set[str] = set()  # deduplicate clusters by (ticker, anchor_date)
    clusters: list[dict] = []

    for ticker, grp in buys.groupby("ticker_up"):
        grp = grp.sort_values("disc_dt")
        dates = grp["disc_dt"].tolist()

        for i, anchor in enumerate(dates):
            key = f"{ticker}|{anchor.date()}"
            if key in seen:
                continue
            window_end = anchor + timedelta(days=window_days)
            members_df = grp[(grp["disc_dt"] >= anchor) & (grp["disc_dt"] <= window_end)]
            pols = members_df["politician"].unique().tolist()
            if len(pols) < min_pols:
                continue
            seen.add(key)

            # Alpha stats for this cluster (only rows with abnormal_return)
            ab_rows = members_df["abnormal_return"].dropna()
            avg_alpha   = round(float(ab_rows.mean()), 4) if len(ab_rows) else None
            max_alpha   = round(float(ab_rows.max()),  4) if len(ab_rows) else None
            win_rate    = round(float((ab_rows > 0).mean() * 100), 1) if len(ab_rows) else None

            spy_rows = members_df["spy_return_30d"].dropna()
            avg_spy = round(float(spy_rows.mean()), 4) if len(spy_rows) else None

            sector = SECTOR_MAP.get(ticker, "general")

            clusters.append({
                "ticker":          ticker,
                "asset_name":      members_df["asset_name"].dropna().iloc[0] if members_df["asset_name"].dropna().any() else "",
                "sector":          sector,
                "cluster_size":    len(pols),
                "politicians":     sorted(pols),
                "anchor_date":     str(anchor.date()),
                "window_days":     window_days,
                "avg_alpha":       avg_alpha,
                "max_alpha":       max_alpha,
                "avg_spy":         avg_spy,
                "win_rate":        win_rate,
                "priced_trades":   int(len(ab_rows)),
            })

    clusters.sort(key=lambda c: (c["avg_alpha"] or -999), reverse=True)
    return clusters


def build_politician_profiles(df: pd.DataFrame) -> dict[str, dict]:
    """Per-politician alpha breakdown by sector."""
    profiles: dict[str, dict] = {}

    df2 = df[df["trade_type"].str.upper() == "BUY"].copy()
    df2 = df2[df2["ticker"].apply(_valid_ticker)]
    df2["sector"] = df2["ticker"].str.upper().map(SECTOR_MAP).fillna("general")

    for pol, grp in df.groupby("politician"):
        buys  = (grp["trade_type"].str.upper() == "BUY").sum()
        sells = (grp["trade_type"].str.upper() == "SELL").sum()
        bcr   = round(buys / (buys + sells), 3) if (buys + sells) > 0 else 0.5

        pol_buys = df2[df2["politician"] == pol]
        overall_ab = pol_buys["abnormal_return"].dropna()
        overall_alpha = round(float(overall_ab.mean()), 4) if len(overall_ab) else None
        overall_win   = round(float((overall_ab > 0).mean() * 100), 1) if len(overall_ab) else None

        sector_breakdown: dict[str, dict] = {}
        for sector, sgrp in pol_buys.groupby("sector"):
            ab = sgrp["abnormal_return"].dropna()
            if len(ab) == 0:
                continue
            sector_breakdown[sector] = {
                "avg_alpha":  round(float(ab.mean()), 4),
                "win_rate":   round(float((ab > 0).mean() * 100), 1),
                "n":          int(len(ab)),
                "tickers":    sorted([t for t in sgrp["ticker"].str.upper().unique().tolist() if isinstance(t, str)]),
            }

        # Best sector = highest avg_alpha with n >= 3
        qualified = {s: v for s, v in sector_breakdown.items() if v["n"] >= 3}
        best_sector = max(qualified, key=lambda s: qualified[s]["avg_alpha"]) if qualified else None

        profiles[pol] = {
            "bcr":            bcr,
            "total_trades":   int(len(grp)),
            "overall_alpha":  overall_alpha,
            "overall_win":    overall_win,
            "priced_buys":    int(len(overall_ab)),
            "best_sector":    best_sector,
            "sector_alpha":   sector_breakdown,
        }

    return profiles


def main():
    parser = argparse.ArgumentParser(description="Cluster signal detector + politician sector profiles")
    parser.add_argument("--csv",     default=str(DATA / "enriched_trades.csv"))
    parser.add_argument("--window",  type=int, default=30, help="Cluster window in days")
    parser.add_argument("--min-pols",type=int, default=2,  help="Min politicians per cluster")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] {csv_path} not found")
        return

    print(f"Loading {csv_path.name} ...")
    df = _load_enriched(csv_path)

    # -- Clusters --
    print(f"Detecting clusters (window={args.window}d, min_pols={args.min_pols}) ...")
    clusters = detect_clusters(df, args.window, args.min_pols)

    cluster_out = DATA / "cluster_signals.json"
    with open(cluster_out, "w") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "params": {"window_days": args.window, "min_politicians": args.min_pols},
            "total_clusters": len(clusters),
            "clusters": clusters,
        }, f, indent=2)

    pos = [c for c in clusters if (c["avg_alpha"] or 0) > 0]
    neg = [c for c in clusters if (c["avg_alpha"] or 0) <= 0]
    print(f"\n  Clusters found : {len(clusters)}")
    print(f"  Positive alpha : {len(pos)}")
    print(f"  Negative alpha : {len(neg)}")
    print(f"\n  Top 10 cluster signals:")
    for c in clusters[:10]:
        a = f"{c['avg_alpha']:+.2f}%" if c['avg_alpha'] is not None else "  n/a "
        print(f"    {c['ticker']:<6} [{c['sector']:<14}] pols={c['cluster_size']}  alpha={a}  win={c['win_rate']}%  n={c['priced_trades']}")
    print(f"\n  Cluster file -> {cluster_out}")

    # -- Politician profiles --
    print(f"\nBuilding politician sector profiles ...")
    profiles = build_politician_profiles(df)

    prof_out = DATA / "politician_profiles.json"
    with open(prof_out, "w") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_politicians": len(profiles),
            "profiles": profiles,
        }, f, indent=2)

    print(f"\n  Politician sector alpha breakdown:")
    ranked = sorted(profiles.items(), key=lambda x: (x[1]["overall_alpha"] or -999), reverse=True)
    for pol, p in ranked[:12]:
        a    = f"{p['overall_alpha']:+.2f}%" if p["overall_alpha"] is not None else "  n/a "
        best = f"  best_sector={p['best_sector']}" if p["best_sector"] else ""
        print(f"    {pol:<28} alpha={a}  bcr={p['bcr']:.2f}  n={p['priced_buys']}{best}")
    print(f"\n  Profile file -> {prof_out}\n")


if __name__ == "__main__":
    main()

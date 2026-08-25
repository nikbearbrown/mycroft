"""
signal_scorer.py -- Phase-gated signal scoring with provenance (Madison pattern).

For every BUY trade that passes conformance gates, computes a signal and records
full provenance. Outputs data/signal_log.json.

Signal tiers
------------
  STRONG  -- cluster ≥ 2 politicians AND politician avg_alpha > 1% AND score ≥ 1.5
  WATCH   -- passes gates but below STRONG threshold
  SKIP    -- fails any phase gate (recorded with reason)

Signal state
------------
  DRAFT    -- 30-day post-disclosure window has not yet closed (result unknown)
  VERIFIED -- window closed; actual abnormal_return is the outcome

Score formula
-------------
  score = cluster_size × politician_bcr × sector_multiplier
  sector_multiplier: 1.5 for semiconductor/AI/cybersecurity, 1.2 for healthcare, 1.0 otherwise

Usage
-----
    python signal_scorer.py
    python signal_scorer.py --csv data/enriched_trades.csv --out data/signal_log.json
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"

# Sector multipliers -- tickers that have shown committee-level oversight alpha
SECTOR_MAP: dict[str, tuple[str, float]] = {
    # Semiconductors / AI infra -> 1.5x
    "NVDA": ("semiconductor", 1.5), "AMD":  ("semiconductor", 1.5),
    "INTC": ("semiconductor", 1.5), "MU":   ("semiconductor", 1.5),
    "MRVL": ("semiconductor", 1.5), "AVGO": ("semiconductor", 1.5),
    "QCOM": ("semiconductor", 1.5), "TSM":  ("semiconductor", 1.5),
    "AMAT": ("semiconductor", 1.5), "LRCX": ("semiconductor", 1.5),
    "KLAC": ("semiconductor", 1.5), "SNDK": ("semiconductor", 1.5),
    # Cybersecurity -> 1.5x
    "CRWD": ("cybersecurity", 1.5), "FTNT": ("cybersecurity", 1.5),
    "PANW": ("cybersecurity", 1.5), "DDOG": ("cybersecurity", 1.5),
    "ZS":   ("cybersecurity", 1.5), "S":    ("cybersecurity", 1.5),
    # AI / cloud infra -> 1.5x
    "MSFT": ("ai_cloud", 1.5), "GOOGL": ("ai_cloud", 1.5),
    "AMZN": ("ai_cloud", 1.5), "META":  ("ai_cloud", 1.5),
    # Healthcare (active oversight) -> 1.2x
    "HUM":  ("healthcare", 1.2), "UNH": ("healthcare", 1.2),
    "CVS":  ("healthcare", 1.2), "ELV": ("healthcare", 1.2),
    "MDT":  ("healthcare", 1.2), "BSX": ("healthcare", 1.2),
}

TODAY = datetime.today().date()
EXHAUSTION_THRESHOLD = 15.0  # % price drift at which signal is considered priced-in


def _is_valid_ticker(ticker: str) -> bool:
    t = str(ticker).strip()
    return bool(t) and t.replace("/", "").replace("-", "").isalpha() and len(t) <= 6


def _signal_state(disclosure_date: str) -> str:
    try:
        dd = datetime.strptime(disclosure_date, "%Y-%m-%d").date()
        return "VERIFIED" if (dd + timedelta(days=30)) <= TODAY else "DRAFT"
    except Exception:
        return "DRAFT"


def _build_politician_profiles(df: pd.DataFrame) -> dict:
    """Per-politician: BCR, avg abnormal_return, win_rate, trade_count."""
    profiles = {}
    for pol, grp in df.groupby("politician"):
        buys  = (grp["trade_type"].str.upper() == "BUY").sum()
        sells = (grp["trade_type"].str.upper() == "SELL").sum()
        bcr   = round(buys / (buys + sells), 3) if (buys + sells) > 0 else 0.5

        buy_rows = grp[grp["trade_type"].str.upper() == "BUY"]
        priced   = buy_rows["abnormal_return"].dropna()
        avg_alpha = round(float(priced.mean()), 4) if len(priced) else 0.0
        win_rate  = round(float((priced > 0).mean() * 100), 1) if len(priced) else 0.0

        profiles[pol] = {
            "bcr":        bcr,
            "avg_alpha":  avg_alpha,
            "win_rate":   win_rate,
            "trade_count": int(len(grp)),
            "priced_buys": int(len(priced)),
        }
    return profiles


def _build_cluster_map(df: pd.DataFrame, window_days: int = 30) -> dict[str, list[str]]:
    """For each (ticker, disclosure_date) return list of politicians who BUY'd same ticker ±window."""
    buys = df[df["trade_type"].str.upper() == "BUY"].copy()
    buys = buys[buys["ticker"].apply(_is_valid_ticker)]
    buys["disclosure_date_dt"] = pd.to_datetime(buys["disclosure_date"], errors="coerce")
    buys = buys.dropna(subset=["disclosure_date_dt"])

    clusters: dict[str, list[str]] = {}
    for _, row in buys.iterrows():
        ticker = str(row["ticker"]).strip().upper()
        center = row["disclosure_date_dt"]
        lo = center - timedelta(days=window_days)
        hi = center + timedelta(days=window_days)

        members = buys[
            (buys["ticker"].str.upper() == ticker) &
            (buys["disclosure_date_dt"] >= lo) &
            (buys["disclosure_date_dt"] <= hi)
        ]["politician"].unique().tolist()

        key = f"{ticker}|{row['disclosure_date']}"
        clusters[key] = members
    return clusters


def score_trades(df: pd.DataFrame) -> list[dict]:
    pol_profiles = _build_politician_profiles(df)
    cluster_map  = _build_cluster_map(df)

    signals = []
    buy_rows = df[df["trade_type"].str.upper() == "BUY"].copy()

    for _, row in buy_rows.iterrows():
        ticker  = str(row.get("ticker", "")).strip().upper()
        pol     = str(row.get("politician", ""))
        disc_dt = str(row.get("disclosure_date", ""))
        tx_dt   = str(row.get("transaction_date", ""))
        profile = pol_profiles.get(pol, {"bcr": 0.5, "avg_alpha": 0.0, "win_rate": 0.0, "trade_count": 0, "priced_buys": 0})

        gates = {}

        # Gate 1 -- valid ticker
        g1 = _is_valid_ticker(ticker)
        gates["gate_1_valid_ticker"] = {
            "passed": g1,
            "evidence": ticker if g1 else f"invalid ticker '{ticker}'"
        }

        # Gate 2 -- has dates
        g2 = bool(disc_dt and disc_dt not in ("nan", "")) and bool(tx_dt and tx_dt not in ("nan", ""))
        gates["gate_2_has_dates"] = {
            "passed": g2,
            "evidence": f"tx={tx_dt} disc={disc_dt}" if g2 else "missing date(s)"
        }

        # Gate 3 -- has price data
        pid  = row.get("price_at_disclosure")
        p30  = row.get("price_30d_post_disclosure")
        pat  = row.get("price_at_trade")
        g3   = not (pd.isna(pid) or pd.isna(p30))
        gates["gate_3_has_prices"] = {
            "passed": g3,
            "evidence": f"disc={float(pid):.2f} post={float(p30):.2f}" if g3 else "prices missing"
        }

        # Gate 4 -- signal not already exhausted (price drift since transaction)
        g4 = True
        drift_evidence = "no trade price -- drift unknown"
        if g3 and not pd.isna(pat) and float(pat) > 0:
            drift = (float(pid) - float(pat)) / float(pat) * 100
            g4 = abs(drift) < EXHAUSTION_THRESHOLD
            drift_evidence = f"drift since tx: {drift:+.1f}% ({'exhausted' if not g4 else 'live'})"
        gates["gate_4_not_exhausted"] = {"passed": g4, "evidence": drift_evidence}

        passed_all = g1 and g2 and g3 and g4

        if not passed_all:
            first_fail = next(k for k, v in gates.items() if not v["passed"])
            signals.append({
                "politician":       pol,
                "ticker":           ticker,
                "transaction_date": tx_dt,
                "disclosure_date":  disc_dt,
                "signal":           "SKIP",
                "signal_state":     "N/A",
                "score":            0.0,
                "skip_reason":      first_fail,
                "gates":            gates,
                "provenance":       {"source_filing": str(row.get("trade_url", ""))}
            })
            continue

        # Scoring
        cluster_key  = f"{ticker}|{disc_dt}"
        cluster_pols = cluster_map.get(cluster_key, [pol])
        cluster_size = len(set(cluster_pols))
        sector, mult = SECTOR_MAP.get(ticker, ("general", 1.0))
        score = round(cluster_size * profile["bcr"] * mult, 3)

        if cluster_size >= 2 and profile["avg_alpha"] > 1.0 and score >= 1.5:
            signal = "STRONG"
        elif cluster_size >= 2 or profile["avg_alpha"] > 0:
            signal = "WATCH"
        else:
            signal = "SKIP"

        ab  = row.get("abnormal_return")
        spy = row.get("spy_return_30d")

        signals.append({
            "politician":       pol,
            "ticker":           ticker,
            "asset_name":       str(row.get("asset_name", "")),
            "transaction_date": tx_dt,
            "disclosure_date":  disc_dt,
            "signal":           signal,
            "signal_state":     _signal_state(disc_dt),
            "score":            score,
            "gates":            gates,
            "provenance": {
                "source_filing":       str(row.get("trade_url", "")),
                "sector":              sector,
                "sector_multiplier":   mult,
                "cluster_size":        cluster_size,
                "cluster_politicians": cluster_pols,
                "politician_bcr":      profile["bcr"],
                "politician_avg_alpha": profile["avg_alpha"],
                "politician_win_rate": profile["win_rate"],
                "politician_trade_count": profile["trade_count"],
                "price_at_trade":      None if pd.isna(pat) else round(float(pat), 2),
                "price_at_disclosure": round(float(pid), 2),
                "price_30d_post":      round(float(p30), 2),
                "abnormal_return":     None if pd.isna(ab) else round(float(ab), 4),
                "spy_return_30d":      None if pd.isna(spy) else round(float(spy), 4),
            }
        })

    return signals


def main():
    parser = argparse.ArgumentParser(description="Phase-gated signal scorer with provenance")
    parser.add_argument("--csv", default=str(DATA / "enriched_trades.csv"))
    parser.add_argument("--out", default=str(DATA / "signal_log.json"))
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] File not found: {csv_path}")
        return

    print(f"Scoring trades from {csv_path.name} ...")
    df = pd.read_csv(csv_path, dtype=str)
    for col in ["price_at_trade", "price_at_disclosure", "price_30d_post_disclosure",
                "spy_return_30d", "abnormal_return"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    signals = score_trades(df)

    counts = {"STRONG": 0, "WATCH": 0, "SKIP": 0}
    states = {"DRAFT": 0, "VERIFIED": 0, "N/A": 0}
    for s in signals:
        counts[s["signal"]] = counts.get(s["signal"], 0) + 1
        states[s.get("signal_state", "N/A")] = states.get(s.get("signal_state", "N/A"), 0) + 1

    total_buy = len(signals)
    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source":        str(csv_path),
        "methodology":   "phase_gate_v1 -- cluster × BCR × sector_multiplier",
        "summary": {
            "total_buy_trades_evaluated": total_buy,
            "strong": counts["STRONG"],
            "watch":  counts["WATCH"],
            "skip":   counts["SKIP"],
            "draft_signals":    states["DRAFT"],
            "verified_signals": states["VERIFIED"],
            "skip_rate_pct": round(counts["SKIP"] / total_buy * 100, 1) if total_buy else 0,
        },
        "signals": signals,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'-'*44}")
    print(f"  BUY trades evaluated : {total_buy:,}")
    print(f"  STRONG signals       : {counts['STRONG']:,}")
    print(f"  WATCH  signals       : {counts['WATCH']:,}")
    print(f"  SKIP   (gated out)   : {counts['SKIP']:,}  ({output['summary']['skip_rate_pct']}%)")
    print(f"  DRAFT  (window open) : {states['DRAFT']:,}")
    print(f"  VERIFIED (closed)    : {states['VERIFIED']:,}")
    print(f"{'-'*44}")
    print(f"  Signal log saved -> {out_path}\n")

    # Print top STRONG signals
    strong = [s for s in signals if s["signal"] == "STRONG"]
    strong.sort(key=lambda x: x["score"], reverse=True)
    if strong:
        print("  Top STRONG signals:")
        for s in strong[:10]:
            p = s["provenance"]
            ab_str = f"  alpha={p['abnormal_return']:+.2f}%" if p.get("abnormal_return") is not None else ""
            print(f"    {s['ticker']:<6} {s['politician']:<25} score={s['score']:.2f}  "
                  f"cluster={p['cluster_size']}  bcr={p['politician_bcr']:.2f}{ab_str}  [{s['signal_state']}]")
        print()


if __name__ == "__main__":
    main()

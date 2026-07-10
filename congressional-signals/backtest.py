"""
backtest.py -- Event-study backtest of the congressional cluster signal.

Strategy: at each qualifying BUY disclosure, "enter" and hold 30 days.
Return = pct_change_post_disclosure; alpha = abnormal_return (vs SPY, matched window).

Key design choice (no look-ahead / no circularity):
  Signal tiers are assigned ONLY from information known at entry --
  cluster_size x max buy-conviction-ratio (BCR). We do NOT use the realized
  return to define the tier. Then we measure forward return per tier. If
  STRONG > WATCH > SKIP monotonically, the entry-time signal predicts returns.

Compares tiers against two baselines:
  - "copy everything": every priced BUY (the naive strategy)
  - SPY: the market over the same windows

Outputs:
  reports/backtest_report.md   (human)
  data/verified/backtest.json  (agent/audit)

Usage:  python backtest.py
"""

import json
from datetime import timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"
VERIFIED = DATA / "verified"
RPTS = ROOT / "reports"; RPTS.mkdir(exist_ok=True)

CSV = (VERIFIED / "enriched_trades.csv") if (VERIFIED / "enriched_trades.csv").exists() else (DATA / "enriched_trades.csv")

WINDOW_DAYS = 30
STRONG_MIN = 2.0   # signal_score >= 2.0  -> STRONG   (known at entry)
WATCH_MIN  = 1.0   # 1.0 <= score < 2.0  -> WATCH


def valid(t: str) -> bool:
    t = str(t).strip()
    return bool(t) and t.replace("/", "").replace("-", "").isalpha() and 1 <= len(t) <= 6


def load() -> pd.DataFrame:
    df = pd.read_csv(CSV, dtype=str).fillna("")
    for c in ["pct_change_post_disclosure", "spy_return_30d", "abnormal_return"]:
        df[c] = pd.to_numeric(df.get(c, ""), errors="coerce")
    df["disc_dt"] = pd.to_datetime(df["disclosure_date"], errors="coerce")
    df["ttype"] = df["trade_type"].str.upper()
    df["tkr"] = df["ticker"].str.upper()
    return df


def politician_bcr(df: pd.DataFrame) -> dict[str, float]:
    """BCR per politician = buys / (buys + sells) across the whole dataset."""
    bcr = {}
    for pol, g in df.groupby("politician"):
        b = (g["ttype"] == "BUY").sum()
        s = (g["ttype"] == "SELL").sum()
        bcr[pol] = round(b / (b + s), 3) if (b + s) else 0.5
    return bcr


def tag_signal(df: pd.DataFrame, bcr: dict[str, float]) -> pd.DataFrame:
    """For each priced BUY, compute cluster_size + max BCR within a 30-day
    window, and the entry-time signal_score. Tier from score ONLY."""
    buys = df[(df["ttype"] == "BUY") & df["tkr"].apply(valid) & df["abnormal_return"].notna()].copy()
    buys = buys.dropna(subset=["disc_dt"])

    sizes, scores = [], []
    for _, row in buys.iterrows():
        same = buys[buys["tkr"] == row["tkr"]]
        lo, hi = row["disc_dt"] - timedelta(days=WINDOW_DAYS), row["disc_dt"] + timedelta(days=WINDOW_DAYS)
        window = same[(same["disc_dt"] >= lo) & (same["disc_dt"] <= hi)]
        pols = window["politician"].unique().tolist()
        size = len(pols)
        max_bcr = max((bcr.get(p, 0.5) for p in pols), default=0.5)
        sizes.append(size)
        scores.append(round(size * max_bcr, 3))

    buys["cluster_size"] = sizes
    buys["signal_score"] = scores

    def tier(r):
        if r["cluster_size"] < 2:
            return "SOLO"                       # not a cluster at all
        if r["signal_score"] >= STRONG_MIN:
            return "STRONG"
        if r["signal_score"] >= WATCH_MIN:
            return "WATCH"
        return "SKIP"

    buys["tier"] = buys.apply(tier, axis=1)
    return buys


def summarize(sub: pd.DataFrame) -> dict:
    if len(sub) == 0:
        return {"n": 0}
    return {
        "n": int(len(sub)),
        "avg_return": round(float(sub["pct_change_post_disclosure"].mean()), 2),
        "avg_spy": round(float(sub["spy_return_30d"].mean()), 2),
        "avg_alpha": round(float(sub["abnormal_return"].mean()), 2),
        "win_rate": round(float((sub["abnormal_return"] > 0).mean() * 100), 1),
        "median_alpha": round(float(sub["abnormal_return"].median()), 2),
    }


def equity_curve(sub: pd.DataFrame) -> dict:
    """Equal-weight $10k across the tier's signals, sequenced by disclosure date.
    Each position returns its realized 30-day % move; report final vs SPY."""
    if len(sub) == 0:
        return {}
    s = sub.sort_values("disc_dt")
    strat = float((1 + s["pct_change_post_disclosure"] / 100).mean())    # avg gross multiple
    spy = float((1 + s["spy_return_30d"] / 100).mean())
    return {
        "start": 10000,
        "strategy_end": round(10000 * strat, 0),
        "spy_end": round(10000 * spy, 0),
    }


def main():
    df = load()
    bcr = politician_bcr(df)
    buys = tag_signal(df, bcr)

    print(f"Backtest source: {CSV.name}")
    print(f"Priced BUY events: {len(buys)}\n")

    tiers = ["STRONG", "WATCH", "SKIP", "SOLO"]
    rows = {t: summarize(buys[buys["tier"] == t]) for t in tiers}
    rows["ALL BUYS (copy everything)"] = summarize(buys)

    # Print table
    hdr = f"{'Tier':<28}{'n':>6}{'Return':>9}{'SPY':>8}{'Alpha':>9}{'Win%':>7}"
    print(hdr); print("-" * len(hdr))
    for name in ["STRONG", "WATCH", "SKIP", "SOLO", "ALL BUYS (copy everything)"]:
        r = rows[name]
        if r.get("n", 0) == 0:
            print(f"{name:<28}{0:>6}     n/a"); continue
        print(f"{name:<28}{r['n']:>6}{r['avg_return']:>+8.2f}%{r['avg_spy']:>+7.2f}%{r['avg_alpha']:>+8.2f}%{r['win_rate']:>6.1f}%")

    strong_curve = equity_curve(buys[buys["tier"] == "STRONG"])
    print()
    if strong_curve:
        print(f"$10,000 equal-weighted across STRONG signals:")
        print(f"  strategy -> ${strong_curve['strategy_end']:,.0f}   |   same money in SPY -> ${strong_curve['spy_end']:,.0f}")

    # Monotonicity check (the real result)
    seq = [rows[t]["avg_alpha"] for t in ["STRONG", "WATCH", "SKIP"] if rows[t].get("n", 0) > 0]
    monotone = all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1)) if len(seq) > 1 else None
    print(f"\nSTRONG >= WATCH >= SKIP alpha ordering holds: {monotone}")

    # Artifacts
    out = {
        "source": CSV.name,
        "window_days": WINDOW_DAYS,
        "tier_thresholds": {"STRONG": STRONG_MIN, "WATCH": WATCH_MIN},
        "note": "Tiers assigned from entry-time signal_score (cluster_size x max BCR) only; no look-ahead.",
        "results": rows,
        "strong_equity_10k": strong_curve,
        "alpha_monotone": monotone,
    }
    (VERIFIED).mkdir(parents=True, exist_ok=True)
    with open(VERIFIED / "backtest.json", "w") as f:
        json.dump(out, f, indent=2, default=str)

    # Markdown report
    lines = [
        "# Backtest — Congressional Cluster Signal",
        "",
        f"**Source:** `{CSV.name}` · **Hold:** 30 days from disclosure · "
        f"**Entry-time tiering:** cluster_size × max BCR (no look-ahead)",
        "",
        "Strategy: enter each qualifying BUY at its disclosure date, hold 30 days. "
        "Alpha = return minus SPY over the identical window.",
        "",
        "| Tier | n | Avg Return | SPY | **Alpha** | Win% |",
        "|------|---|-----------|-----|-----------|------|",
    ]
    for name in ["STRONG", "WATCH", "SKIP", "SOLO", "ALL BUYS (copy everything)"]:
        r = rows[name]
        if r.get("n", 0) == 0:
            lines.append(f"| {name} | 0 | — | — | — | — |"); continue
        lines.append(f"| {name} | {r['n']} | {r['avg_return']:+.2f}% | {r['avg_spy']:+.2f}% | "
                     f"**{r['avg_alpha']:+.2f}%** | {r['win_rate']:.1f}% |")
    lines += [""]
    if strong_curve:
        lines += [
            f"**$10,000 equal-weighted across STRONG signals** → "
            f"**${strong_curve['strategy_end']:,.0f}** vs SPY **${strong_curve['spy_end']:,.0f}**.",
            "",
        ]
    lines += [
        f"**Alpha ordering STRONG ≥ WATCH ≥ SKIP holds:** {monotone}",
        "",
        "### Caveats",
        "- Small n on STRONG; in-sample; equal-weight, no transaction costs or slippage.",
        "- Amount ranges (not exact sizes) — positions unweighted by capital deployed.",
        "- Correlation, not proven causation. Research/education only — not financial advice.",
    ]
    with open(RPTS / "backtest_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n  Report -> {RPTS / 'backtest_report.md'}")
    print(f"  JSON   -> {VERIFIED / 'backtest.json'}")


if __name__ == "__main__":
    main()

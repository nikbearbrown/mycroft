# =============================================================================
# Week 6 deliverable (part 2 of 2) — the signal-validation backtest.
#
# Executes EXACTLY the design fixed in docs/backtest_preregistration.md (read it
# first). Nothing here is chosen after seeing results:
#   - buzz variable  bz(t) = within-entity z-scored storyCount  (point-in-time safe)
#   - price variable r(t)  = within-entity z-scored weekly log return
#                            ln(P(t)/P(t-1)), P = last close at/before run_date
#   - forward tests  corr(bz(t), r(t+n)) for n in {0,1,2,4}     (buzz leads price)
#   - reverse tests  corr(r(t),  bz(t+n)) for n in {1,2,4}      (price leads buzz)
#   - 7-test family, Benjamini-Hochberg FDR at q=0.05
#   - pooled panel = primary; per-entity = descriptive only
#
# Run: python run_backtest.py
# Reads backfill_output/backfill_v1.json + backfill_output/prices_v1.json and
# watchlist.json. Writes backfill_output/backtest_results.json and prints a
# human summary. No network, no DB — pure computation over verified local data.
# =============================================================================

import json
from bisect import bisect_right
from pathlib import Path

import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "backfill_output"
BACKFILL_PATH = OUT_DIR / "backfill_v1.json"
PRICES_PATH = OUT_DIR / "prices_v1.json"
WATCHLIST_PATH = BASE_DIR / "watchlist.json"
RESULTS_PATH = OUT_DIR / "backtest_results.json"

FDR_Q = 0.05
# Pre-registered lag family (see §4 of the pre-registration). direction "fwd"
# = buzz(t) vs price(t+n); "rev" = price(t) vs buzz(t+n).
LAGS = [
    ("fwd", 0), ("fwd", 1), ("fwd", 2), ("fwd", 4),
    ("rev", 1), ("rev", 2), ("rev", 4),
]


def zscore(arr):
    """Within-entity z-score, ignoring NaNs. Returns NaNs unchanged if std==0."""
    a = np.asarray(arr, dtype=float)
    mean = np.nanmean(a)
    std = np.nanstd(a)
    if not np.isfinite(std) or std == 0:
        return np.full_like(a, np.nan)
    return (a - mean) / std


def close_at_or_before(sorted_dates, closes, run_date):
    """Last close on/before run_date (handles weekends + the 2026-07-03 holiday)."""
    i = bisect_right(sorted_dates, run_date) - 1
    return closes[sorted_dates[i]] if i >= 0 else np.nan


def build_panel(metric):
    """Return {entity: {'bz': z-scored buzz array, 'r': z-scored return array}}
    aligned to the 13 run_dates, for every entity that has a ticker+prices."""
    backfill = json.loads(BACKFILL_PATH.read_text(encoding="utf-8"))
    prices = json.loads(PRICES_PATH.read_text(encoding="utf-8"))
    watchlist = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
    ticker_of = {e["entity"]: e.get("ticker") for e in watchlist}

    run_dates = [w["run_date"] for w in backfill]  # already chronological
    n = len(run_dates)

    # Pre-sort each ticker's daily dates once for the at-or-before lookup.
    sorted_dates = {t: sorted(series) for t, series in prices.items()}

    panel = {}
    for entity, ticker in ticker_of.items():
        if not ticker or ticker not in prices:
            continue  # private comparable or no price — excluded from price tests

        buzz = np.array(
            [backfill[i]["raw_metrics"].get(entity, {}).get(metric, np.nan) for i in range(n)],
            dtype=float,
        )
        px = np.array(
            [close_at_or_before(sorted_dates[ticker], prices[ticker], run_dates[i]) for i in range(n)],
            dtype=float,
        )
        # Weekly log return; r[0] undefined (no prior week).
        ret = np.full(n, np.nan)
        ret[1:] = np.log(px[1:] / px[:-1])

        panel[entity] = {
            "ticker": ticker,
            "bz": zscore(buzz),
            "r": zscore(ret),
            "raw_buzz": buzz,
            "raw_price": px,
        }
    return panel, run_dates


def pooled_pairs(panel, direction, n):
    """Stack (x, y) across all entities for one lag test; drop NaN pairs."""
    xs, ys = [], []
    for e in panel.values():
        bz, r = e["bz"], e["r"]
        length = len(bz)
        for t in range(length):
            if t + n >= length:
                continue
            if direction == "fwd":       # buzz(t) -> price(t+n)
                x, y = bz[t], r[t + n]
            else:                        # price(t) -> buzz(t+n)
                x, y = r[t], bz[t + n]
            if np.isfinite(x) and np.isfinite(y):
                xs.append(x)
                ys.append(y)
    return np.array(xs), np.array(ys)


def per_entity_pairs(e, direction, n):
    bz, r = e["bz"], e["r"]
    length = len(bz)
    xs, ys = [], []
    for t in range(length):
        if t + n >= length:
            continue
        x, y = (bz[t], r[t + n]) if direction == "fwd" else (r[t], bz[t + n])
        if np.isfinite(x) and np.isfinite(y):
            xs.append(x)
            ys.append(y)
    return np.array(xs), np.array(ys)


def run(metric, apply_fdr):
    panel, run_dates = build_panel(metric)

    # ---- Primary: pooled panel ----
    pooled = []
    pvals = []
    for direction, n in LAGS:
        x, y = pooled_pairs(panel, direction, n)
        if len(x) >= 3:
            r, p = stats.pearsonr(x, y)
        else:
            r, p = np.nan, np.nan
        pooled.append({"direction": direction, "lag_weeks": n, "n_obs": int(len(x)),
                       "pearson_r": None if np.isnan(r) else round(float(r), 4),
                       "p_value": None if np.isnan(p) else round(float(p), 4)})
        pvals.append(p)

    if apply_fdr:
        mask = np.array([p is not None for p in [row["p_value"] for row in pooled]])
        valid_p = np.array([row["p_value"] for row in pooled if row["p_value"] is not None])
        reject, q_adj, _, _ = multipletests(valid_p, alpha=FDR_Q, method="fdr_bh")
        j = 0
        for row in pooled:
            if row["p_value"] is not None:
                row["fdr_q_value"] = round(float(q_adj[j]), 4)
                row["survives_fdr"] = bool(reject[j])
                j += 1
            else:
                row["fdr_q_value"] = None
                row["survives_fdr"] = False

    # ---- Exploratory: per-entity ----
    per_entity = {}
    for entity, e in panel.items():
        rows = []
        for direction, n in LAGS:
            x, y = per_entity_pairs(e, direction, n)
            if len(x) >= 3:
                r, p = stats.pearsonr(x, y)
                rows.append({"direction": direction, "lag_weeks": n, "n_obs": int(len(x)),
                             "pearson_r": round(float(r), 4), "p_value": round(float(p), 4)})
            else:
                rows.append({"direction": direction, "lag_weeks": n, "n_obs": int(len(x)),
                             "pearson_r": None, "p_value": None})
        per_entity[entity] = {"ticker": e["ticker"], "tests": rows}

    return {"metric": metric, "run_dates": run_dates,
            "entities_in_panel": sorted(panel), "pooled": pooled, "per_entity": per_entity}


def fmt_row(row):
    tag = ""
    if "survives_fdr" in row:
        tag = "  <== survives FDR" if row["survives_fdr"] else ""
    q = f" q={row['fdr_q_value']}" if row.get("fdr_q_value") is not None else ""
    return (f"  {row['direction']:>3} n={row['lag_weeks']}  "
            f"r={str(row['pearson_r']):>8}  p={str(row['p_value']):>7}{q}  "
            f"(N={row['n_obs']}){tag}")


def main():
    primary = run("storyCount", apply_fdr=True)
    secondary = run("totalPoints", apply_fdr=False)  # flagged: look-ahead risk

    print("=" * 68)
    print("PRIMARY — buzz metric: storyCount (point-in-time safe)")
    print(f"Pooled panel over {len(primary['entities_in_panel'])} public-ticker entities: "
          f"{', '.join(primary['entities_in_panel'])}")
    print("-" * 68)
    for row in primary["pooled"]:
        print(fmt_row(row))
    print("-" * 68)
    survivors = [r for r in primary["pooled"] if r.get("survives_fdr")]
    print(f"Tests surviving BH-FDR (q<{FDR_Q}): {len(survivors)}")
    print()
    print("SECONDARY — totalPoints (NOT point-in-time safe; descriptive only, no FDR)")
    for row in secondary["pooled"]:
        print(fmt_row(row))
    print("=" * 68)

    RESULTS_PATH.write_text(json.dumps(
        {"fdr_q": FDR_Q, "primary": primary, "secondary_caveated": secondary}, indent=2),
        encoding="utf-8")
    print(f"Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()

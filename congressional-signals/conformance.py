"""
conformance.py -- Phase-gate validation for trade records (Madison pattern).

Checks every row in enriched_trades.csv against four structural gates before
it is eligible to be scored. Prints a report and writes data/conformance_report.json.

Gates
-----
1. valid_ticker       -- non-empty, 1–5 alpha chars (not a bond/option placeholder)
2. has_dates          -- both transaction_date and disclosure_date present
3. has_prices         -- price_at_disclosure and price_30d_post_disclosure populated
4. has_market_adj     -- spy_return_30d and abnormal_return populated

Usage
-----
    python conformance.py
    python conformance.py --csv data/enriched_trades.csv
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"

GATES = [
    "valid_ticker",
    "has_dates",
    "has_prices",
    "has_market_adj",
]


def _valid_ticker(row: pd.Series) -> tuple[bool, str]:
    t = str(row.get("ticker", "")).strip()
    if not t or t.lower() in ("nan", "none", ""):
        return False, "blank ticker"
    if not t.replace("/", "").replace("-", "").isalpha():
        return False, f"non-alpha ticker '{t}'"
    if len(t) > 6:
        return False, f"ticker too long '{t}'"
    return True, t


def _has_dates(row: pd.Series) -> tuple[bool, str]:
    td = str(row.get("transaction_date", "")).strip()
    dd = str(row.get("disclosure_date", "")).strip()
    if not td or td in ("nan", ""):
        return False, "missing transaction_date"
    if not dd or dd in ("nan", ""):
        return False, "missing disclosure_date"
    return True, f"tx={td} disc={dd}"


def _has_prices(row: pd.Series) -> tuple[bool, str]:
    pid = row.get("price_at_disclosure")
    p30 = row.get("price_30d_post_disclosure")
    if pd.isna(pid) or pd.isna(p30):
        missing = []
        if pd.isna(pid):
            missing.append("price_at_disclosure")
        if pd.isna(p30):
            missing.append("price_30d_post_disclosure")
        return False, f"missing {', '.join(missing)}"
    return True, f"disc={float(pid):.2f} post={float(p30):.2f}"


def _has_market_adj(row: pd.Series) -> tuple[bool, str]:
    spy = row.get("spy_return_30d")
    ab  = row.get("abnormal_return")
    if pd.isna(spy) or pd.isna(ab):
        missing = []
        if pd.isna(spy):
            missing.append("spy_return_30d")
        if pd.isna(ab):
            missing.append("abnormal_return")
        return False, f"missing {', '.join(missing)}"
    return True, f"spy={float(spy):.2f}% alpha={float(ab):.2f}%"


GATE_FNS = {
    "valid_ticker":   _valid_ticker,
    "has_dates":      _has_dates,
    "has_prices":     _has_prices,
    "has_market_adj": _has_market_adj,
}


def run_conformance(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path, dtype=str)

    for col in ["price_at_disclosure", "price_30d_post_disclosure",
                "spy_return_30d", "abnormal_return",
                "price_at_trade", "pct_change_post_disclosure"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    total = len(df)
    gate_fails = {g: 0 for g in GATES}
    rows_passed_all = 0
    first_fail_gate = {g: 0 for g in GATES}  # rows that fail here first

    records = []
    for _, row in df.iterrows():
        gate_results = {}
        first_fail = None
        for gate in GATES:
            passed, evidence = GATE_FNS[gate](row)
            gate_results[gate] = {"passed": passed, "evidence": evidence}
            if not passed:
                gate_fails[gate] += 1
                if first_fail is None:
                    first_fail = gate
                    first_fail_gate[gate] += 1

        all_passed = first_fail is None
        if all_passed:
            rows_passed_all += 1

        records.append({
            "politician":        row.get("politician", ""),
            "ticker":            row.get("ticker", ""),
            "trade_type":        row.get("trade_type", ""),
            "disclosure_date":   row.get("disclosure_date", ""),
            "passed_all_gates":  all_passed,
            "first_fail_gate":   first_fail,
            "gates":             gate_results,
        })

    report = {
        "generated_at":     datetime.utcnow().isoformat() + "Z",
        "source":           str(csv_path),
        "total_rows":       total,
        "passed_all_gates": rows_passed_all,
        "skip_rate_pct":    round((total - rows_passed_all) / total * 100, 1),
        "gate_fail_counts": gate_fails,
        "first_fail_at_gate": first_fail_gate,
        "records":          records,
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Conformance checker for trade records")
    parser.add_argument("--csv", default=str(DATA / "enriched_trades.csv"))
    parser.add_argument("--out", default=str(DATA / "conformance_report.json"))
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] File not found: {csv_path}")
        return

    print(f"Running conformance on {csv_path.name} ...")
    report = run_conformance(csv_path)

    total = report["total_rows"]
    passed = report["passed_all_gates"]
    print(f"\n{'='*44}")
    print(f"  Total rows        : {total:,}")
    print(f"  Passed all gates  : {passed:,}  ({100*passed//total}%)")
    print(f"  Skip rate         : {report['skip_rate_pct']}%")
    print(f"{'='*44}")
    print("  Gate-level fail counts:")
    for gate, count in report["gate_fail_counts"].items():
        print(f"    {gate:<22} {count:>5,} rows failed")
    print(f"{'='*44}\n")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Full report saved -> {out_path}")


if __name__ == "__main__":
    main()

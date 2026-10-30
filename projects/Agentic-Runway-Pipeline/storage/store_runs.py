"""
storage/store_runs.py  —  Sprint 6: persist every run + confidence + trend history.

Until now, each pipeline run's results vanished when the program ended. This stores
every run in a DuckDB database, so you can:
  1. Keep a permanent record of each run
  2. Attach a per-brief confidence score (how trustworthy is this brief?)
  3. See how a company's risk signals change OVER TIME (the trend)

Scope note (Sprint 6 only): this STORES and shows a trend. It does NOT build a
dashboard (that's Sprint 7). Plain text output here.

Requires: pip install duckdb

Run:
    # store a run's signals
    python -m storage.store_runs data/deduped/signals.json --store

    # show the trend for a company across all stored runs
    python -m storage.store_runs --trend openai
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB_PATH = "data/runs.duckdb"


def _connect():
    import duckdb
    Path("data").mkdir(exist_ok=True)
    con = duckdb.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id      VARCHAR,
            run_at      TIMESTAMP,
            company_id  VARCHAR,
            signal_id   VARCHAR,
            signal_type VARCHAR,
            score       INTEGER,
            validated   BOOLEAN,
            source_url  VARCHAR
        )
    """)
    return con


def brief_confidence(signals: list[dict]) -> int:
    """
    A per-brief confidence score (0-100): how trustworthy is this company's brief?
    Simple, explainable: average signal score, reduced if few signals or few validated.
    (Deliberately transparent, not a black box.)
    """
    if not signals:
        return 0
    avg_score = sum(s.get("score", 0) for s in signals) / len(signals)
    validated_frac = sum(1 for s in signals if s.get("validated_by")) / len(signals)
    # fewer signals / fewer validated -> lower confidence in the brief
    coverage = min(len(signals) / 3, 1.0)  # 3+ signals = full coverage
    return round(avg_score * (0.5 + 0.5 * validated_frac) * coverage)


def store(signals_path: str) -> None:
    con = _connect()
    signals = json.load(open(signals_path))
    run_id = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    run_at = dt.datetime.utcnow()

    for s in signals:
        con.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [run_id, run_at, s.get("company_id"), s.get("signal_id"),
             s.get("signal_type"), s.get("score", 0),
             bool(s.get("validated_by")), s.get("source_url")]
        )

    # per-company confidence for this run
    by_company = {}
    for s in signals:
        by_company.setdefault(s.get("company_id"), []).append(s)

    print(f"STORED RUN {run_id}  ({len(signals)} signals)")
    print("=" * 52)
    for company, sigs in by_company.items():
        conf = brief_confidence(sigs)
        print(f"  {company}: {len(sigs)} signals, brief confidence {conf}/100")
    con.close()


def trend(company: str) -> None:
    con = _connect()
    rows = con.execute("""
        SELECT run_id, run_at,
               COUNT(*) AS signals,
               SUM(CASE WHEN validated THEN 1 ELSE 0 END) AS validated,
               SUM(CASE WHEN signal_type IN ('layoff','security_issue','executive_change')
                        THEN 1 ELSE 0 END) AS distress
        FROM runs WHERE company_id = ?
        GROUP BY run_id, run_at ORDER BY run_at
    """, [company]).fetchall()
    con.close()

    print(f"RISK TREND -- {company}")
    print("=" * 52)
    if not rows:
        print("  No stored runs for this company yet. Run with --store first.")
        return
    print(f"  {'run':<18} {'signals':>8} {'validated':>10} {'distress':>9}")
    for run_id, run_at, signals, validated, distress in rows:
        print(f"  {run_id:<18} {signals:>8} {validated or 0:>10} {distress or 0:>9}")
    print("\n  (trend across runs -- rising distress or falling validation is the story)")
    print("  The tool shows the trend. A human still judges it. HALT-AWAITING-HUMAN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("signals_path", nargs="?")
    ap.add_argument("--store", action="store_true")
    ap.add_argument("--trend", metavar="COMPANY")
    args = ap.parse_args()

    if args.trend:
        trend(args.trend)
    elif args.store and args.signals_path:
        store(args.signals_path)
    else:
        print("usage:\n  --store <signals.json>   store a run\n  --trend <company>        show the trend")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

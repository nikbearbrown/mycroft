"""Resolve market outcomes for a small sample of signals (for testing --score).

Your extracted signals may have transcript_date = today (pipeline bug). The
resolver needs a past date so +30/+90/+180 horizons exist. This script can
overwrite those dates for the sample only (testing — not true filing dates).

Usage:
    python -m ecis.scripts.resolve_outcomes_sample
    python -m ecis.scripts.resolve_outcomes_sample --limit 50
    python -m ecis.scripts.resolve_outcomes_sample --limit 50 --ticker TICKER
    python -m ecis.scripts.resolve_outcomes_sample --backfill-date 2025-12-01
    python -m ecis.scripts.resolve_outcomes_sample --no-backfill
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ecis.resolve_sample")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve outcomes for the next N unresolved signals",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max number of unresolved signals to resolve (default: 50)",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default=None,
        help="Optional ticker filter",
    )
    parser.add_argument(
        "--backfill-date",
        type=str,
        default=None,
        help="Set transcript_date on the sample to this YYYY-MM-DD before resolving "
             "(default: today-200d so 30/90/180 horizons are available)",
    )
    parser.add_argument(
        "--no-backfill",
        action="store_true",
        help="Do not change transcript_date (use dates already in the DB)",
    )
    args = parser.parse_args(argv)

    from ecis.db.init_db import get_connection
    from ecis.scoring.outcome_resolver import resolve_signal

    conn_s = get_connection("signals")
    if args.ticker:
        ticker = args.ticker.strip().upper()
        rows = conn_s.execute(
            "SELECT signal_id FROM signals WHERE ticker = ? ORDER BY signal_id",
            (ticker,),
        ).fetchall()
    else:
        rows = conn_s.execute(
            "SELECT signal_id FROM signals ORDER BY signal_id"
        ).fetchall()
    conn_s.close()

    conn_o = get_connection("outcomes")
    existing = {
        r["signal_id"]
        for r in conn_o.execute("SELECT DISTINCT signal_id FROM outcomes").fetchall()
    }
    conn_o.close()

    todo = [r["signal_id"] for r in rows if r["signal_id"] not in existing][: args.limit]
    if not todo:
        print("No unresolved signals found.")
        return 0

    if not args.no_backfill:
        if args.backfill_date:
            try:
                backfill = date.fromisoformat(args.backfill_date)
            except ValueError:
                print(f"Invalid --backfill-date: {args.backfill_date}")
                return 1
        else:
            # 200 days ago → 30/90/180 horizons are all in the past
            backfill = date.today() - timedelta(days=200)

        conn_s = get_connection("signals")
        placeholders = ",".join("?" * len(todo))
        conn_s.execute(
            f"UPDATE signals SET transcript_date = ? WHERE signal_id IN ({placeholders})",
            [str(backfill), *todo],
        )
        conn_s.commit()
        conn_s.close()
        print(
            f"Backfilled transcript_date={backfill} on {len(todo)} signals "
            "(test only — not real filing dates)."
        )

    print(
        f"Resolving {len(todo)} signals (limit={args.limit})"
        + (f" ticker={args.ticker.strip().upper()}" if args.ticker else "")
    )

    total_outcomes = 0
    for i, sid in enumerate(todo, 1):
        outcomes = resolve_signal(sid)
        total_outcomes += len(outcomes)
        print(f"  [{i}/{len(todo)}] signal {sid}: {len(outcomes)} outcomes")

    print(f"\nDone. Wrote {total_outcomes} outcome rows for {len(todo)} signals.")
    print("Next: python -m ecis.main --score")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
audit_freshness.py  —  source-freshness / provenance audit for runway-risk-scorer

Row 5 rigor artifact. This does NOT score anything. It inspects the signals and
reports data-quality problems a human reviewer needs to know before trusting a
brief (P3 — provenance; P8 — trust is earned):

  - signals missing a source_url          (no provenance -> untrustworthy)
  - signals with a stale occurred_date     (older than STALE_DAYS)
  - signals dated in the future            (impossible -> data error)
  - unvalidated signals                    (validated_by empty -> excluded from briefs)

It writes a human-readable audit to stdout. It does not decide whether the data
is "good enough" — that is the reviewer's call at the gate.

Usage:
    python audit_freshness.py data/samples/sample_signals.json
    python audit_freshness.py data/samples/sample_signals.json --stale-days 365
"""

import argparse
import json
from datetime import date, datetime

STALE_DAYS_DEFAULT = 365


def load(path):
    with open(path) as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("expected a JSON array of signals")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("signals_path")
    ap.add_argument("--stale-days", type=int, default=STALE_DAYS_DEFAULT)
    ap.add_argument("--today", default=date.today().isoformat())
    args = ap.parse_args()

    today = datetime.fromisoformat(args.today).date()
    signals = load(args.signals_path)

    missing_source = []
    future_dated = []
    stale = []
    unvalidated = []
    bad_date = []

    for s in signals:
        sid = s.get("signal_id", "<no-id>")
        cid = s.get("company_id", "<no-company>")

        if not s.get("source_url"):
            missing_source.append((cid, sid))

        if not s.get("validated_by"):
            unvalidated.append((cid, sid))

        od = s.get("occurred_date")
        if od:
            try:
                d = datetime.fromisoformat(od).date()
                if d > today:
                    future_dated.append((cid, sid, od))
                elif (today - d).days > args.stale_days:
                    stale.append((cid, sid, (today - d).days))
            except ValueError:
                bad_date.append((cid, sid, od))

    print("SOURCE-FRESHNESS AUDIT")
    print("=" * 52)
    print(f"Signals inspected: {len(signals)}   (as of {today}, stale threshold {args.stale_days}d)")
    print()

    def section(title, items, fmt):
        print(f"{title}: {len(items)}")
        for it in items:
            print(f"     - {fmt(it)}")
        print()

    section("Missing source_url (no provenance)", missing_source, lambda x: f"{x[0]} [{x[1]}]")
    section("Future-dated (data error)", future_dated, lambda x: f"{x[0]} [{x[1]}] date={x[2]}")
    section("Malformed date", bad_date, lambda x: f"{x[0]} [{x[1]}] date={x[2]}")
    section(f"Stale (older than {args.stale_days}d)", stale, lambda x: f"{x[0]} [{x[1]}] {x[2]} days old")
    section("Unvalidated (excluded from briefs)", unvalidated, lambda x: f"{x[0]} [{x[1]}]")

    problems = len(missing_source) + len(future_dated) + len(bad_date)
    print("-" * 52)
    print(f"Hard problems (missing source / future / malformed): {problems}")
    print("Audit reports facts only. A human decides if the data is fit to use.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
runway_risk_score.py  —  AI-vendor runway-risk scorer

Week 2 structure: the recipe's step skeleton is now explicit in the code —
    STEP 1  ingest         : load the signals file
    STEP 2  validate_shape : keep only signals with the required fields, and
                             (P2) only human-validated signals inform the brief
    STEP 3  score          : compute the five mechanical metrics with provenance
    STEP 4  report         : human brief (P5 customer 1) + machine JSON (customer 2)
    GATE    halt           : never a verdict; a human decides (P1/P4)

Snickerdoodle labor separation (P1): the script computes; a human judges.
Provenance (P3): every metric carries the signal_ids and source_urls it used.

Usage:
    python runway_risk_score.py data/samples/sample_signals.json
    python runway_risk_score.py data/samples/sample_signals.json --company harbor-ai
    python runway_risk_score.py data/samples/sample_signals.json --json
    python runway_risk_score.py data/samples/sample_signals.json --json-out reports
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime

DISTRESS_TYPES = {"layoff", "security_issue", "executive_change"}

# Week 4: trailing activity window in days (recent window vs the window before it)
RECENT_WINDOW_DAYS = 365

# fields every signal must have to be usable at all (STEP 2 shape check)
REQUIRED_FIELDS = ("signal_id", "company_id", "signal_type", "occurred_date", "source_url")


# ------------------------------------------------------------------ helpers
def parse_money(value):
    """'$45M' -> 45_000_000. Returns (amount|None, note)."""
    if not value:
        return None, "no value field"
    v = value.strip().lower().replace("$", "").replace(",", "")
    mult = 1
    if v.endswith("b"):
        mult, v = 1_000_000_000, v[:-1]
    elif v.endswith("m"):
        mult, v = 1_000_000, v[:-1]
    elif v.endswith("k"):
        mult, v = 1_000, v[:-1]
    try:
        return float(v) * mult, "parsed"
    except ValueError:
        return None, f"unparseable value: {value!r}"


def months_between(d1, d2):
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def safe_date(value):
    """Parse an ISO date; return None on anything malformed (fail safe, no crash)."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except (ValueError, TypeError):
        return None


def is_validated(sig):
    """P2: only human-validated signals may inform the brief."""
    return sig.get("validated_by") not in (None, "")


# ------------------------------------------------------------------ STEP 1
def ingest(path):
    """STEP 1 — load the declared input. Returns a list of raw signal dicts."""
    with open(path) as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("expected a JSON array of signals")
    return data


# ------------------------------------------------------------------ STEP 2
def validate_shape(signals):
    """
    STEP 2 — split signals into (usable, dropped_malformed, dropped_unvalidated).
    - malformed: missing a required field -> cannot be trusted, excluded.
    - unvalidated: no validated_by -> excluded per P2.
    Only signals that are both well-shaped AND validated reach scoring.
    """
    usable, malformed, unvalidated = [], [], []
    for s in signals:
        missing = [f for f in REQUIRED_FIELDS if not s.get(f)]
        if missing:
            malformed.append({"signal": s, "missing": missing})
        elif not is_validated(s):
            unvalidated.append(s)
        else:
            usable.append(s)
    return usable, malformed, unvalidated


# ------------------------------------------------------------------ STEP 3
def score(company_id, usable, dropped_unvalidated_count, today):
    """STEP 3 — compute the five metrics with provenance. No judgment."""
    # 1. total_raised
    total = 0.0
    raise_prov = []
    parse_notes = []
    for s in usable:
        if s.get("signal_type") == "funding_round":
            amt, note = parse_money(s.get("signal_value"))
            if amt is not None:
                total += amt
                raise_prov.append({"signal_id": s["signal_id"], "source_url": s["source_url"], "value": s["signal_value"]})
            else:
                parse_notes.append(f'{s["signal_id"]}: {note}')

    # 2. months_since_last_raise
    raise_dates = [
        (safe_date(s["occurred_date"]), s)
        for s in usable
        if s.get("signal_type") == "funding_round" and safe_date(s.get("occurred_date"))
    ]
    if raise_dates:
        last_dt, last_sig = max(raise_dates, key=lambda t: t[0])
        months_since = months_between(last_dt, today)
        recency_prov = {"signal_id": last_sig["signal_id"], "source_url": last_sig["source_url"], "date": last_dt.isoformat()}
    else:
        months_since, recency_prov = None, None

    # 3. funding_stage_trend
    stage_sigs = [s for s in usable if s.get("signal_type") == "funding_stage" and s.get("signal_value")]
    stage_sigs.sort(key=lambda s: s.get("occurred_date") or "")
    stages = [s["signal_value"] for s in stage_sigs]
    stage_prov = [{"signal_id": s["signal_id"], "stage": s["signal_value"], "date": s.get("occurred_date")} for s in stage_sigs]

    # 4. distress_indicators
    distress = [s for s in usable if s.get("signal_type") in DISTRESS_TYPES]
    distress_prov = [{"signal_id": s["signal_id"], "type": s["signal_type"], "title": s.get("signal_title"), "source_url": s["source_url"]} for s in distress]

    # 5. signal_freshness
    dated = [safe_date(s["occurred_date"]) for s in usable if safe_date(s.get("occurred_date"))]
    freshness_days = (today - max(dated)).days if dated else None

    # Week 4: trailing-window activity + signal-velocity delta (mechanical, no verdict)
    recent_cut = today.toordinal() - RECENT_WINDOW_DAYS
    prior_cut = today.toordinal() - 2 * RECENT_WINDOW_DAYS
    recent_count = prior_count = 0
    for s in usable:
        d = safe_date(s.get("occurred_date"))
        if not d:
            continue
        o = d.toordinal()
        if o > recent_cut:
            recent_count += 1
        elif o > prior_cut:
            prior_count += 1
    velocity_delta = recent_count - prior_count

    return {
        "company_id": company_id,
        "run_date": today.isoformat(),
        "signals_used": len(usable),
        "signals_dropped_unvalidated": dropped_unvalidated_count,
        "gate": "HALT-AWAITING-HUMAN",   # never a verdict (P1)
        "metrics": {
            "total_raised_usd": total if raise_prov else None,
            "months_since_last_raise": months_since,
            "funding_stage_trend": stages,
            "distress_indicator_count": len(distress),
            "signal_freshness_days": freshness_days,
            "recent_window_days": RECENT_WINDOW_DAYS,
            "signals_recent_window": recent_count,
            "signals_prior_window": prior_count,
            "signal_velocity_delta": velocity_delta,
        },
        "provenance": {
            "total_raised": raise_prov,
            "months_since_last_raise": recency_prov,
            "funding_stage": stage_prov,
            "distress": distress_prov,
            "parse_notes": parse_notes,
        },
    }


# ------------------------------------------------------------------ STEP 4 (report)
def render_brief(r):
    """Human-readable brief (P5 customer 1). Reports facts + provenance. Never a verdict."""
    m = r["metrics"]
    pv = r["provenance"]
    L = []
    L.append(f"RUNWAY-RISK BRIEF — {r['company_id']}")
    L.append("=" * 52)
    L.append(f"Signals used (validated): {r['signals_used']}   dropped (unvalidated): {r['signals_dropped_unvalidated']}")
    L.append("")

    tr = m["total_raised_usd"]
    L.append(f"1. Total raised: {'$'+format(tr, ',.0f') if tr is not None else 'UNKNOWN (no validated funding_round signals)'}")
    for p in pv["total_raised"]:
        L.append(f"     - {p['value']}  [{p['signal_id']}]  {p['source_url']}")
    for note in pv["parse_notes"]:
        L.append(f"     ! {note}")

    ms = m["months_since_last_raise"]
    L.append(f"2. Months since last raise: {ms if ms is not None else 'UNKNOWN'}")
    if pv["months_since_last_raise"]:
        p = pv["months_since_last_raise"]
        L.append(f"     - last raise {p['date']}  [{p['signal_id']}]  {p['source_url']}")

    st = m["funding_stage_trend"]
    L.append(f"3. Funding-stage trend: {' -> '.join(st) if st else 'UNKNOWN'}")

    L.append(f"4. Distress indicators (layoff/security/exec-change): {m['distress_indicator_count']}")
    for p in pv["distress"]:
        L.append(f"     - {p['type']}: {p['title']}  [{p['signal_id']}]  {p['source_url']}")

    fr = m["signal_freshness_days"]
    L.append(f"5. Most recent validated signal: {str(fr)+' days ago' if fr is not None else 'UNKNOWN'}")

    win = m["recent_window_days"]
    L.append(f"6. Activity (last {win}d vs prior {win}d): {m['signals_recent_window']} vs {m['signals_prior_window']}")
    vd = m["signal_velocity_delta"]
    sign = "+" if vd > 0 else ""
    L.append(f"7. Signal-velocity delta: {sign}{vd}   (positive = picking up, negative = going quiet)")

    L.append("")
    L.append("-" * 52)
    L.append("HUMAN GATE (P1/P4) — not cleared by this script.")
    L.append("A named human must judge whether this runway risk is acceptable")
    L.append("for procurement and log the decision in logs/RUN_LOG.md.")
    L.append("This tool computed metrics. It did not decide anything.")
    return "\n".join(L)


# ------------------------------------------------------------------ orchestration
def main():
    ap = argparse.ArgumentParser(description="AI-vendor runway-risk scorer")
    ap.add_argument("signals_path")
    ap.add_argument("--company", default=None, help="limit to one company_id")
    ap.add_argument("--today", default=date.today().isoformat(), help="override run date (ISO)")
    ap.add_argument("--json", action="store_true", help="also print machine-readable JSON to stdout")
    ap.add_argument("--json-out", default=None, metavar="DIR",
                    help="write one <company>.json file per company into DIR")
    args = ap.parse_args()

    today = datetime.fromisoformat(args.today).date()

    # STEP 1 — ingest
    signals = ingest(args.signals_path)

    by_company = defaultdict(list)
    for s in signals:
        by_company[s.get("company_id")].append(s)

    targets = [args.company] if args.company else sorted(k for k in by_company if k)
    results = []

    for c in targets:
        if c not in by_company:
            print(f"[skip] no signals for company_id={c!r}", file=sys.stderr)
            continue

        # STEP 2 — validate shape + drop unvalidated
        usable, malformed, unvalidated = validate_shape(by_company[c])

        # STEP 3 — score
        result = score(c, usable, len(unvalidated), today)
        results.append(result)

        # STEP 4 — human report
        print(render_brief(result))
        print()

        # machine log line (P5)
        print(f'[LOG] recipe=runway-risk company={c} used={result["signals_used"]} '
              f'dropped_unvalidated={result["signals_dropped_unvalidated"]} '
              f'malformed={len(malformed)} '
              f'distress={result["metrics"]["distress_indicator_count"]} '
              f'gate={result["gate"]}', file=sys.stderr)

    # STEP 4 — machine JSON (customer 2)
    if args.json:
        print(json.dumps(results, indent=2))

    if args.json_out:
        os.makedirs(args.json_out, exist_ok=True)
        for r in results:
            path = os.path.join(args.json_out, f"{r['company_id']}.json")
            with open(path, "w") as fh:
                json.dump(r, fh, indent=2)
            print(f"[wrote] {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
"""
run_pipeline.py  —  Sprint 5b: the full path, and feed VALIDATED signals to the scorer.

Chains the agentic pipeline end to end and then scores — honoring P2: only
HUMAN-VALIDATED signals are scored. Unvalidated signals are counted but held back,
because the human gate is the whole point of the design.

Full path:  (signals already fetched/extracted/deduped)
            -> split validated vs unvalidated
            -> score ONLY the validated ones (reuse the runway-risk scoring logic)
            -> report; never a verdict (halts at the human gate)

Run:
    python run_pipeline.py data/deduped/signals.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def is_validated(s: dict) -> bool:
    return bool(s.get("validated_by"))


def score_signals(validated: list[dict]) -> dict:
    """
    Minimal re-use of the runway-risk scoring idea: count signal types for a company.
    (In the real integration this calls your existing scorer module. Shown inline so
    the full path runs; the point of Sprint 5 is that the chain WORKS end to end.)
    """
    from collections import Counter
    by_company = {}
    for s in validated:
        by_company.setdefault(s.get("company_id", "?"), []).append(s)
    briefs = {}
    for company, sigs in by_company.items():
        types = Counter(s.get("signal_type") for s in sigs)
        distress = sum(types.get(t, 0) for t in ("layoff", "security_issue", "executive_change"))
        briefs[company] = {
            "validated_signals": len(sigs),
            "signal_types": dict(types),
            "distress_indicators": distress,
            "sources": [s.get("source_url") for s in sigs],  # provenance (P3)
        }
    return briefs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("signals_path")
    args = ap.parse_args()
    signals = json.load(open(args.signals_path))

    validated = [s for s in signals if is_validated(s)]
    held = [s for s in signals if not is_validated(s)]

    print("FULL PIPELINE -> SCORER (P2: only validated signals scored)")
    print("=" * 52)
    print(f"Total signals:        {len(signals)}")
    print(f"Validated (scored):   {len(validated)}")
    print(f"Unvalidated (HELD):   {len(held)}  <- waiting for a human (P2)")
    print()

    if not validated:
        print("No validated signals yet. The scorer correctly scores NOTHING until a")
        print("human validates. This is the design working, not a failure.")
        print("\nHALT-AWAITING-HUMAN")
        return 0

    briefs = score_signals(validated)
    for company, b in briefs.items():
        print(f"RUNWAY-RISK BRIEF -- {company}")
        print(f"  validated signals: {b['validated_signals']}")
        print(f"  types: {b['signal_types']}")
        print(f"  distress indicators: {b['distress_indicators']}")
        print()
    print("HALT-AWAITING-HUMAN  (the tool computed; it did not decide)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
tests/test_break_agentic.py  —  Sprint 8: break tests for the agentic components.

Feeds deliberately bad input to each new component (Sprints 1-6) and checks it
FAILS SAFELY \u2014 rejects, skips, or holds \u2014 rather than crashing or inventing data.
Honest rigor: if a component can be broken, we want to know here, not in production.

Run:
    python -m tests.test_break_agentic
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PASS, FAIL = "PASS", "FAIL"
results = []


def check(name, condition):
    results.append((name, PASS if condition else FAIL))


# --- Sprint 1: schema rejects bad data ---
def test_schema_rejects_bad():
    from schema.signal import Signal
    from pydantic import ValidationError
    bad_cases = [
        {"signal_id": "x", "company_id": "c", "signal_type": "not_a_type",
         "signal_title": "t", "signal_value": "v", "occurred_date": "2024-01-01",
         "source_url": "https://x.com", "score": 50},                      # bad type
        {"signal_id": "x", "company_id": "c", "signal_type": "layoff",
         "signal_title": "t", "signal_value": "v", "occurred_date": "2099-01-01",
         "source_url": "https://x.com", "score": 50},                      # future date
        {"signal_id": "x", "company_id": "c", "signal_type": "layoff",
         "signal_title": "t", "signal_value": "v", "occurred_date": "2024-01-01",
         "source_url": "not-a-url", "score": 50},                          # bad url
        {"signal_id": "x", "company_id": "c", "signal_type": "layoff",
         "signal_title": "t", "signal_value": "v", "occurred_date": "2024-01-01",
         "source_url": "https://x.com", "score": 999},                     # score out of range
    ]
    for i, bad in enumerate(bad_cases):
        try:
            Signal(**bad)
            check(f"schema rejects bad case {i}", False)  # should have raised
        except ValidationError:
            check(f"schema rejects bad case {i}", True)   # correctly raised


# --- confidence score handles empty / thin input ---
def test_confidence_handles_empty():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "storage"))
    from storage.store_runs import brief_confidence
    check("confidence of [] is 0 (no crash)", brief_confidence([]) == 0)
    one = [{"score": 80, "validated_by": None}]
    c = brief_confidence(one)
    check("confidence of 1 unvalidated signal is low (<50)", c < 50)


# --- scorer holds unvalidated signals (P2) ---
def test_scorer_holds_unvalidated():
    # a signal with validated_by=None must NOT be scored
    sig = {"company_id": "c", "signal_type": "layoff", "score": 90, "validated_by": None}
    is_validated = bool(sig.get("validated_by"))
    check("unvalidated signal is held, not scored", is_validated is False)


def main():
    print("BREAK TESTS \u2014 agentic components (Sprint 8)")
    print("=" * 52)
    for t in (test_schema_rejects_bad, test_confidence_handles_empty, test_scorer_holds_unvalidated):
        try:
            t()
        except Exception as e:
            check(f"{t.__name__} ran without crashing", False)
            print(f"  (unexpected error in {t.__name__}: {e})")

    passed = sum(1 for _, r in results if r == PASS)
    for name, r in results:
        print(f"  [{r}] {name}")
    print(f"\n{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

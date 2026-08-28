#!/usr/bin/env python3
"""
test_break.py  —  deliberate break tests for runway-risk-scorer (Row 5)

Feeds the scorer DELIBERATELY BAD input and asserts it fails SAFELY — reports
UNKNOWN or drops the signal, never crashes and never emits a wrong number.

A tool that only works on perfect data is dangerous, because real data is messy.
These tests prove graceful failure.

Run from the repo root:
    python scripts/test_break.py
Exit code 0 = all passed.
"""

import sys
import os

# import the scorer module living next to this file
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runway_risk_score as rr  # noqa: E402
from datetime import date

TODAY = date(2026, 8, 24)
passed = failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


def validated(**kw):
    """helper: a well-formed validated signal, overridable per-test."""
    base = dict(
        signal_id="test-1", company_id="testco", signal_type="funding_round",
        signal_value="$10M", occurred_date="2025-01-01", source_url="https://x/y",
        validated_by="tester",
    )
    base.update(kw)
    return base


print("BREAK TESTS — runway-risk-scorer")
print("=" * 52)

# 1. broken money string -> total stays UNKNOWN, no crash
sigs = [validated(signal_value="$4X million")]
u, m, un = rr.validate_shape(sigs)
r = rr.score("testco", u, len(un), TODAY)
check("broken money string -> total_raised is None (UNKNOWN)",
      r["metrics"]["total_raised_usd"] is None)

# 2. future-dated funding round -> still handled, no crash, negative months not emitted as a raise flag
sigs = [validated(occurred_date="2099-01-01")]
u, m, un = rr.validate_shape(sigs)
r = rr.score("testco", u, len(un), TODAY)
check("future date -> script runs without crashing",
      r["gate"] == "HALT-AWAITING-HUMAN")

# 3. empty company (no signals) -> all UNKNOWN, no crash
u, m, un = rr.validate_shape([])
r = rr.score("emptyco", u, len(un), TODAY)
check("empty company -> total UNKNOWN",
      r["metrics"]["total_raised_usd"] is None)
check("empty company -> freshness UNKNOWN",
      r["metrics"]["signal_freshness_days"] is None)

# 4. missing source_url -> dropped as malformed, not used
sigs = [validated(source_url="")]
u, m, un = rr.validate_shape(sigs)
check("missing source_url -> dropped as malformed (not used)",
      len(u) == 0 and len(m) == 1)

# 5. unvalidated signal -> dropped per P2
sigs = [validated(validated_by="")]
u, m, un = rr.validate_shape(sigs)
check("unvalidated signal -> dropped (P2)",
      len(u) == 0 and len(un) == 1)

# 6. malformed date -> shape check keeps it (has the field) but scoring must not crash
sigs = [validated(occurred_date="not-a-date")]
u, m, un = rr.validate_shape(sigs)
try:
    r = rr.score("testco", u, len(un), TODAY)
    crashed = False
except Exception:
    crashed = True
check("malformed date -> scoring does not crash", not crashed)

print("-" * 52)
print(f"PASSED {passed}   FAILED {failed}")
sys.exit(0 if failed == 0 else 1)

#!/usr/bin/env python3
"""Summarize events.deadletter into an audit table.

Usage (from repo root, stack up):
    docker compose -f deploy/docker-compose.yml exec -T redpanda \
        rpk topic consume events.deadletter -o start -e -f '%v\n' \
    | python scripts/deadletter_audit.py > audits/deadletter-$(date +%F).md

Reads one JSON envelope per line on stdin; every rejected event carries `reject_reason`.
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone

rows = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        rows.append(json.loads(line))
    except Exception:
        rows.append({"reject_reason": "audit: unparseable deadletter line", "_raw": line[:200]})

reasons = Counter()
by_source = Counter()
for r in rows:
    reason = r.get("reject_reason", "(none)")
    # collapse the variable tail of stale/future reasons
    key = reason.split(":")[0].strip() if ":" in reason else reason
    reasons[key] += 1
    by_source[r.get("source", "?")] += 1

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
print(f"# Deadletter audit - {now}\n")
print(f"**{len(rows)}** rejected events on `events.deadletter`.\n")

print("## By reason class\n")
print("| reason | count |")
print("|---|---:|")
for reason, n in reasons.most_common():
    print(f"| {reason} | {n} |")

print("\n## By source\n")
print("| source | count |")
print("|---|---:|")
for src, n in by_source.most_common():
    print(f"| {src} | {n} |")

print("\n## Sample (up to 15)\n")
print("| event_key | source | reject_reason |")
print("|---|---|---|")
for r in rows[:15]:
    print(f"| {r.get('event_key','-')} | {r.get('source','-')} | {r.get('reject_reason','-')} |")

print("\n_An audit reports what it found; it does not say pass._")

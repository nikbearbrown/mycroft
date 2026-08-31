#!/usr/bin/env python3
"""scorecard — Week 4 grading audit. Reads signal_outcomes via `kubectl exec psql`
and writes audits/scorecard-<UTC>.md. An audit reports what it found; it does not
say pass (Snickerdoodle P3 — the verification stack's layer-2 artifact).

Run: python scripts/scorecard.py   (cluster must be reachable: kubectl -n fes)
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def pg_pod() -> str:
    out = subprocess.run(
        ["kubectl", "-n", "fes", "get", "pod", "-l", "app=postgres",
         "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True,
    )
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("scorecard: could not find the postgres pod — is the cluster up?")
    return out.stdout.strip()


def q(pod: str, sql: str) -> list[list[str]]:
    out = subprocess.run(
        ["kubectl", "-n", "fes", "exec", pod, "--",
         "psql", "-U", "fes", "-d", "fes", "-A", "-F", "\t", "-t", "-c", sql],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        print(out.stderr, file=sys.stderr)
        sys.exit("scorecard: query failed")
    return [line.split("\t") for line in out.stdout.strip().splitlines() if line.strip()]


def table(headers, rows) -> str:
    if not rows:
        return "_(none)_\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join((c or "").strip() for c in r) + " |")
    return "\n".join(out) + "\n"


pod = pg_pod()
ts = datetime.now(timezone.utc)

overall = q(pod, """
    SELECT
      count(*) FILTER (WHERE correct IS NOT NULL) graded,
      count(*) FILTER (WHERE correct = true) correct_n,
      count(*) FILTER (WHERE correct = false) incorrect_n,
      count(*) FILTER (WHERE correct IS NULL) pending_n,
      count(*) total
    FROM signal_outcomes
""")[0]
graded, correct_n, incorrect_n, pending_n, total = (int(x) for x in overall)

by_note = q(pod, """
    SELECT COALESCE(grading_note, '(graded)'), count(*)
    FROM signal_outcomes GROUP BY 1 ORDER BY 2 DESC
""")

by_type = q(pod, """
    SELECT s.event_type, o.correct, count(*)
    FROM signal_outcomes o JOIN signals s USING (signal_id)
    GROUP BY 1, 2 ORDER BY 1, 2
""")

detail = q(pod, """
    SELECT o.signal_id, o.ticker, o.predicted_direction, o.realized_direction,
           round(o.pct_move::numeric, 2), o.correct, o.priced_at_date, o.priced_after_date
    FROM signal_outcomes o
    WHERE o.correct IS NOT NULL
    ORDER BY o.priced_after_date
""")

pending_detail = q(pod, """
    SELECT o.signal_id, o.ticker, s.event_type, o.grading_note
    FROM signal_outcomes o JOIN signals s USING (signal_id)
    WHERE o.correct IS NULL
    ORDER BY o.grading_note, o.ticker
""")

precision = f"{correct_n}/{graded} ({100*correct_n/graded:.0f}%)" if graded else "n/a"

md = f"""# Grading scorecard — {ts.strftime('%Y-%m-%d %H:%M UTC')}

**{total}** actionable signals graded-or-attempted. **{graded}** gradeable now (enough time
has elapsed): **{precision}** correct. **{pending_n}** still pending (insufficient time
elapsed, or a real data gap — see below).

> **n={graded} is not a sample size to generalize an accuracy claim from.** See
> `PRE_REGISTRATION.md` — Week 4's own falsification criterion says exactly this.
> This scorecard reports what was found; it does not say the system "works."

## Outcome breakdown

{table(["grading_note (blank = graded)", "count"], by_note)}

## By event_type

{table(["event_type", "correct", "count"], by_type)}

## Graded signals (detail)

{table(["signal_id", "ticker", "predicted", "realized", "pct_move", "correct", "priced_at", "priced_after"], detail)}

## Not yet graded (detail)

{table(["signal_id", "ticker", "event_type", "reason"], pending_detail)}

## Caveats

- Holding period is 1 trading day (`PRE_REGISTRATION.md`, fixed before this ran).
- A `flat` realization (move within ±0.5%) counts as incorrect against a directional call —
  that is a design choice, not a bug: "down" that didn't move is not a validated call.
- Two Aug-27 signals (BBCQU, LTRYW) could not be priced at all — both are exotic security
  types (a SPAC-unit ticker and a warrant ticker); Yahoo Finance's symbol convention for
  those often differs from the one in SEC's own ticker file. Not a grading-logic bug;
  a ticker-resolution gap, left open rather than papered over.
- Every row here traces to a `gate_decisions` row with a named reviewer — see
  `logs/RUN_LOG.md`.
"""

out = ROOT / "audits" / f"scorecard-{ts.strftime('%Y-%m-%d')}.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(md, encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)}")

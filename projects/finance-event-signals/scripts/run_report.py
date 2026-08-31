#!/usr/bin/env python3
"""run_report — the human report (P5, two customers).

The agent log is the structured service logs + the DB. This is the readable brief:
what was ingested, what the agent read vs. withheld, and what is waiting on a human.
Requires the stack up. Run: `make report`.

Writes reports/generated/run-<UTC-timestamp>.md
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPOSE = ["docker", "compose", "-f", str(ROOT / "deploy" / "docker-compose.yml")]


def q(sql: str) -> list[list[str]]:
    out = subprocess.run(
        COMPOSE + ["exec", "-T", "postgres", "psql", "-U", "fes", "-d", "fes",
                   "-A", "-F", "\t", "-t", "-c", sql],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        print(out.stderr, file=sys.stderr)
        sys.exit("run_report: postgres query failed — is the stack up? (make up)")
    return [line.split("\t") for line in out.stdout.strip().splitlines() if line.strip()]


def table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_(none)_\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(c.strip() for c in r) + " |")
    return "\n".join(out) + "\n"


ts = datetime.now(timezone.utc)
stamp = ts.strftime("%Y-%m-%d-%H%M")

by_source = q("SELECT source, count(*) FROM events GROUP BY 1 ORDER BY 1")
by_status = q("SELECT status, count(*) FROM signals GROUP BY 1 ORDER BY 2 DESC")
by_type = q("""SELECT event_type, direction, count(*) FROM signals
               WHERE status IN ('pending_review','actionable')
               GROUP BY 1,2 ORDER BY 3 DESC""")
withhold = q("SELECT withheld_reason, count(*) FROM signals WHERE status='withheld' GROUP BY 1 ORDER BY 2 DESC")
queue = q("""SELECT s.event_type, COALESCE(e.ticker,'-'), s.direction, round(s.confidence::numeric,2),
                    COALESCE(e.company,'?'), e.url
             FROM signals s JOIN events e ON e.event_key=s.event_key
             WHERE s.status='pending_review'
             ORDER BY s.confidence DESC NULLS LAST LIMIT 50""")
decisions = q("""SELECT g.verdict, g.reviewer, s.event_type, COALESCE(e.company,'?'), g.decided_at
                 FROM gate_decisions g JOIN signals s ON s.signal_id=g.signal_id
                 JOIN events e ON e.event_key=s.event_key ORDER BY g.decided_at DESC""")

n_events = sum(int(r[1]) for r in by_source) if by_source else 0
counts = {r[0]: int(r[1]) for r in by_status}
n_pending = counts.get("pending_review", 0)
n_withheld = counts.get("withheld", 0)
n_actionable = counts.get("actionable", 0)

md = f"""# Run report — {ts.strftime('%Y-%m-%d %H:%M UTC')}

**Summary.** {n_events} events ingested. The agent produced {n_pending + n_actionable} directional
reads and **withheld {n_withheld}** (looked and declined). {n_pending} reads are waiting for a
human at the gate; {n_actionable} have been cleared to actionable.

> This is the human report. The machine log is the structured service logs + PostgreSQL.
> `confidence` is a coarse prior for ordering the queue, **not a calibrated probability**
> (see `data/verified/SCHEMA_REFERENCE.md`). Nothing here is a trade recommendation.

## Ingested

{table(["source", "count"], by_source)}
Rejected events go to `events.deadletter` (not shown here) — run `make deadletter` or see
`audits/deadletter-*.md`.

## Agent output

{table(["status", "count"], by_status)}

### Directional reads by type

{table(["event_type", "direction", "count"], by_type)}

### Why reads were withheld

{table(["reason", "count"], withhold)}

## Review queue — waiting for a human

{table(["event_type", "ticker", "direction", "conf", "company", "filing"], queue)}

## Gate decisions

{table(["verdict", "reviewer", "event_type", "company", "when"], decisions)}

## Caveats

- Withhold rate is provider-dependent: the offline `deterministic` LLM only asserts a
  direction for strong event types / explicit keywords (~88% withhold on a mixed batch);
  `anthropic` emits on more. Confirm which provider ran (`LLM_PROVIDER` in `.env`).
- No read is validated against a realized price move until the Week-4 `outcome-grader`.
- Solo development — every gate decision above is `acting-reviewer SOLO`.
"""

out = ROOT / "reports" / "generated" / f"run-{stamp}.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(md, encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)}")

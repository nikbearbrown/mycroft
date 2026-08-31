"""outcome-grader — the honest loop (Week 4).

Grades every `actionable` signal against the realized price move, per the rule
fixed in PRE_REGISTRATION.md (committed BEFORE this script was written):

  price_at_publish = close at-or-before the signal's published_at date
  price_after      = close HOLDING_DAYS trading days later
  realized         = down if pct_move <= -0.5%, up if >= +0.5%, else flat
  correct          = predicted_direction == realized

If either bar is missing (not enough time has elapsed, or the ticker has no
price history), the row is written with correct=NULL and a grading_note —
NEVER a guessed value (P3). Idempotent: re-running upserts, so a signal that
was ungradeable last week can be graded once more time has passed.

Only ever reads `status='actionable'` signals. Never touches `rejected` or
`pending_review` — a rejected signal never became a claim to grade (P1).
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone

import psycopg2
import psycopg2.extras

HOLDING_DAYS = int(os.getenv("GRADER_HOLDING_DAYS", "1"))
MOVE_THRESHOLD_PCT = float(os.getenv("GRADER_MOVE_THRESHOLD_PCT", "0.5"))
DSN = os.getenv("POSTGRES_DSN", "postgres://fes:fes@postgres:5432/fes?sslmode=disable")
UA = os.getenv("PRICE_USER_AGENT", "finance-event-signals-grader/1.0")


def log(**kw):
    print(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **kw}), flush=True)


@dataclass
class Bar:
    d: date
    close: float


def fetch_daily_closes(ticker: str) -> list[Bar]:
    """Yahoo Finance chart API. stdlib only, no key. One month of daily bars
    is more than enough for a HOLDING_DAYS=1..5 grade."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1mo&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    result = data.get("chart", {}).get("result")
    if not result:
        return []
    r = result[0]
    ts = r.get("timestamp") or []
    closes = (r.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    bars = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        bars.append(Bar(d=datetime.fromtimestamp(t, tz=timezone.utc).date(), close=float(c)))
    bars.sort(key=lambda b: b.d)
    return bars


def grade_one(ticker: str, published: date, direction: str) -> dict:
    """Returns a dict of columns for signal_outcomes. Never raises for
    ordinary 'not enough data' cases — that's a grading_note, not an error."""
    if not ticker:
        return {"grading_note": "no ticker on this event — cannot price it"}

    try:
        bars = fetch_daily_closes(ticker)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return {"grading_note": f"price fetch failed: {e}"}
    except Exception as e:  # noqa: BLE001 — never let a bad ticker crash the batch
        return {"grading_note": f"price fetch error: {e}"}

    if not bars:
        return {"grading_note": "no price history returned for this ticker"}

    at_bars = [b for b in bars if b.d <= published]
    if not at_bars:
        return {"grading_note": f"no close on or before {published} in the fetched window"}
    at = at_bars[-1]

    after_candidates = [b for b in bars if b.d > at.d]
    if len(after_candidates) < HOLDING_DAYS:
        return {
            "grading_note": "insufficient time elapsed",
            "priced_at_date": at.d,
            "price_at_publish": at.close,
        }
    after = after_candidates[HOLDING_DAYS - 1]

    pct = (after.close - at.close) / at.close * 100.0
    if pct <= -MOVE_THRESHOLD_PCT:
        realized = "down"
    elif pct >= MOVE_THRESHOLD_PCT:
        realized = "up"
    else:
        realized = "flat"

    return {
        "price_at_publish": at.close,
        "priced_at_date": at.d,
        "price_after": after.close,
        "priced_after_date": after.d,
        "pct_move": round(pct, 4),
        "realized_direction": realized,
        "correct": (direction == realized),
        "grading_note": None,
    }


UPSERT_SQL = """
INSERT INTO signal_outcomes
  (signal_id, ticker, predicted_direction, price_at_publish, price_after, pct_move,
   realized_direction, holding_days, priced_at_date, priced_after_date, correct, grading_note)
VALUES (%(signal_id)s, %(ticker)s, %(predicted_direction)s, %(price_at_publish)s,
        %(price_after)s, %(pct_move)s, %(realized_direction)s, %(holding_days)s,
        %(priced_at_date)s, %(priced_after_date)s, %(correct)s, %(grading_note)s)
ON CONFLICT (signal_id) DO UPDATE SET
  ticker = EXCLUDED.ticker, predicted_direction = EXCLUDED.predicted_direction,
  price_at_publish = EXCLUDED.price_at_publish, price_after = EXCLUDED.price_after,
  pct_move = EXCLUDED.pct_move, realized_direction = EXCLUDED.realized_direction,
  holding_days = EXCLUDED.holding_days, priced_at_date = EXCLUDED.priced_at_date,
  priced_after_date = EXCLUDED.priced_after_date, correct = EXCLUDED.correct,
  grading_note = EXCLUDED.grading_note, graded_at = now()
"""

SELECT_ACTIONABLE = """
SELECT s.signal_id, e.ticker, e.published_at, s.direction, s.event_type
FROM signals s JOIN events e ON e.event_key = s.event_key
WHERE s.status = 'actionable'
ORDER BY e.published_at
"""


def main():
    conn = psycopg2.connect(DSN)
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(SELECT_ACTIONABLE)
    rows = cur.fetchall()
    log(event="started", actionable_signals=len(rows), holding_days=HOLDING_DAYS)

    graded, pending, failed = 0, 0, 0
    for row in rows:
        published = row["published_at"].date() if row["published_at"] else None
        if published is None:
            outcome = {"grading_note": "no published_at on this event"}
        else:
            outcome = grade_one(row["ticker"], published, row["direction"])
            time.sleep(0.3)  # be polite to the free API

        params = {
            "signal_id": row["signal_id"],
            "ticker": row["ticker"],
            "predicted_direction": row["direction"],
            "holding_days": HOLDING_DAYS,
            "price_at_publish": None,
            "price_after": None,
            "pct_move": None,
            "realized_direction": None,
            "priced_at_date": None,
            "priced_after_date": None,
            "correct": None,
            "grading_note": None,
        }
        params.update(outcome)
        cur.execute(UPSERT_SQL, params)

        if params["correct"] is not None:
            graded += 1
        elif params["grading_note"] and "error" in params["grading_note"].lower() or (
            params["grading_note"] and "failed" in (params["grading_note"] or "").lower()
        ):
            failed += 1
        else:
            pending += 1

        log(
            event="graded" if params["correct"] is not None else "not-graded",
            signal_id=row["signal_id"],
            ticker=row["ticker"],
            event_type=row["event_type"],
            note=params.get("grading_note"),
            correct=params["correct"],
        )

    log(event="done", graded=graded, pending=pending, failed=failed, total=len(rows))
    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        log(event="fatal", error=str(e))
        sys.exit(1)

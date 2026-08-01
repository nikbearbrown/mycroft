# =============================================================================
# Week 5 deliverable — historical backfill.
#
# Pulls ~90 days of HN Algolia history per watchlist entity in weekly chunks,
# paginating each chunk, deduping by objectID, scoring with the SAME functions
# Weeks 2/3 already wrote (metric_generation.parse_hit, compute_buzz_score.func)
# so backfilled scores are computed identically to live runs, then stores one
# row per entity-week into hn_buzz_runs (schema per DATABASE_SETUP.md).
#
# Run: python backfill_history.py [--days 90] [--dry-run]
# Needs SUPABASE_URL / SUPABASE_ANON_KEY in .env (or --dry-run to skip the DB
# and just write JSON files under backfill_output/ for inspection). Writes via
# the supabase-py REST client, not a raw Postgres connection.
# =============================================================================

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

from metric_generation import parse_hit
from compute_buzz_score import func as score_entities

ALGOLIA_URL = "https://hn.algolia.com/api/v1/search_by_date"
HITS_PER_PAGE = 100          # max allowed; keeps page count low for busy terms
REQUEST_DELAY_SEC = 0.2      # throttle between calls, stays well under rate limits
CHUNK_DAYS = 7               # Week 5 decision: weekly chunks (see plan.md)
BACKFILL_TABLE = "hn_buzz_runs_backfill"  # kept separate from hn_buzz_runs — see insert_rows()

load_dotenv()
WATCHLIST_PATH = Path(__file__).parent / "watchlist.json"
OUTPUT_DIR = Path(__file__).parent / "backfill_output"


def fetch_term_window(term, since_unix, until_unix):
    """Fetch every hit for one query term in [since_unix, until_unix), paginating."""
    hits = []
    page = 0
    while True:
        params = {
            # Quoted + advancedSyntax forces exact-phrase matching. Algolia's
            # default loose/fuzzy matching lets short terms (e.g. "AMD") match
            # unrelated stories (938 hits/week incl. "ICE facial recognition",
            # "weedkiller ingredient") and can even DROP real hits ("Ryzen"
            # unquoted returned 0; quoted returned 10) — confirmed by hand
            # against the live API before applying this fix.
            "query": f'"{term}"',
            "tags": "story",
            "advancedSyntax": "true",
            "numericFilters": f"created_at_i>{since_unix},created_at_i<{until_unix}",
            "hitsPerPage": HITS_PER_PAGE,
            "page": page,
        }
        resp = requests.get(ALGOLIA_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        hits.extend(data.get("hits", []))

        page += 1
        if page >= data.get("nbPages", 0):
            break
        time.sleep(REQUEST_DELAY_SEC)

    return hits


def week_chunks(total_days, chunk_days=CHUNK_DAYS):
    """Yield (since_unix, until_unix, label) walking backward from now in chunk_days steps."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    chunks = []
    cursor = now
    remaining = total_days
    while remaining > 0:
        span = min(chunk_days, remaining)
        until = cursor
        since = until - timedelta(days=span)
        chunks.append((int(since.timestamp()), int(until.timestamp()), since.strftime("%Y-%m-%d")))
        cursor = since
        remaining -= span
    return list(reversed(chunks))  # oldest first


def fetch_entity_week(entity_cfg, since_unix, until_unix):
    """Fetch + merge every query term for one entity over one week, dedupe by objectID."""
    hits_by_id = {}
    for term in entity_cfg["queryTerms"]:
        term_hits = fetch_term_window(term, since_unix, until_unix)
        for hit in term_hits:
            rec = parse_hit(hit)
            oid = rec["objectID"]
            if oid is not None:
                hits_by_id[oid] = rec
        time.sleep(REQUEST_DELAY_SEC)
    return list(hits_by_id.values())


def build_raw_metrics(entity_cfg, hits):
    fp_points = entity_cfg["frontPagePoints"]
    story_count = len(hits)
    total_points = sum(h["points"] for h in hits)
    total_comments = sum(h["num_comments"] for h in hits)
    front_page_count = sum(1 for h in hits if h["points"] >= fp_points)
    return {
        "storyCount": story_count,
        "totalPoints": total_points,
        "totalComments": total_comments,
        "frontPageCount": front_page_count,
    }


def score_entity_week(entity_cfg, run_date, hits):
    """Build one entity's scoring-input item for a given week (no score yet)."""
    raw_metrics = build_raw_metrics(entity_cfg, hits)
    return {
        "json": {
            "entity": entity_cfg["entity"],
            "ticker": entity_cfg["ticker"],
            "breakoutThreshold": entity_cfg["breakoutThreshold"],
            "runDate": run_date,
            "rawMetrics": raw_metrics,
            "lowConfidence": raw_metrics["storyCount"] < 3,
        }
    }


def watchlist_version_tag():
    # Watchlist governance (plan.md): backfilled rows are tagged with the
    # watchlist version in force today so a later v2 change can't silently
    # get compared against v1-era history.
    return "v1"


def run_backfill(total_days, dry_run):
    with open(WATCHLIST_PATH) as f:
        watchlist = json.load(f)

    chunks = week_chunks(total_days)
    print(f"Backfilling {len(watchlist)} entities x {len(chunks)} weekly chunks "
          f"({total_days} days) — dry_run={dry_run}")

    if dry_run:
        OUTPUT_DIR.mkdir(exist_ok=True)

    # Chunk outer, entity inner: one row per week covering ALL entities, so a
    # backfilled row has the same shape as a live run's leaderboard (per
    # DATABASE_SETUP.md — one row = one run, not one row per entity).
    rows = []
    for since_unix, until_unix, run_date in chunks:
        week_items = []
        for entity_cfg in watchlist:
            hits = fetch_entity_week(entity_cfg, since_unix, until_unix)
            week_items.append(score_entity_week(entity_cfg, run_date, hits))

        # Cold-start every week: backfill has no prior-run wiring, matching
        # Week 3/4 behavior for a run with no prior snapshot (acceleration=0).
        # Trailing baselines are computed separately (Week 5 plan step 8),
        # from this stored series, once all weeks are in.
        scored_week = score_entities(week_items)
        leaderboard = [s["json"] for s in scored_week]
        raw_metrics = {s["json"]["entity"]: s["json"]["rawMetrics"] for s in scored_week}

        rows.append({
            "run_date": run_date,
            "window_hours": CHUNK_DAYS * 24,
            "complete": True,
            "watchlist_version": watchlist_version_tag(),
            "leaderboard": leaderboard,
            "raw_metrics": raw_metrics,
        })

        for s in scored_week:
            j = s["json"]
            print(f"  {run_date}  {j['entity']:30s} stories={j['rawMetrics']['storyCount']:4d}  "
                  f"buzz={j['buzzScore']:5.1f}  lowConfidence={j['lowConfidence']}")

    if dry_run:
        out_path = OUTPUT_DIR / f"backfill_{watchlist_version_tag()}.json"
        with open(out_path, "w") as f:
            json.dump(rows, f, indent=2)
        print(f"\nWrote {len(rows)} rows to {out_path} (dry run — nothing inserted into Postgres).")
    else:
        insert_rows(rows)
        print(f"\nInserted {len(rows)} rows into {BACKFILL_TABLE}.")


def insert_rows(rows):
    from supabase import create_client

    # Written to a DEDICATED table, not hn_buzz_runs: the live workflow's
    # "Get Previous Run" query picks the latest row by created_at (insert
    # time), not run_date. A backfilled row inserted today would look like
    # the most recent run and get used as tomorrow's velocity baseline —
    # comparing a 24h daily window against a 168h weekly one. Kept separate
    # so backfill can never corrupt live velocity; Week 6's backtest queries
    # this table directly instead.
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
    # jsonb columns take a plain dict/list here — the client serializes it,
    # unlike the raw-SQL path in DATABASE_SETUP.md which needed ::jsonb casts.
    for row in rows:
        client.table(BACKFILL_TABLE).insert({
            "run_date": row["run_date"],
            "window_hours": row["window_hours"],
            "watchlist_version": row["watchlist_version"],
            "leaderboard": row["leaderboard"],
            "raw_metrics": row["raw_metrics"],
            "complete": row["complete"],
        }).execute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill ~90 days of HN buzz history.")
    parser.add_argument("--days", type=int, default=90, help="total days to backfill (default 90)")
    parser.add_argument("--dry-run", action="store_true",
                         help="skip Postgres insert; write JSON to backfill_output/ instead")
    args = parser.parse_args()
    run_backfill(args.days, args.dry_run)

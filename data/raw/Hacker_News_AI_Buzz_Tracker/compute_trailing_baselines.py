# =============================================================================
# Week 5 deliverable — trailing baselines (plan.md step 8).
#
# Reads the weekly rows backfill_history.py wrote to hn_buzz_runs_backfill and
# computes, per watchlist entity, a trailing average of raw metrics and buzz
# score across the backfilled window. This is what lets velocity and the Week
# 6 backtest be meaningful from day one instead of cold-starting: instead of
# comparing a live run to "no prior snapshot", it can compare against "this
# entity's typical week."
#
# Run: python compute_trailing_baselines.py [--dry-run]
# Needs SUPABASE_URL / SUPABASE_ANON_KEY in .env (or --dry-run to read the
# local backfill_output/backfill_v1.json instead of Supabase, and write
# results to backfill_output/trailing_baselines.json instead of the DB).
# =============================================================================

import argparse
import json
import os
from pathlib import Path
from statistics import mean

from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = Path(__file__).parent / "backfill_output"
BACKFILL_TABLE = "hn_buzz_runs_backfill"
BASELINE_TABLE = "entity_baselines"


def fetch_backfill_rows(dry_run):
    """Return the list of weekly backfill rows, from Supabase or the local dry-run file."""
    if dry_run:
        path = OUTPUT_DIR / "backfill_v1.json"
        with open(path) as f:
            return json.load(f)

    from supabase import create_client
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
    resp = client.table(BACKFILL_TABLE).select("run_date, watchlist_version, leaderboard").execute()
    return resp.data


def compute_baselines(rows):
    """Group every entity's weekly rawMetrics/buzzScore across all rows, average them."""
    by_entity = {}
    watchlist_version = None
    for row in rows:
        watchlist_version = row.get("watchlist_version", watchlist_version)
        for entity_row in row["leaderboard"]:
            entry = by_entity.setdefault(entity_row["entity"], {
                "ticker": entity_row["ticker"],
                "storyCounts": [],
                "totalPoints": [],
                "totalComments": [],
                "frontPageCounts": [],
                "buzzScores": [],
            })
            m = entity_row["rawMetrics"]
            entry["storyCounts"].append(m["storyCount"])
            entry["totalPoints"].append(m["totalPoints"])
            entry["totalComments"].append(m["totalComments"])
            entry["frontPageCounts"].append(m["frontPageCount"])
            entry["buzzScores"].append(entity_row["buzzScore"])

    baselines = []
    for entity, entry in by_entity.items():
        weeks_used = len(entry["storyCounts"])
        baselines.append({
            "entity": entity,
            "ticker": entry["ticker"],
            "watchlist_version": watchlist_version,
            "weeks_used": weeks_used,
            "avg_story_count": round(mean(entry["storyCounts"]), 2),
            "avg_total_points": round(mean(entry["totalPoints"]), 2),
            "avg_total_comments": round(mean(entry["totalComments"]), 2),
            "avg_front_page_count": round(mean(entry["frontPageCounts"]), 2),
            "avg_buzz_score": round(mean(entry["buzzScores"]), 2),
        })

    baselines.sort(key=lambda b: b["avg_buzz_score"], reverse=True)
    return baselines


def write_baselines(baselines, dry_run):
    if dry_run:
        OUTPUT_DIR.mkdir(exist_ok=True)
        out_path = OUTPUT_DIR / "trailing_baselines.json"
        with open(out_path, "w") as f:
            json.dump(baselines, f, indent=2)
        print(f"\nWrote {len(baselines)} entity baselines to {out_path} (dry run — nothing inserted).")
        return

    from supabase import create_client
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
    for b in baselines:
        client.table(BASELINE_TABLE).insert(b).execute()
    print(f"\nInserted {len(baselines)} entity baselines into {BASELINE_TABLE}.")


def run(dry_run):
    rows = fetch_backfill_rows(dry_run)
    print(f"Loaded {len(rows)} weekly backfill rows.")

    baselines = compute_baselines(rows)
    for b in baselines:
        print(f"  {b['entity']:30s} weeks={b['weeks_used']:2d}  "
              f"avgStories={b['avg_story_count']:6.1f}  avgBuzz={b['avg_buzz_score']:5.1f}")

    write_baselines(baselines, dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute per-entity trailing baselines from the backfill.")
    parser.add_argument("--dry-run", action="store_true",
                         help="read/write local JSON under backfill_output/ instead of Supabase")
    args = parser.parse_args()
    run(args.dry_run)

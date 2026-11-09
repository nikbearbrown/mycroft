"""
pull_eval_claims.py — Phase 1 of the classifier evaluation: pull ~50
independent claims across 8-10 patents from BigQuery and write them as
an unlabeled CSV in the format eval_classifier.py reads.

Cost basis: `patents-public-data.patents.publications` is not
partitioned or clustered, so a query is billed for the full size of
every column it touches, regardless of how many rows it returns. That
is why each single-patent lookup so far has cost ~$0.71 — and why this
script fetches its whole candidate pool in ONE query rather than one
per patent. Asking for 80 candidates costs about the same as asking
for 1.

Cost safety:
  - Without --yes, the script only runs a BigQuery dry run (free),
    prints the bytes that would be scanned and the on-demand cost,
    and exits.
  - With --yes, the real query is submitted with maximum_bytes_billed
    set just above the dry-run figure, so BigQuery itself refuses the
    job if the scan would come out larger than what was shown.
  - The raw pool is cached to eval/claims_pool.jsonl. Re-running the
    selection (different --target, --cap, etc.) reads the cache and
    makes no query at all.

Two ways to choose patents:
  sample (default) — US B2 grants in a date range, up to --per-section
      candidates from each CPC section A-H (by first-listed CPC code),
      picked deterministically by a hash of the publication number.
      Spreading across sections is what tests whether "narrow /
      defensive" is the prompt or the domains we happened to read.
  --patents — an explicit list of publication numbers instead.

Selection (local, free): candidates whose claims don't parse cleanly
(no claims, or numbering that isn't 1..n) are dropped. Then patents are
taken round-robin across CPC sections, up to --cap independent claims
each, until --target claims are reached (min 8 / max 10 patents).

Usage:
    python pull_eval_claims.py                      # dry run: plan + cost, no charge
    python pull_eval_claims.py --yes                # run the query, write the CSV
    python pull_eval_claims.py --from-cache         # re-select from the cached pool, no query
    python pull_eval_claims.py --patents US-11791319-B2 US-10822628-B2 ...
"""
import argparse
import csv
import html
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from google.cloud import bigquery

from claims_parser import split_claims

PROJECT = "patent-intelligence-system"
TABLE = "patents-public-data.patents.publications"

# BigQuery on-demand query pricing, USD per TiB scanned (US multi-region).
# The project may be on the Sandbox / free tier (first 1 TiB per month
# free), in which case the actual charge is $0 — this is the list price.
USD_PER_TIB = 6.25

# CPC sections. Y (cross-sectional tagging) is left out on purpose: it is
# never a patent's primary classification in a meaningful sense.
CPC_SECTIONS = {
    "A": "Human necessities",
    "B": "Performing operations; transporting",
    "C": "Chemistry; metallurgy",
    "D": "Textiles; paper",
    "E": "Fixed constructions",
    "F": "Mechanical engineering; lighting; heating; weapons",
    "G": "Physics",
    "H": "Electricity",
}

EVAL_DIR = Path(__file__).parent / "eval"
POOL_PATH = EVAL_DIR / "claims_pool.jsonl"
OUT_PATH = EVAL_DIR / "labeled_claims.csv"

CSV_COLUMNS = ["publication_number", "claim_number", "gold_breadth", "gold_posture",
               "label_notes", "claim_text", "cpc_section", "title"]

# Shared SELECT: English, non-truncated claims and title, first-listed CPC.
SELECT_FIELDS = """
    publication_number,
    grant_date,
    (SELECT SUBSTR(c.code, 1, 1) FROM UNNEST(cpc) AS c WHERE c.first LIMIT 1) AS cpc_section,
    (SELECT t.text FROM UNNEST(title_localized) AS t WHERE t.language = 'en' LIMIT 1) AS title,
    (SELECT cl.text FROM UNNEST(claims_localized) AS cl
       WHERE cl.language = 'en' AND NOT IFNULL(cl.truncated, FALSE) LIMIT 1) AS claims_text
"""

SAMPLE_QUERY = f"""
WITH candidates AS (
  SELECT {SELECT_FIELDS}
  FROM `{TABLE}`
  WHERE country_code = 'US'
    AND kind_code = 'B2'
    AND grant_date BETWEEN @start_date AND @end_date
)
SELECT * FROM candidates
WHERE claims_text IS NOT NULL
  AND cpc_section IN UNNEST(@sections)
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY cpc_section
  ORDER BY FARM_FINGERPRINT(CONCAT(publication_number, @seed))
) <= @per_section
"""

EXPLICIT_QUERY = f"""
SELECT {SELECT_FIELDS}
FROM `{TABLE}`
WHERE publication_number IN UNNEST(@patents)
"""


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def build_job(args) -> (str, List[bigquery.ScalarQueryParameter]):
    if args.patents:
        return EXPLICIT_QUERY, [bigquery.ArrayQueryParameter("patents", "STRING", args.patents)]
    return SAMPLE_QUERY, [
        bigquery.ScalarQueryParameter("start_date", "INT64", args.start_date),
        bigquery.ScalarQueryParameter("end_date", "INT64", args.end_date),
        bigquery.ArrayQueryParameter("sections", "STRING", sorted(CPC_SECTIONS)),
        bigquery.ScalarQueryParameter("per_section", "INT64", args.per_section),
        bigquery.ScalarQueryParameter("seed", "STRING", args.seed),
    ]


def dry_run(client: bigquery.Client, query: str, params) -> int:
    config = bigquery.QueryJobConfig(query_parameters=params, dry_run=True, use_query_cache=False)
    return client.query(query, job_config=config).total_bytes_processed


def cost_usd(n_bytes: int) -> float:
    return n_bytes / 2**40 * USD_PER_TIB


def run_query(client: bigquery.Client, query: str, params, cap_bytes: int) -> List[dict]:
    config = bigquery.QueryJobConfig(query_parameters=params, maximum_bytes_billed=cap_bytes)
    job = client.query(query, job_config=config)
    rows = [dict(r) for r in job.result()]
    billed = job.total_bytes_billed or 0
    print(f"Query done: {len(rows)} rows, {billed / 2**30:.1f} GiB billed "
          f"(~${cost_usd(billed):.2f} list price), cache hit: {job.cache_hit}")
    return rows


# ---------------------------------------------------------------------------
# Parse + select (local, free)
# ---------------------------------------------------------------------------

def parse_pool(rows: List[dict]) -> (List[dict], List[str]):
    """Splits each patent's claims and keeps only patents that parse
    cleanly. Returns (usable patents, reasons for drops)."""
    usable, dropped = [], []
    for row in rows:
        pub = row["publication_number"]
        # BigQuery's claims text carries HTML entities (e.g. "&#39;" for an
        # apostrophe); unescape so labelers and the classifier see real text.
        claims = split_claims(html.unescape(row["claims_text"] or ""))
        numbers = [c.number for c in claims]
        if not claims:
            dropped.append(f"{pub}: claims text present but parser found 0 claims")
            continue
        if numbers != list(range(1, len(numbers) + 1)):
            dropped.append(f"{pub}: claim numbering not 1..n ({numbers[:8]}...) — parse is suspect")
            continue
        independents = [c for c in claims if c.is_independent]
        if not independents:
            dropped.append(f"{pub}: no independent claims found")
            continue
        usable.append({
            "publication_number": pub,
            "cpc_section": row.get("cpc_section") or "?",
            "title": html.unescape(row.get("title") or ""),
            "total_claims": len(claims),
            "independents": [{"number": c.number, "text": c.text} for c in independents],
        })
    return usable, dropped


def spread(items: list, k: int) -> list:
    """k evenly spaced items, keeping first and last — so a capped patent
    contributes e.g. its system, method, and medium claims, not just the
    first k in a row."""
    if len(items) <= k:
        return items
    step = (len(items) - 1) / (k - 1) if k > 1 else 0
    return [items[round(i * step)] for i in range(k)]


def select(patents: List[dict], target: int, cap: int,
           min_patents: int, max_patents: int, min_independent: int) -> List[dict]:
    by_section: Dict[str, List[dict]] = defaultdict(list)
    for p in patents:
        if len(p["independents"]) >= min_independent:
            by_section[p["cpc_section"]].append(p)

    def done():
        total = sum(len(p["selected"]) for p in chosen)
        return len(chosen) >= max_patents or (total >= target and len(chosen) >= min_patents)

    chosen = []
    queues = {s: list(ps) for s, ps in sorted(by_section.items())}
    while queues and not done():
        for section in list(queues):
            if done():
                break
            chosen.append({**queues[section].pop(0)})
            chosen[-1]["selected"] = spread(chosen[-1]["independents"], cap)
            if not queues[section]:
                del queues[section]

    # Overshoot is trimmed from whichever patent contributes the most, so
    # no single patent dominates the labels.
    while sum(len(p["selected"]) for p in chosen) > target:
        biggest = max(chosen, key=lambda p: len(p["selected"]))
        if len(biggest["selected"]) <= 1:
            break
        biggest["selected"] = spread(biggest["independents"], len(biggest["selected"]) - 1)
    return chosen


def write_csv(chosen: List[dict], path: Path) -> int:
    n = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for p in chosen:
            for c in p["selected"]:
                w.writerow({
                    "publication_number": p["publication_number"],
                    "claim_number": c["number"],
                    "gold_breadth": "",
                    "gold_posture": "",
                    "label_notes": "",
                    "claim_text": c["text"],
                    "cpc_section": p["cpc_section"],
                    "title": p["title"],
                })
                n += 1
    return n


def print_selection(chosen: List[dict], pool_size: int, dropped: List[str]):
    print(f"\nPool: {pool_size} patents parsed cleanly, {len(dropped)} dropped")
    for d in dropped:
        print(f"  dropped {d}")
    total = sum(len(p["selected"]) for p in chosen)
    print(f"\nSelected {total} independent claims from {len(chosen)} patents:")
    for p in chosen:
        sec = p["cpc_section"]
        print(f"  {p['publication_number']:<18} {sec} ({CPC_SECTIONS.get(sec, '?')[:28]:<28}) "
              f"{len(p['selected'])}/{len(p['independents'])} indep. — {p['title'][:50]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true", help="actually run the BigQuery query (costs money)")
    ap.add_argument("--from-cache", action="store_true", help=f"re-select from {POOL_PATH.name}, no query")
    ap.add_argument("--patents", nargs="+", help="explicit publication numbers instead of sampling")
    ap.add_argument("--start-date", type=int, default=20200101, help="grant date lower bound, YYYYMMDD")
    ap.add_argument("--end-date", type=int, default=20241231, help="grant date upper bound, YYYYMMDD")
    ap.add_argument("--per-section", type=int, default=20, help="candidates per CPC section in the pool")
    ap.add_argument("--seed", default="mycroft-eval-1", help="changes which patents the sample picks")
    ap.add_argument("--target", type=int, default=50, help="independent claims to select")
    ap.add_argument("--cap", type=int, default=6, help="max independent claims taken from one patent")
    ap.add_argument("--min-independent", type=int,
                    help="skip patents with fewer independent claims (default 3 when sampling, 1 with --patents)")
    ap.add_argument("--min-patents", type=int, default=8)
    ap.add_argument("--max-patents", type=int, default=10)
    ap.add_argument("--force", action="store_true", help=f"overwrite an existing {OUT_PATH.name}")
    args = ap.parse_args()

    if args.min_independent is None:
        args.min_independent = 1 if args.patents else 3
    EVAL_DIR.mkdir(exist_ok=True)

    if args.from_cache:
        if not POOL_PATH.exists():
            sys.exit(f"No cached pool at {POOL_PATH} — run with --yes first")
        rows = [json.loads(l) for l in POOL_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"Loaded {len(rows)} cached rows from {POOL_PATH} (no query)")
    else:
        client = bigquery.Client(project=PROJECT)
        query, params = build_job(args)
        n_bytes = dry_run(client, query, params)
        mode = f"explicit list of {len(args.patents)}" if args.patents else (
            f"sample: up to {args.per_section} per CPC section x {len(CPC_SECTIONS)} sections, "
            f"grants {args.start_date}-{args.end_date}")
        print("Query plan (dry run — nothing billed):")
        print(f"  mode:          {mode}")
        print(f"  bytes scanned: {n_bytes:,} ({n_bytes / 2**30:.1f} GiB)")
        print(f"  cost:          ~${cost_usd(n_bytes):.2f} at ${USD_PER_TIB}/TiB on-demand "
              f"($0 if still inside the free 1 TiB/month)")
        print(f"  queries:       1")
        if not args.yes:
            print("\nDry run only. Re-run with --yes to execute.")
            return
        if POOL_PATH.exists() and not args.force:
            sys.exit(f"{POOL_PATH} already exists — use --from-cache to reuse it, "
                     f"or --force to pay for a fresh pull")
        rows = run_query(client, query, params, cap_bytes=int(n_bytes * 1.05) + 1)
        with POOL_PATH.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"Raw pool cached to {POOL_PATH}")

    patents, dropped = parse_pool(rows)
    chosen = select(patents, args.target, args.cap, args.min_patents,
                    args.max_patents, args.min_independent)
    print_selection(chosen, len(patents), dropped)

    if OUT_PATH.exists() and not args.force:
        sys.exit(f"\n{OUT_PATH} already exists (it may hold your labels) — "
                 f"pass --force to overwrite it")
    n = write_csv(chosen, OUT_PATH)
    print(f"\nWrote {n} unlabeled claims to {OUT_PATH}")


if __name__ == "__main__":
    main()

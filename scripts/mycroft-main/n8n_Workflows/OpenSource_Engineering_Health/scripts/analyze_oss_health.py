#!/usr/bin/env python3
import argparse
import csv
import json
import math
import os
from pathlib import Path
from datetime import datetime, timezone


def parse_iso(ts: str) -> datetime:
    # Handles "Z" timestamps from GitHub (UTC)
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


def activity_score(days_since_push: float) -> int:
    # 0–30 (freshness)
    if days_since_push <= 1:
        return 30
    if days_since_push <= 7:
        return 24
    if days_since_push <= 30:
        return 18
    if days_since_push <= 90:
        return 12
    if days_since_push <= 180:
        return 6
    return 0


def issue_health_score(issues_per_1k_stars: float) -> int:
    # 0–20 (lower is better)
    if issues_per_1k_stars <= 10:
        return 20
    if issues_per_1k_stars <= 20:
        return 15
    if issues_per_1k_stars <= 40:
        return 10
    if issues_per_1k_stars <= 80:
        return 5
    return 0

from typing import Optional

def license_score(license_name: Optional[str]) -> int:

    # 0–10
    return 10 if license_name else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="~/n8n-files/raw", help="Folder containing repo JSON files")
    parser.add_argument("--out-dir", default="~/n8n-files/analysis", help="Folder to write analysis outputs")
    args = parser.parse_args()

    raw_dir = Path(os.path.expanduser(args.raw_dir))
    out_dir = Path(os.path.expanduser(args.out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted([p for p in raw_dir.glob("*.json") if not p.name.startswith("_")])
    if not json_files:
        raise SystemExit(f"No JSON files found in {raw_dir}")

    rows = []
    for fp in json_files:
        with fp.open("r", encoding="utf-8") as f:
            data = json.load(f)

        repo_full = data.get("repo", "")
        metrics = data.get("metrics", {})
        links = data.get("links", {})

        stars = int(metrics.get("stars", 0))
        forks = int(metrics.get("forks", 0))
        issues = int(metrics.get("open_issues_count_including_prs", 0))
        pushed_at = metrics.get("pushed_at")
        collected_at = data.get("collected_at")
        lic = metrics.get("license")

        # Compute days since push (relative to latest collected_at in the batch)
        rows.append({
            "file": fp.name,
            "repo": repo_full,
            "stars": stars,
            "forks": forks,
            "open_issues_incl_prs": issues,
            "pushed_at": pushed_at,
            "collected_at": collected_at,
            "license": lic,
            "repo_url": links.get("repo"),
            "issues_url": links.get("issues"),
            "pulls_url": links.get("pulls"),
            "releases_url": links.get("releases"),
            "security_url": links.get("security"),
        })

    # Reference "now" as the latest collected_at we have
    now = max(parse_iso(r["collected_at"]) for r in rows if r["collected_at"])

    # Add derived metrics
    for r in rows:
        pushed = parse_iso(r["pushed_at"]) if r["pushed_at"] else now
        days = (now - pushed).total_seconds() / 86400.0
        stars = r["stars"]
        issues = r["open_issues_incl_prs"]

        issues_per_1k = issues / (stars / 1000.0) if stars else float("inf")

        r["days_since_push"] = round(days, 3)
        r["issues_per_1k_stars"] = round(issues_per_1k, 3)

    # Popularity score (0–40) via log-normalized stars/forks within this set
    max_log_stars = max(math.log10(r["stars"] + 1) for r in rows)
    max_log_forks = max(math.log10(r["forks"] + 1) for r in rows)

    for r in rows:
        stars_part = 25.0 * (math.log10(r["stars"] + 1) / max_log_stars) if max_log_stars else 0.0
        forks_part = 15.0 * (math.log10(r["forks"] + 1) / max_log_forks) if max_log_forks else 0.0

        pop = stars_part + forks_part
        act = activity_score(r["days_since_push"])
        iss = issue_health_score(r["issues_per_1k_stars"])
        lic = license_score(r["license"])

        r["stars_score_25"] = round(stars_part, 2)
        r["forks_score_15"] = round(forks_part, 2)
        r["popularity_score_40"] = round(pop, 2)
        r["activity_score_30"] = act
        r["issue_health_score_20"] = iss
        r["license_score_10"] = lic
        r["total_score_100"] = round(pop + act + iss + lic, 2)

    # Write signals CSV
    signals_path = out_dir / "oss_signals.csv"
    with signals_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Write scores CSV
    score_fields = [
        "repo", "total_score_100",
        "popularity_score_40", "stars_score_25", "forks_score_15",
        "activity_score_30", "days_since_push",
        "issue_health_score_20", "issues_per_1k_stars",
        "license_score_10", "license",
        "repo_url"
    ]
    scores_sorted = sorted(rows, key=lambda x: x["total_score_100"], reverse=True)
    scores_path = out_dir / "oss_scores.csv"
    with scores_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=score_fields)
        writer.writeheader()
        for r in scores_sorted:
            writer.writerow({k: r.get(k) for k in score_fields})

    # Write Markdown report
    report_path = out_dir / "oss_report.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# OSS Engineering Maturity – Comparison Report\n\n")
        f.write(f"Generated from JSON snapshots in `{raw_dir}`.\n\n")
        f.write(f"**Scoring (0–100)** = Popularity (0–40) + Activity (0–30) + Issue Health (0–20) + License (0–10)\n\n")
        f.write("## Results (ranked)\n\n")
        f.write("| Rank | Repo | Total | Popularity | Activity | Issue Health | License | Issues/1k Stars |\n")
        f.write("|---:|---|---:|---:|---:|---:|---:|---:|\n")
        for i, r in enumerate(scores_sorted, start=1):
            f.write(
                f"| {i} | {r['repo']} | {r['total_score_100']} | "
                f"{r['popularity_score_40']} | {r['activity_score_30']} | "
                f"{r['issue_health_score_20']} | {r['license_score_10']} | "
                f"{r['issues_per_1k_stars']} |\n"
            )

        f.write("\n## Repo-by-repo notes\n\n")
        for r in scores_sorted:
            f.write(f"### {r['repo']}\n")
            f.write(f"- Stars: {r['stars']}, Forks: {r['forks']}\n")
            f.write(f"- Open issues (incl PRs): {r['open_issues_incl_prs']} (≈ {r['issues_per_1k_stars']} per 1k stars)\n")
            f.write(f"- Last pushed: {r['pushed_at']} (~{r['days_since_push']} days ago)\n")
            f.write(f"- License: {r['license']}\n")
            f.write(f"- Repo: {r['repo_url']}\n\n")

        f.write("## Notes / limitations\n")
        f.write("- Popularity is normalized within this repo set (log scale).\n")
        f.write("- Issue Health uses issue-density as a proxy; it doesn’t measure issue response time.\n")
        f.write("- Next iteration: add PR velocity, time-to-close, bus factor, CI status, release cadence.\n")

    print("✅ Wrote:")
    print(f" - {signals_path}")
    print(f" - {scores_path}")
    print(f" - {report_path}")


if __name__ == "__main__":
    main()

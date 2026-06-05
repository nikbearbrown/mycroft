#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any

ROOT = Path(__file__).resolve().parents[1]

CLEAN_PROFILES = ROOT / "data/outputs/clean_company_profiles.json"
SCORECARD = ROOT / "data/outputs/company_scorecard.csv"
WINNER_REPORT = ROOT / "data/outputs/winner_report.md"

# --- helpers ---------------------------------------------------------

def load_clean_profiles() -> List[Dict[str, Any]]:
    if not CLEAN_PROFILES.exists():
        raise FileNotFoundError(f"Missing: {CLEAN_PROFILES}. Run scripts/03_clean_and_score.py first.")
    return json.loads(CLEAN_PROFILES.read_text(encoding="utf-8", errors="ignore"))

def load_scorecard() -> List[Dict[str, str]]:
    if not SCORECARD.exists():
        raise FileNotFoundError(f"Missing: {SCORECARD}. Run scripts/03_clean_and_score.py first.")
    with SCORECARD.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def normalize_company(s: str) -> str:
    return (s or "").strip().lower()

def find_company_in_question(q: str, companies: List[str]) -> str | None:
    ql = q.lower()
    for c in companies:
        if c in ql:
            return c
    return None

def fmt_bullets(lines: List[str], limit: int = 6) -> str:
    out = []
    for s in lines[:limit]:
        one = " ".join(str(s).split())
        if one:
            out.append(f"- {one}")
    return "\n".join(out) if out else "- (no data)"

def fmt_links(links: List[Dict[str, str]], limit: int = 6) -> str:
    out = []
    for x in links[:limit]:
        title = " ".join((x.get("title") or "").split())
        url = (x.get("url") or "").strip()
        if title and url:
            out.append(f"- {title} — {url}")
    return "\n".join(out) if out else "- (no links)"

# --- answer builders --------------------------------------------------

def answer_pricing(profiles: Dict[str, Dict[str, Any]]) -> str:
    md = ["# Pricing comparison (snippets)\n"]
    for company, p in profiles.items():
        md.append(f"## {company}")
        md.append(fmt_bullets(p.get("pricing_highlights", []), 8))
        md.append("")
    md.append("**Note:** Pricing is extracted from public pages and may include truncated snippets; use links as ground truth.")
    return "\n".join(md)

def answer_recent_news(profiles: Dict[str, Dict[str, Any]]) -> str:
    md = ["# Recent / News signals (clean links)\n"]
    for company, p in profiles.items():
        md.append(f"## {company}")
        md.append(fmt_links(p.get("recent_links", []), 8))
        md.append("")
    return "\n".join(md)

def answer_positioning(profiles: Dict[str, Dict[str, Any]]) -> str:
    md = ["# GTM / Positioning signals (top terms)\n",
          "These are extracted ‘surface signals’ (keywords) from the cleaned pages.\n"]
    for company, p in profiles.items():
        md.append(f"## {company}")
        terms = p.get("top_terms", [])
        md.append(f"- **Top terms:** {', '.join(terms[:18]) if terms else '(none)'}")
        md.append("")
    return "\n".join(md)

def answer_winner(score_rows: List[Dict[str, str]]) -> str:
    rows = sorted(score_rows, key=lambda r: float(r.get("total_score", "0") or 0), reverse=True)

    md = [
        "# Who is doing better? (heuristic scorecard)\n",
        "This uses cleaned public signals and an explainable heuristic:\n"
        "- **Release signal**: count of real announcement links\n"
        "- **Enterprise signal**: enterprise/sales/security terms\n"
        "- **Developer signal**: tokens/api/platform/docs terms\n"
        "- **Pricing signal**: presence of pricing markers in extracted pricing snippets\n",
        "## Ranking\n",
    ]
    for r in rows:
        md.append(
            f"- **{r['company']}** — score={r['total_score']} "
            f"(release={r['release_signal']}, enterprise={r['enterprise_signal']}, "
            f"dev={r['developer_signal']}, pricing={r['pricing_signal']})"
        )

    # Short interpretation (top 2)
    top = rows[0]
    second = rows[1] if len(rows) > 1 else None
    md.append("\n## Why this ranking happened (based on captured evidence)\n")
    md.append(
        f"- **{top['company']}** leads mainly because of higher **release signal** (more product/announcement links captured)."
    )
    if second:
        md.append(
            f"- **{second['company']}** scores strongly on **enterprise/pricing signals**, even with fewer release links."
        )

    md.append("\nIf you want a different definition of “better” (enterprise GTM vs pricing vs shipping velocity), we can re-weight the score.")
    return "\n".join(md)

def answer_single_company(company: str, p: Dict[str, Any]) -> str:
    md = [f"# {company} — snapshot\n"]
    md.append(f"**Sources used:** {', '.join(p.get('sources_used', []))}")
    md.append("")
    md.append("## Positioning signals")
    terms = p.get("top_terms", [])
    md.append(f"- {', '.join(terms[:20]) if terms else '(none)'}")
    md.append("")
    md.append("## Pricing (snippets)")
    md.append(fmt_bullets(p.get("pricing_highlights", []), 10))
    md.append("")
    md.append("## Recent links (clean)")
    md.append(fmt_links(p.get("recent_links", []), 10))
    return "\n".join(md)

# --- router -----------------------------------------------------------

def route(question: str) -> str:
    q = (question or "").strip()
    ql = q.lower()

    prof_list = load_clean_profiles()
    companies = [normalize_company(p.get("company")) for p in prof_list]
    profiles = {normalize_company(p.get("company")): p for p in prof_list}

    # single-company detection
    detected = find_company_in_question(ql, companies)
    if detected and any(k in ql for k in ["pricing", "price", "news", "recent", "position", "gtm", "terms", "snapshot"]):
        return answer_single_company(detected, profiles[detected])

    if any(k in ql for k in ["pricing", "price", "cost", "token"]):
        return answer_pricing(profiles)

    if any(k in ql for k in ["recent", "news", "release", "partnership", "announcement", "what's new", "whats new"]):
        return answer_recent_news(profiles)

    if any(k in ql for k in ["position", "positioning", "gtm", "messaging", "focus", "enterprise", "developer", "strategy"]):
        return answer_positioning(profiles)

    if any(k in ql for k in ["better", "winner", "leading", "stronger", "who wins", "best"]):
        rows = load_scorecard()
        return answer_winner(rows)

    # fallback / help
    return (
        "# Ask me something like:\n"
        "- `compare pricing`\n"
        "- `recent news`\n"
        "- `positioning`\n"
        "- `which company is doing better?`\n"
        "- `openai snapshot` / `anthropic pricing` / `cohere news`\n"
    )

def main():
    if len(sys.argv) == 1:
        print("Interactive mode. Type a question, or 'exit'.\n")
        while True:
            q = input("Q> ").strip()
            if q.lower() in {"exit", "quit"}:
                break
            print("\n" + route(q) + "\n")
            print("-" * 70 + "\n")
        return

    q = " ".join(sys.argv[1:])
    print(route(q))

if __name__ == "__main__":
    main()
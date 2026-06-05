import json
import csv
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
IN_PROFILES = ROOT / "data/outputs/company_profiles.json"

OUT_CLEAN_PROFILES = ROOT / "data/outputs/clean_company_profiles.json"
OUT_CLEAN_SUMMARY = ROOT / "data/outputs/clean_summary.md"
OUT_SCORECARD = ROOT / "data/outputs/company_scorecard.csv"
OUT_WINNER = ROOT / "data/outputs/winner_report.md"

BAD_TERM_SUBSTRINGS = [
    "png", "webp", "svg", "cdn", "ctfassets", "cookie", "logo", "image", "assets", "sanity", "ghost"
]

ENTERPRISE_KWS = {"enterprise", "sales", "contact", "security", "compliance", "seats"}
DEV_KWS = {"api", "tokens", "platform", "developer", "docs", "sdk"}
PRICING_KWS = {"pricing", "$", "mtok", "1m", "billed", "subscription", "annual", "monthly", "contact sales"}

def looks_like_noise(title: str, url: str) -> bool:
    t = (title or "").lower()
    u = (url or "").lower()
    if "skip to" in t or "privacy policy" in t or "press kit" in t:
        return True
    if t.startswith("image"):
        return True
    if any(x in u for x in ["svg", "png", "webp", "jpg", "cdn", "cookieyes", "logo"]):
        return True
    return False

def clean_terms(terms):
    out = []
    for term in terms or []:
        tl = term.lower()
        if any(b in tl for b in BAD_TERM_SUBSTRINGS):
            continue
        out.append(term)
    return out

def clean_links(links):
    out = []
    for x in links or []:
        title, url = x.get("title",""), x.get("url","")
        if looks_like_noise(title, url):
            continue
        out.append({"title": title, "url": url})
    return out

def kw_score(terms, vocab):
    s = set([t.lower() for t in terms or []])
    return sum(1 for v in vocab if v in s)

def pricing_strength(pricing_highlights):
    joined = " ".join(pricing_highlights or []).lower()
    return sum(1 for k in PRICING_KWS if k in joined)

def release_signal(clean_links_list):
    # count links that look like real announcements
    c = 0
    for x in clean_links_list:
        t = x["title"].lower()
        if "introducing" in t or re.search(r"\bjan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec\b", t):
            c += 1
    return c

def main():
    profiles = json.loads(IN_PROFILES.read_text())
    clean_profiles = []
    score_rows = []

    for p in profiles:
        company = p["company"]

        terms = clean_terms(p.get("top_terms", []))
        links = clean_links(p.get("recent_links", []))
        pricing = p.get("pricing_highlights", [])

        ent = kw_score(terms, ENTERPRISE_KWS)
        dev = kw_score(terms, DEV_KWS)
        price_sig = pricing_strength(pricing)
        rel = release_signal(links)

        total = round(2.0*rel + 1.5*ent + 1.0*dev + 1.0*price_sig, 2)

        clean_profiles.append({
            **p,
            "top_terms": terms,
            "recent_links": links,
        })

        score_rows.append({
            "company": company,
            "sources_used": ",".join(p.get("sources_used", [])),
            "release_signal": rel,
            "enterprise_signal": ent,
            "developer_signal": dev,
            "pricing_signal": price_sig,
            "total_score": total,
        })

    # write clean profiles
    OUT_CLEAN_PROFILES.write_text(json.dumps(clean_profiles, indent=2), encoding="utf-8")

    # write clean summary
    md = ["# Competitive Landscape (Cleaned Signals)\n"]
    for p in clean_profiles:
        md.append(f"## {p['company']}\n")
        md.append(f"**Sources used:** {', '.join(p.get('sources_used', []))}\n")
        md.append(f"**Top terms (clean):** {', '.join(p.get('top_terms', [])[:15])}\n")
        md.append("**Pricing highlights:**")
        for s in (p.get("pricing_highlights", [])[:6]):
            md.append(f"- {' '.join(s.split())}")
        md.append("\n**Recent links (clean):**")
        for x in (p.get("recent_links", [])[:6]):
            md.append(f"- {x['title']} ({x['url']})")
        md.append("\n")
    OUT_CLEAN_SUMMARY.write_text("\n".join(md), encoding="utf-8")

    # write scorecard
    with OUT_SCORECARD.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=score_rows[0].keys())
        w.writeheader()
        w.writerows(sorted(score_rows, key=lambda r: r["total_score"], reverse=True))

    # winner report
    rows_sorted = sorted(score_rows, key=lambda r: r["total_score"], reverse=True)
    md2 = ["# Winner Report (Heuristic)\n",
           "This is an explainable heuristic based on cleaned signals: release links + enterprise/dev terms + pricing signal.\n",
           "## Ranking\n"]
    for r in rows_sorted:
        md2.append(f"- **{r['company']}** score={r['total_score']} "
                   f"(release={r['release_signal']}, enterprise={r['enterprise_signal']}, "
                   f"dev={r['developer_signal']}, pricing={r['pricing_signal']})")
    OUT_WINNER.write_text("\n".join(md2), encoding="utf-8")

    print("✅ Wrote:")
    print(" -", OUT_CLEAN_PROFILES)
    print(" -", OUT_CLEAN_SUMMARY)
    print(" -", OUT_SCORECARD)
    print(" -", OUT_WINNER)

if __name__ == "__main__":
    main()

from pathlib import Path
import json, re, csv
from collections import defaultdict, Counter

PAGES_JSONL = Path("data/structured/pages.jsonl")
OUT_DIR = Path("data/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def read_jsonl(path: Path):
    rows = []
    for i, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"⚠️ Skipping bad JSON line {i}: {e}")
    return rows

def clean_text(t: str) -> str:
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def price_lines(text: str, max_lines=12):
    # pull “price-like” snippets
    lines = re.split(r"[\\n\\r]+", text)
    hits = []
    for l in lines:
        s = l.strip()
        if not s:
            continue
        low = s.lower()
        if ("$" in s) or ("mtok" in low) or ("1m tokens" in low) or ("per month" in low) or ("per seat" in low):
            if s not in hits:
                hits.append(s)
        if len(hits) >= max_lines:
            break
    return hits

def top_terms(text: str, n=12):
    # super simple keywording (no ML required)
    words = re.findall(r"[A-Za-z][A-Za-z\\-]{2,}", text.lower())
    stop = set("""
        the a an and or to of in for on with from by as at into is are be this that we you your our
        pricing blog news product terms privacy cookie use api https www com
    """.split())
    words = [w for w in words if w not in stop and not w.isdigit()]
    c = Counter(words)
    return [w for w,_ in c.most_common(n)]

def extract_markdown_links(text: str, max_items=8):
    # if your scrapes include markdown-style links, grab them
    out = []
    for m in re.finditer(r"\[([^\]]+)\]\((https?://[^)]+)\)", text):
        title = clean_text(m.group(1))
        url = m.group(2).strip()
        if title and (title, url) not in out:
            out.append((title, url))
        if len(out) >= max_items:
            break
    return out

def main():
    if not PAGES_JSONL.exists():
        raise FileNotFoundError(f"Missing {PAGES_JSONL}. Run scripts/01_rebuild_pages_jsonl.py first.")

    pages = read_jsonl(PAGES_JSONL)
    print(f"Loaded {len(pages)} page records")

    # Filter out blocked pages (403/captcha/etc)
    ok_pages = [p for p in pages if not p.get("blocked", False)]
    blocked_pages = [p for p in pages if p.get("blocked", False)]

    print(f"✅ OK pages: {len(ok_pages)}")
    print(f"🚫 Blocked pages: {len(blocked_pages)}")
    for p in blocked_pages:
        print(f"  - {p.get('slug')}__{p.get('kind')} (blocked=True)")

    # Group by company
    grouped = defaultdict(list)
    for p in ok_pages:
        grouped[p.get("slug", p.get("company", "unknown"))].append(p)

    profiles = []
    matrix_rows = []

    for slug, items in grouped.items():
        combined_text = " ".join([p.get("text", "") for p in items])
        combined_text = clean_text(combined_text)

        kinds = sorted(set(p.get("kind","") for p in items))
        pricing_text = " ".join([p.get("text","") for p in items if p.get("kind") == "pricing"])
        news_text = " ".join([p.get("text","") for p in items if p.get("kind") in ("news_or_partnerships","blog")])

        prof = {
            "company": slug,
            "sources_used": kinds,
            "top_terms": top_terms(combined_text, 14),
            "pricing_highlights": price_lines(pricing_text, 10),
            "recent_links": [{"title":t, "url":u} for t,u in extract_markdown_links(news_text, 8)],
        }
        profiles.append(prof)

        matrix_rows.append({
            "company": slug,
            "sources_used": ",".join(kinds),
            "top_terms": ", ".join(prof["top_terms"][:10]),
            "pricing_highlights": " | ".join(prof["pricing_highlights"][:5]),
        })

    # Write outputs
    (OUT_DIR / "company_profiles.json").write_text(json.dumps(profiles, indent=2), encoding="utf-8")

    with (OUT_DIR / "competitive_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company","sources_used","top_terms","pricing_highlights"])
        w.writeheader()
        w.writerows(matrix_rows)

    # Markdown summary
    md = ["# Competitive Landscape (GTM + Positioning) – Structured Summary\n"]
    md.append(f"- Total pages: {len(pages)}")
    md.append(f"- Used pages (non-blocked): {len(ok_pages)}")
    md.append(f"- Blocked pages: {len(blocked_pages)}\n")

    for p in profiles:
        md.append(f"## {p['company']}\n")
        md.append(f"**Sources used:** {', '.join(p['sources_used'])}\n")
        md.append(f"**Top terms:** {', '.join(p['top_terms'])}\n")
        if p["pricing_highlights"]:
            md.append("**Pricing highlights:**\n")
            for line in p["pricing_highlights"][:6]:
                md.append(f"- {line}")
        if p["recent_links"]:
            md.append("\n**Recent links found:**\n")
            for link in p["recent_links"][:6]:
                md.append(f"- {link['title']} ({link['url']})")
        md.append("\n")

    (OUT_DIR / "summary.md").write_text("\n".join(md), encoding="utf-8")

    print(f"\n✅ Wrote outputs to: {OUT_DIR}/")
    print(f" - {OUT_DIR/'company_profiles.json'}")
    print(f" - {OUT_DIR/'competitive_matrix.csv'}")
    print(f" - {OUT_DIR/'summary.md'}")

if __name__ == "__main__":
    main()

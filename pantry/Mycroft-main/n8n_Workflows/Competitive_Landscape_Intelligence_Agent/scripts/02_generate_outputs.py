import json, re
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup

PAGES_JSONL = Path("data/structured/pages.jsonl")
RAW_DIR = Path("data/sample_raw")
OUT_DIR = Path("data/structured/outputs")

BLOCK_MARKERS = ("just a moment", "captcha", "verification successful", "403", "forbidden")

def is_blocked_text(t: str) -> bool:
    tl = (t or "").lower()
    return any(m in tl for m in BLOCK_MARKERS)

def read_jsonl(path: Path):
    rows = []
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows

def default_html_path(slug: str, kind: str) -> Path:
    return RAW_DIR / f"{slug}__{kind}.html"

def html_to_text(html: str):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    h1s = [h.get_text(" ", strip=True) for h in soup.find_all("h1")[:3]]
    h2s = [h.get_text(" ", strip=True) for h in soup.find_all("h2")[:8]]

    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{2,}", "\n", text)
    return title, h1s, h2s, text

def extract_pricing_signals(text: str):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    hits = []
    keywords = ("per month", "per year", "monthly", "annual", "free", "enterprise", "contact sales", "pricing", "$", "usd", "seat")
    for ln in lines:
        l = ln.lower()
        if any(k in l for k in keywords):
            # keep short-ish lines only
            if 20 <= len(ln) <= 180:
                hits.append(ln)
        if len(hits) >= 20:
            break
    return hits

def extract_gtm_themes(text: str):
    # simple keyword scoring (good enough for structured output)
    themes = {
        "Developer-first": ["api", "sdk", "docs", "developer", "integration"],
        "Enterprise/Security": ["enterprise", "security", "compliance", "soc 2", "sla", "governance"],
        "Partnerships/Ecosystem": ["partner", "partnership", "integrations", "ecosystem"],
        "Pricing/Packaging": ["pricing", "plans", "tiers", "subscription", "billing", "free"],
        "Product Capability": ["model", "reasoning", "context", "tool", "agent", "multimodal", "fine-tuning"]
    }
    tl = text.lower()
    scores = {k: sum(tl.count(w) for w in ws) for k, ws in themes.items()}
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [k for k, v in top if v > 0][:4]

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pages = read_jsonl(PAGES_JSONL)

    per_company = defaultdict(list)
    blocked_pages = []

    for rec in pages:
        slug = rec.get("slug")
        kind = rec.get("kind")
        company = rec.get("company")

        html_path = Path(rec.get("file_path") or rec.get("out_file") or default_html_path(slug, kind))

        if not html_path.exists():
            # fallback: sometimes files are under data/sample_raw/pages
            alt = Path("data/sample_raw/pages") / html_path.name
            if alt.exists():
                html_path = alt

        if not html_path.exists():
            rec["status"] = "missing_html"
            per_company[company].append(rec)
            continue

        html = html_path.read_text(errors="ignore")
        if is_blocked_text(html):
            rec["status"] = "blocked"
            blocked_pages.append({"company": company, "kind": kind, "path": str(html_path)})
        else:
            rec["status"] = "ok"

        title, h1s, h2s, text = html_to_text(html)

        rec["local_html"] = str(html_path)
        rec["title"] = title
        rec["h1"] = h1s
        rec["h2_top"] = h2s[:6]
        rec["gtm_themes"] = extract_gtm_themes(text)
        if kind == "pricing":
            rec["pricing_signals"] = extract_pricing_signals(text)

        per_company[company].append(rec)

    # Write JSON outputs
    (OUT_DIR / "pages_enriched.json").write_text(json.dumps(per_company, indent=2), encoding="utf-8")
    (OUT_DIR / "blocked_pages.json").write_text(json.dumps(blocked_pages, indent=2), encoding="utf-8")

    # Write Markdown per company
    for company, items in per_company.items():
        md = [f"# {company} — Competitive Signals\n"]
        for rec in items:
            md.append(f"## {rec.get('kind','unknown').upper()}")
            md.append(f"- Source URL: {rec.get('source_url') or rec.get('url')}")
            md.append(f"- Local file: {rec.get('local_html','(missing)')}")
            md.append(f"- Status: {rec.get('status')}")
            if rec.get("title"):
                md.append(f"- Title: {rec['title']}")
            if rec.get("gtm_themes"):
                md.append(f"- GTM themes: {', '.join(rec['gtm_themes'])}")
            if rec.get("pricing_signals"):
                md.append("\n**Pricing signals (snippets):**")
                for s in rec["pricing_signals"][:10]:
                    md.append(f"- {s}")
            if rec.get("h2_top"):
                md.append("\n**Top headings:**")
                for h in rec["h2_top"][:6]:
                    md.append(f"- {h}")
            md.append("\n---\n")
        (OUT_DIR / f"{company}_report.md").write_text("\n".join(md), encoding="utf-8")

    # Write one combined summary
    summary = ["# Competitive Landscape Summary (GTM + Positioning)\n"]
    for company in sorted(per_company.keys()):
        ok = sum(1 for r in per_company[company] if r.get("status") == "ok")
        blk = sum(1 for r in per_company[company] if r.get("status") == "blocked")
        miss = sum(1 for r in per_company[company] if r.get("status") == "missing_html")
        summary.append(f"## {company}")
        summary.append(f"- OK pages: {ok} | Blocked: {blk} | Missing HTML: {miss}")
        themes = defaultdict(int)
        for r in per_company[company]:
            for t in r.get("gtm_themes", []):
                themes[t] += 1
        if themes:
            top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:4]
            summary.append("- Recurring GTM themes: " + ", ".join([f"{k}({v})" for k, v in top_themes]))
        summary.append("")
    (OUT_DIR / "competitive_summary.md").write_text("\n".join(summary), encoding="utf-8")

    print(f"✅ Wrote outputs to: {OUT_DIR}")
    if blocked_pages:
        print(f"⚠️ Blocked pages: {len(blocked_pages)} (see blocked_pages.json)")

if __name__ == "__main__":
    main()

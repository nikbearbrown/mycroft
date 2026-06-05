import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

def is_blocked(text: str) -> bool:
    t = (text or "").lower()
    return any(x in t for x in [
        "just a moment", "captcha", "verification successful",
        "403", "forbidden", "access denied", "cloudflare"
    ])

def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def get_title_and_desc(html: str):
    soup = BeautifulSoup(html, "lxml")
    title = (soup.title.get_text(strip=True) if soup.title else "")
    desc = ""
    m = soup.find("meta", attrs={"name": "description"})
    if m and m.get("content"):
        desc = m["content"].strip()
    if not desc:
        og = soup.find("meta", attrs={"property": "og:description"})
        if og and og.get("content"):
            desc = og["content"].strip()
    return title, desc

def get_headings(html: str):
    soup = BeautifulSoup(html, "lxml")
    hs = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        txt = tag.get_text(" ", strip=True)
        if txt:
            hs.append(txt)
    # de-dupe while keeping order
    seen = set()
    out = []
    for h in hs:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out[:80]

def main():
    ROOT = Path(__file__).resolve().parents[1]
    RAW_DIR = ROOT / "data" / "sample_raw"
    OUT_DIR = ROOT / "data" / "structured"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH = OUT_DIR / "pages.jsonl"

    targets_path = ROOT / "targets.json"
    targets = json.loads(targets_path.read_text(encoding="utf-8")).get("targets", [])

    slug_to_company = {t.get("slug"): t.get("company") for t in targets}
    source_map = {t.get("slug"): t.get("sources", {}) for t in targets}

    html_files = sorted(RAW_DIR.glob("*.html"))
    records = []
    blocked_count = 0

    for p in html_files:
        name = p.stem  # e.g. openai__pricing
        if "__" in name:
            slug, kind = name.split("__", 1)
        else:
            slug, kind = name, "unknown"

        html = p.read_text(encoding="utf-8", errors="ignore")
        title, desc = get_title_and_desc(html)
        headings = get_headings(html)
        text = clean_text(html)

        blocked = is_blocked(text) or len(text) < 300
        if blocked:
            blocked_count += 1

        rec = {
            "company": slug_to_company.get(slug, slug),
            "slug": slug,
            "kind": kind,
            "source_url": source_map.get(slug, {}).get(kind, ""),
            "local_file": str(p),
            "title": title,
            "meta_description": desc,
            "headings": headings,
            "word_count": len(re.findall(r"\w+", text)),
            "blocked": blocked,
            "text": text,
        }
        records.append(rec)

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✅ Wrote {len(records)} records → {OUT_PATH}")
    print(f"⚠️ Blocked: {blocked_count}")

if __name__ == "__main__":
    main()

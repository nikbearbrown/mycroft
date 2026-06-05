import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

RAW_DIR = Path("data/sample_raw")
TARGETS_JSON = Path("targets.json")  # keep one canonical one in repo root
OUT_JSONL = Path("data/structured/pages.jsonl")
OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

BLOCK_PATTERNS = [
    "just a moment",
    "captcha",
    "verification successful",
    "cloudflare",
    "access denied",
    "403",
    "forbidden",
    "enable cookies",
]

def is_blocked(text: str) -> bool:
    t = (text or "").lower()
    return any(p in t for p in BLOCK_PATTERNS)

def extract_text(html: str):
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    # remove noise
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    headings = [h.get_text(" ", strip=True) for h in soup.find_all(re.compile("^h[1-3]$"))]
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return title, headings[:30], text

def infer_slug_kind(filename: str):
    # expects pattern: slug__kind.html
    m = re.match(r"(.+?)__([a-zA-Z0-9_]+)\.html?$", filename)
    if not m:
        return None, None
    return m.group(1), m.group(2)

def main():
    targets = json.loads(TARGETS_JSON.read_text())
    source_map = {}
    for t in targets.get("targets", []):
        slug = t["slug"]
        source_map[slug] = t.get("sources", {})

    records = []
    for p in sorted(RAW_DIR.glob("*.htm*")):
        slug, kind = infer_slug_kind(p.name)
        if not slug:
            continue

        html = p.read_text(errors="ignore")
        title, headings, text = extract_text(html)

        records.append({
            "company": slug,  # we’ll map to company name later if needed
            "slug": slug,
            "kind": kind,
            "source_url": source_map.get(slug, {}).get(kind, ""),
            "local_file": str(p),
            "title": title,
            "headings": headings,
            "word_count": len(re.findall(r"\w+", text)),
            "blocked": is_blocked(text),
            "text": text,
        })

    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✅ Wrote {len(records)} records → {OUT_JSONL}")
    blocked = [r for r in records if r["blocked"]]
    print(f"⚠️ Blocked: {len(blocked)}")

if __name__ == "__main__":
    main()

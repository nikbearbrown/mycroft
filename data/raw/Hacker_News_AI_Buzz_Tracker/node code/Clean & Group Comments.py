# n8n code node: Clean & Group Comments  (Week 9 — HTML clean, dedupe, group per entity)
import html, re
TAG_RE = re.compile(r"<[^>]+>")
MAX_COMMENT_CHARS = 500
COMMENT_CAP = 15

def clean_comment(raw):
    if not raw:
        return None
    text = TAG_RE.sub(" ", raw)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_COMMENT_CHARS] if text else None

def build(_items):
    by_entity = {}
    for it in _items:
        j = it["json"]
        if j.get("deleted") or j.get("dead"):
            continue
        c = clean_comment(j.get("text"))
        if not c:
            continue
        ent = j["entity"]
        bucket = by_entity.setdefault(ent, {"ticker": j["ticker"], "row": j["row"], "comments": [], "seen": set()})
        if c not in bucket["seen"]:
            bucket["seen"].add(c)
            bucket["comments"].append(c)
    out = []
    for ent, b in by_entity.items():
        out.append({"json": {"entity": ent, "ticker": b["ticker"], "row": b["row"],
                               "comments": b["comments"][:COMMENT_CAP],
                               "commentsAnalyzed": len(b["comments"][:COMMENT_CAP])}})
    return out


return build(_items)

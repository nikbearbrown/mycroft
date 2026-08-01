# n8n code node: Attach Narratives  (Week 7 — combine-by-position with the Groq response)
import json
THEMES = ["launch", "outage", "funding", "research", "controversy", "hiring"]
TONES  = ["bullish", "bearish", "neutral"]

def merge(_items):
    row = _items[0]["json"]["row"]
    narr = {}
    for it in _items:
        j = it["json"]
        ent = j.get("entity")
        try:
            content = j["choices"][0]["message"]["content"]
            o = json.loads(content)
            theme = o.get("theme") if o.get("theme") in THEMES else "research"
            tone  = o.get("tone")  if o.get("tone")  in TONES  else "neutral"
            narr[ent] = {"narrative": (o.get("narrative") or "").strip(), "theme": theme, "tone": tone}
        except Exception as ex:
            narr[ent] = {"narrative": None, "theme": None, "tone": None, "degraded": True, "reason": str(ex)}
    for e in row.get("leaderboard", []):
        e["narrative"] = narr.get(e.get("entity"))
    row["narratives"] = narr
    return [{"json": row}]


return merge(_items)

# n8n code node: Explode Entities  (Week 7 narrative — one Groq request body per entity)
THEMES = ["launch", "outage", "funding", "research", "controversy", "hiring"]
TONES  = ["bullish", "bearish", "neutral"]

def build(_items):
    row = _items[0]["json"]
    lb = row.get("leaderboard", [])
    out = []
    for e in lb:
        # Use the top-N stories for richer grounding; fall back to the single topStory.
        tops = e.get("topStories") or ([e["topStory"]] if e.get("topStory") else [])
        lines = []
        for i, s in enumerate(tops[:5], 1):
            t = (s.get("title") or "")[:200]
            lines.append(f"{i}. [{s.get('points', 0)} pts] {t}")
        stories = "\n".join(lines) if lines else "(no stories this window)"
        system = ("You are a technical-community analyst for an AI-sector attention "
            "tracker. Buzz measures ATTENTION, not price direction. Ground every "
            "statement in the provided titles; never invent facts. Reply with one JSON object only.")
        user = (f"Entity: {e.get('entity')} (ticker {e.get('ticker')})\n"
            f"Top Hacker News stories this window:\n{stories}\n\n"
            f'Return JSON with keys: "narrative" (<=70 words, grounded), '
            f'"theme" (one of {THEMES}), "tone" (one of {TONES}).')
        body = {"model": "llama-3.3-70b-versatile", "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        out.append({"json": {"entity": e.get("entity"), "row": row, "groqBody": body}})
    return out


return build(_items)

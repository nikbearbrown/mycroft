# n8n code node: Explode For Story Fetch  (Week 9 — one item per (entity, story))
def build(_items):
    row = _items[0]["json"]
    out = []
    for e in row.get("leaderboard", []):
        tops = e.get("topStories") or ([e["topStory"]] if e.get("topStory") else [])
        for s in tops[:3]:
            if s.get("objectID"):
                out.append({"json": {"entity": e.get("entity"), "ticker": e.get("ticker"),
                                       "row": row, "storyObjectID": s["objectID"]}})
    return out


return build(_items)
    
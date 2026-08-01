# n8n code node: Extract Comment IDs  (Week 9 — one item per (entity, comment id))
def build(_items):
    out = []
    for it in _items:
        j = it["json"]
        for kid in (j.get("kids") or [])[:15]:
            out.append({"json": {"entity": j["entity"], "ticker": j["ticker"],
                                   "row": j["row"], "commentID": kid}})
    return out


return build(_items)

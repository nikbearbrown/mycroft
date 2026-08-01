# n8n code node: Skip Sector Clustering  (Week 9 — False branch of "Has Usable Opinions?")
# Runs when zero entities produced a usable opinion this run. Writes an honest
# degraded sectorNarrative instead of calling the LLM, then feeds the same three
# terminal consumers (Save Snapshot, Code in Python, If).
def build(_items):
    row = _items[0]["json"]["row"]
    row["sectorNarrative"] = {
        "narrative": None,
        "crossEntityThemes": [],
        "degraded": True,
        "reason": "no non-degraded entity opinions this run",
    }
    return [{"json": row}]


return build(_items)

# n8n code node: Build Sector Prompt  (Week 9 — one cross-entity Groq body per run)
# Emits hasUsableOpinions=False (and NO groqBody) when every entity degraded, so
# the downstream "Has Usable Opinions?" If node can skip the LLM call entirely
# rather than letting the model fabricate a sector narrative from nothing.
# response_format is intentionally omitted (see Build Opinion Prompts note).
def build(_items):
    row = _items[0]["json"]
    opinions = row.get("community_opinions", {})
    lines = []
    for ent, op in opinions.items():
        # Cluster only robust opinions: skip degraded/empty AND low-confidence ones
        # (built on <3 comments) so a 1-2 comment opinion can't steer the sector
        # narrative. If that leaves nothing usable, hasUsableOpinions=False below.
        if not op or op.get("degraded") or not op.get("summary") or op.get("lowConfidence"):
            continue
        themes = ", ".join(op.get("themes") or [])
        lines.append(f"- {ent}: [{op.get('sentiment')}] {op['summary']} (themes: {themes})")

    if not lines:
        return [{"json": {"row": row, "hasUsableOpinions": False}}]

    block = "\n".join(lines)
    system = ("You are a technical-community analyst summarizing this week's AI-sector "
        "discussion across tracked entities. Ground every statement in the summaries "
        "given; never invent facts about entities not listed. Reply with a single valid "
        "JSON object only -- no markdown code fences, no text before or after the object.")
    user = (f"Per-entity Community Opinion summaries this window:\n{block}\n\n"
        'Return a JSON object with exactly these keys: "sectorNarrative" (2-4 sentences '
        'on cross-cutting themes/mood), "crossEntityThemes" (<=6 short strings).')
    body = {"model": "llama-3.3-70b-versatile", "temperature": 0.3, "max_tokens": 600,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    return [{"json": {"row": row, "groqBody": body, "hasUsableOpinions": True}}]


return build(_items)

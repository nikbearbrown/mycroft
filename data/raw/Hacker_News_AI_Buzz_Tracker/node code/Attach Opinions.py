# n8n code node: Attach Opinions  (Week 9 — parse per-entity Groq responses)
import json
import re
SENTIMENTS = ["positive", "negative", "mixed", "neutral"]

# An opinion built on very few comments is thin evidence — mirror the buzz-score
# sparse-entity floor (<3 stories) with a <3 comments confidence floor. NOTE: this
# only bounds THIN-DATA noise; it does NOT fix story->entity misattribution (an
# opinion can have 15 comments that are all about the wrong subject). That upstream
# relevance fix is Week 10 in plan.md.
OPINION_MIN_COMMENTS = 3

def extract_json_object(text):
    """Content is no longer guaranteed strict JSON (no response_format), so strip
    markdown fences and fall back to the outermost {...} span before parsing."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    if text.startswith("{"):
        return text
    start, end = text.find("{"), text.rfind("}https://www.youtube.com/watch?v=iX3-YZb1-S0")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return text[start:end + 1]

def build(_items):
    row = _items[0]["json"]["row"]
    opinions = {}
    for it in _items:
        j = it["json"]
        ent = j.get("entity")
        ca = j.get("commentsAnalyzed", 0)
        try:
            if "choices" not in j:
                raise RuntimeError(f"Groq error: {j.get('error') or j}")
            content = j["choices"][0]["message"]["content"]
            o = json.loads(extract_json_object(content))
            sentiment = o.get("sentiment") if o.get("sentiment") in SENTIMENTS else "neutral"
            opinions[ent] = {
                "summary": (o.get("summary") or "").strip(), "sentiment": sentiment,
                "themes": [str(t).strip() for t in (o.get("themes") or [])][:5],
                "notableOpinions": [str(q).strip() for q in (o.get("notableOpinions") or [])][:3],
                "commentsAnalyzed": ca,
                "lowConfidence": ca < OPINION_MIN_COMMENTS,
                "degraded": False,
            }
        except Exception as ex:
            opinions[ent] = {"summary": None, "sentiment": None, "themes": [], "notableOpinions": [],
                             "commentsAnalyzed": ca, "lowConfidence": True,
                             "degraded": True, "reason": str(ex)}
    # Entities with zero comments never reached this node — fill degraded here.
    for e in row.get("leaderboard", []):
        ent = e.get("entity")
        if ent not in opinions:
            opinions[ent] = {"summary": None, "sentiment": None, "themes": [],
                               "notableOpinions": [], "commentsAnalyzed": 0,
                               "lowConfidence": True, "degraded": True,
                               "reason": "no comments available"}
        e["communityOpinion"] = opinions[ent]
    row["community_opinions"] = opinions
    return [{"json": row}]


return build(_items)

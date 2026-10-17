# n8n code node: Get Metrics
from datetime import datetime, timezone


def parse_hit(hit):
    """Keep only the fields we need; drop _highlightResult / _tags noise."""
    return {
        "title": hit.get("title"),
        "url": hit.get("url"),
        "points": hit.get("points") or 0,
        "num_comments": hit.get("num_comments") or 0,
        "created_at_i": hit.get("created_at_i"),
        "objectID": hit.get("objectID"),
    }


def run_date_from_since(since):
    """Window-start date as YYYY-MM-DD (UTC). Falls back to None if unset."""
    if since is None:
        return None
    return datetime.fromtimestamp(since, tz=timezone.utc).strftime("%Y-%m-%d")


# --- Week 10 story->entity relevance (mirrors story_relevance.py; see that file
# and tests/test_story_relevance.py for the rationale and the Bento fixture) ---
def title_matches(title, terms):
    """True if any of the entity's query terms is in the story TITLE (ci)."""
    if not title:
        return False
    t = title.lower()
    for term in terms or []:
        term = (term or "").strip().lower()
        if term and term in t:
            return True
    return False


def func(_items):
    # Per-execution accumulators (local, so nothing leaks between entity runs).
    hits_by_id = {}     # objectID -> parsed_hit  (dedupe: same story across terms counts once)
    entity = None       # canonical entity name (same across all input items)
    since = None        # smallest sinceUnix seen across this entity's terms
    query_terms = []    # this entity's query terms, collected from the fanned-out items
    seen_terms = set()
    meta = {            # per-entity config, captured from the first item that has it
        "ticker": None,
        "frontPagePoints": 100,
        "breakoutThreshold": 70,
    }
    meta_captured = False

    for item in _items:
        try:
            data = item.get("json", {})

            # All items belong to the same entity; capture the name + meta once.
            if entity is None and data.get("entity"):
                entity = data.get("entity")
            if not meta_captured and data.get("entity"):
                meta = {
                    "ticker": data.get("ticker"),
                    "frontPagePoints": data.get("frontPagePoints", 100),
                    "breakoutThreshold": data.get("breakoutThreshold", 70),
                }
                meta_captured = True

            # Collect the query term this item searched on (threaded via Merge1),
            # so top-story selection can require a title match (Week 10).
            term = data.get("term")
            if term and term not in seen_terms:
                seen_terms.add(term)
                query_terms.append(term)

            term_since = data.get("sinceUnix")
            if term_since is not None:
                since = term_since if since is None else min(since, term_since)

            for hit in (data.get("hits") or []):
                rec = parse_hit(hit)
                oid = rec["objectID"]
                if oid is None:
                    continue
                hits_by_id[oid] = rec
        except Exception:
            # Empty / malformed response for one term: skip the term, keep going.
            continue

    fp_points = meta["frontPagePoints"]
    hits = list(hits_by_id.values())

    # Buzz-score metrics are computed over ALL deduped hits (unchanged) — the
    # Week 10 relevance filter applies only to top-story SELECTION below.
    story_count = len(hits)
    total_points = sum(h["points"] for h in hits)
    total_comments = sum(h["num_comments"] for h in hits)
    front_page_count = sum(1 for h in hits if h["points"] >= fp_points)

    # Top-3 stories by points, RELEVANCE-FILTERED (Week 10): a story qualifies as
    # a top story only if a query term appears in its title, so the narrative and
    # the Community Opinion comment fetch target stories actually about the entity.
    # Metrics stay over all hits; this only governs narrative/opinion attribution.
    # If query_terms is empty (terms didn't thread through), fall back to points
    # ranking so we degrade to old behavior rather than emptying every entity.
    ranked = sorted(hits, key=lambda h: h["points"], reverse=True)
    if query_terms:
        relevant = [h for h in ranked if title_matches(h["title"], query_terms)]
        relevance_filtered = True
    else:
        relevant = ranked
        relevance_filtered = False

    top_story = None
    top_stories = []
    for h in relevant[:3]:
        top_stories.append({
            "title": h["title"], "url": h["url"], "points": h["points"],
            "num_comments": h["num_comments"], "objectID": h["objectID"],
            "permalink": f"https://news.ycombinator.com/item?id={h['objectID']}",
            "titleMatch": True,
        })
    if top_stories:
        top_story = top_stories[0]

    return {
        "json": {
            "entity": entity,
            "ticker": meta["ticker"],
            "breakoutThreshold": meta["breakoutThreshold"],
            "runDate": run_date_from_since(since),
            "rawMetrics": {
                "storyCount": story_count,        # = deduped hit count (all hits)
                "totalPoints": total_points,
                "totalComments": total_comments,
                "frontPageCount": front_page_count,
            },
            "topStory": top_story,
            "topStories": top_stories,
            "lowConfidence": story_count < 3,      # sparse-entity floor (plan.md)
            # Week 10 attribution audit fields:
            "relevanceFiltered": relevance_filtered,   # False = terms missing, fell back
            "storiesConsidered": story_count,          # all deduped hits
            "relevantStories": len(relevant),          # hits with a title match
        }
    }


return func(_items)

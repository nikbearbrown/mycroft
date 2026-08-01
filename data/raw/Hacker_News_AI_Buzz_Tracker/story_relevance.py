"""
Story -> entity relevance (Week 10, plan.md).

Week 9 surfaced that an entity's "top story" — chosen purely by Hacker News
points — can be a story that only *incidentally* mentions the entity in its body.
The canonical case: a Show HN post for "Bento" (a slide tool) that merely
name-dropped Claude and ChatGPT out-ranked stories actually about OpenAI and
Anthropic, so their Community Opinions summarized comments about a presentation
tool. Root cause is upstream attribution (Algolia phrase-matches anywhere in the
story, then we rank by points), not the analyzer.

The fix implemented here: a story is *relevant* to an entity only if one of the
entity's query terms appears in the story TITLE (not just the body). Top-story
selection — which drives the LLM narrative and the Community Opinion comment
fetch — is restricted to relevant stories. If none are relevant, the entity has
no top story and its narrative/opinion degrade cleanly, rather than confidently
describing the wrong subject (degrade-over-wrong).

Scope boundary (deliberate): this filters only *top-story selection*. The Buzz
Score's volume/engagement/front-page metrics are still computed over all deduped
hits, because those weights are held fixed through Phase 1 for comparability and
an incidental mention is still a (weak) attention signal. Only *what we claim
people are saying* is relevance-gated.

Known tradeoff: title matching is a case-insensitive phrase-substring test, so a
multi-word term ("Microsoft Copilot") only matches when that exact phrase is in
the title. A real story titled "Microsoft ships a Copilot update" would be
filtered out and the entity would degrade. That is the conservative direction
(degrade, don't misattribute); term lists can be tuned in the watchlist.

This module is the testable reference; node code/Get Metrics.py mirrors
`title_matches` / `select_top_stories` inline (n8n code nodes can't import).
"""


def title_matches(title, terms):
    """True if any query term appears (case-insensitive) in the story title.

    `title` may be None (some HN items lack a title); `terms` is the list of the
    entity's raw query terms. Empty/blank terms are ignored so they can't match
    everything.
    """
    if not title:
        return False
    t = title.lower()
    for term in terms or []:
        term = (term or "").strip().lower()
        if term and term in t:
            return True
    return False


def select_top_stories(hits, terms, n=3):
    """Return the top `n` *relevant* stories for an entity, highest points first.

    A hit is relevant when its title matches one of the entity's terms. Hits are
    ranked by points and then filtered, so ordering among relevant stories is
    preserved. Returns [] when nothing is relevant (caller degrades gracefully).

    Guard: if `terms` is empty/missing (query terms failed to thread through),
    relevance can't be judged, so fall back to points-ranked top-N unfiltered
    rather than degrading every entity to empty.
    """
    ranked = sorted(hits, key=lambda h: h.get("points") or 0, reverse=True)
    if not terms:
        return ranked[:n]
    relevant = [h for h in ranked if title_matches(h.get("title"), terms)]
    return relevant[:n]

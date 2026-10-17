# Story → entity relevance fix (Week 10)

## The problem (found in Week 9)

An entity's "top story" was chosen purely by Hacker News points. Because the
Algolia search phrase-matches a query term *anywhere* in a story (title, body,
or URL), a popular story that only *incidentally* mentions an entity could become
that entity's top story.

Canonical case: a Show HN post — **"Bento — An entire PowerPoint in one HTML
file"** (`item?id=49008211`, 1018 points) — name-dropped Claude and ChatGPT in
its body. It out-pointed every real story and became the top story for **both**
OpenAI and Anthropic, so their Community Opinions summarized comments about a
slide tool, and the sector narrative inherited the false claim that "OpenAI and
Anthropic were praised for their presentation software."

Root cause is **upstream attribution** (points-ranked, matches anywhere), not the
analyzer — the analyzer ran correctly on the wrong input. The Week 9 interim
mitigation (`lowConfidence` for opinions built on <3 comments, excluded from
sector clustering) bounds thin-data noise only; Bento had 15 comments, so it was
never caught. This week fixes the cause.

## The fix

A story is *relevant* to an entity only if one of the entity's query terms
appears in the **story title** (case-insensitive), not merely somewhere in the
body. Top-story selection — which drives the LLM narrative and the Community
Opinion comment fetch — is restricted to relevant stories.

- If relevant stories exist → top 3 by points, each tagged `titleMatch: true`.
- If none are relevant → no top story; the entity's narrative and Community
  Opinion **degrade cleanly** rather than confidently describing the wrong
  subject (*degrade-over-wrong*).

### Where it lives

- `node code/Get Metrics.py` — inline `title_matches()` + relevance-filtered
  top-story selection (n8n code nodes can't import).
- `story_relevance.py` — the testable reference (`title_matches`,
  `select_top_stories`), mirrored by the node.
- `tests/test_story_relevance.py` — 8 fixtures, including the real Bento case
  asserting it is **not** selected despite having the most points.

### Scope boundary (deliberate)

The filter governs **top-story selection only**. The Buzz Score's
volume/engagement/front-page metrics are still computed over *all* deduped hits,
because (a) those weights are held fixed through Phase 1 for comparability, and
(b) an incidental mention is still a weak attention signal. Only *what we claim
the community is saying* is relevance-gated, not *how much attention* an entity
gets.

### Audit fields added to each entity's metrics

| Field | Meaning |
|---|---|
| `relevanceFiltered` | `true` normally; `false` means query terms didn't thread through and it fell back to points ranking |
| `storiesConsidered` | count of all deduped hits |
| `relevantStories` | count of hits with a title match |

These make it visible, per run, how aggressively the filter is cutting.

## Known tradeoff

Title matching is a case-insensitive phrase-substring test, so a multi-word term
("Microsoft Copilot") only matches when that exact phrase is in the title. A real
story titled *"Microsoft ships a Copilot update"* would be filtered out and the
entity would degrade. This is the conservative direction (degrade, don't
misattribute). Two levers if an entity over-degrades:

1. Tune its `queryTerms` in the watchlist to include the distinctive single token
   that actually appears in titles (e.g. add `"Copilot"`).
2. A future refinement could accept a title match on the distinctive token of a
   multi-word term while still rejecting generic tokens — not done here to avoid
   reintroducing noise.

## Re-verification (human, live)

Because this changes `Get Metrics`, it must be pasted into the live n8n node and
a full run re-verified against live data. Acceptance check (plan.md Week 10):
**an entity's Community Opinion should discuss that entity, not a co-mentioned
third party.** Concretely, re-run and confirm the Bento post no longer appears as
OpenAI's or Anthropic's top story, and that `relevantStories` is reported per
entity.

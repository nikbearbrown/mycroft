# Community Opinion Analyzer — Design (Week 9)

**Date:** 2026-07-22 · **Author:** Om Mali · **Reference implementation:** `community_opinion.py`

This layer adds a **third, comment-grounded** signal, distinct from the other two:
- Weeks 2–4: the deterministic Buzz Score — *how much* attention.
- Week 7: the title-level narrative/theme/tone — *what the headlines are about*.
- Week 9 (this layer): the Community Opinion analyzer — *what commenters actually said*,
  read from verbatim HN comment text rather than story titles.

---

## 1. Comment-fetch strategy

The Algolia search API (used for stories) does not return comment text. Comment bodies
live only on the **HN Firebase item API** (`https://hacker-news.firebaseio.com/v0/item/{id}.json`),
which is unauthenticated, free, and returns one JSON object per item (story or comment).

Fetch shape, per plan.md:
1. Take an entity's **top 3 stories** by points (`community_opinion.TOP_N_STORIES = 3`),
   reusing `llm_narrative.fetch_top_stories()` (Algolia, already deduped/ranked, `objectID`
   present per hit).
2. For each story, `GET` the story item → read its `kids` array (top-level comment IDs, in
   the order Firebase returns them — no separate ranking step).
3. `GET` each kid item, up to the **top 10 per story** (`TOP_N_COMMENTS_PER_STORY = 10`),
   fetching a couple extra per story to absorb `deleted`/`dead` items without falling short.
4. Cap: **3 stories × 10 comments = ~30 comments per entity**, matching plan.md's bound on
   API calls and token use. This is `~12 entities × ~3 story calls × ~10 comment calls`
   worst case per run — bounded and sequential-safe (no pagination needed, unlike Algolia).

**Only top-level comments are fetched** (no reply-tree recursion) — plan.md scopes this to
top-level opinion, not full-thread sentiment, keeping the fetch bounded and the LLM input
a flat list rather than a nested structure it would have to reason about.

## 2. Cleaning step

HN comment `text` is raw HTML (`<p>`, `<i>`, `&#x27;`, `&gt;`, etc). `clean_comment()`:
1. Strips tags with a regex (`<[^>]+>` → space) — a full HTML parser is unnecessary for
   comment bodies, which don't nest complex markup.
2. Decodes entities via stdlib `html.unescape` (no new dependency).
3. Collapses whitespace and trims.
4. Truncates to **500 chars** (`MAX_COMMENT_CHARS`) — bounds token cost per comment; long
   comments are usually restating points already covered by shorter ones in the same thread.
5. Drops empties.

`clean_and_dedupe()` also drops **exact-duplicate** cleaned comments (some threads have
copy-pasted boilerplate replies, e.g. bot-like "this" replies) before they're handed to
the LLM, so one repeated comment doesn't skew the sentiment read.

Skipping `deleted`/`dead` comments happens earlier, in `fetch_comments_for_story()`,
since those items either have no `text` at all or one that shouldn't be attributed to
a live commenter.

## 3. LLM analyzer — inputs, outputs, prompt

**Input per entity:** entity name, ticker (optional), and the cleaned/deduped comment list
(<=30 strings).

**Output per entity** (structured JSON):
```json
{
  "summary": "2-3 sentences, grounded in the comments",
  "sentiment": "positive | negative | mixed | neutral",
  "themes": ["<=5 recurring topics/concerns"],
  "notableOpinions": ["<=3 verbatim excerpts"],
  "enumCoerced": false,
  "entity": "...", "ticker": "...",
  "provider": "groq", "model": "llama-3.3-70b-versatile",
  "degraded": false,
  "storiesAnalyzed": 3, "commentsAnalyzed": 24
}
```
- **System message**: frames the role, states this is comment-grounded (distinct from
  headline narrative), and demands grounding + JSON-only output — same discipline as
  Week 7's narrative prompt.
- **User message**: numbered comment list, then the exact output keys and the controlled
  sentiment vocabulary inline.
- **`notableOpinions`** are explicitly requested **verbatim** (not paraphrased) — these are
  quotes, so inventing or rewording one would misattribute words to a real commenter; the
  prompt says so directly and the parser does not further edit the strings it returns.
- **`temperature=0.3`**, same as Week 7, for repeatable, non-embellished output.
- Reuses the same provider plumbing as `llm_narrative.py` (Groq JSON mode / Claude with
  defensive `{...}` extraction) — no new "which LLM" decision needed; see
  `docs/llm_narrative_design.md` §1 for that reasoning.

## 4. Sector theme clustering

`cluster_sector_themes()` takes the run's per-entity (non-degraded) opinions and asks the
LLM for one **cross-entity sector narrative of the week** plus a short list of themes that
recur across more than one entity. This is a **second, separate LLM call per run** (not
per entity) — it reads only the already-generated per-entity summaries, not raw comments,
so it stays cheap (~1 call, small input) regardless of watchlist size.

Output:
```json
{
  "sectorNarrative": "2-4 sentences on cross-cutting themes/mood this week",
  "crossEntityThemes": ["<=6 shared themes"],
  "provider": "groq", "model": "...", "degraded": false, "entitiesClustered": 2
}
```

## 5. Graceful degradation (plan.md requirement)

Never crashes the run — the Buzz Score, Week-7 narrative, and digest must ship regardless:

| Situation | Behavior |
|---|---|
| Entity has zero comments across its top stories (sparse/comment-less stories) | `degraded=true`, `summary=null`, `reason="no comments available..."`, `storiesAnalyzed`/`commentsAnalyzed` still recorded (both may be 0) |
| No `GROQ_API_KEY` and no `ANTHROPIC_API_KEY` | `degraded=true`, `reason="no LLM key set..."` |
| API error / timeout / bad request | Caught → `degraded=true` with the exception summary |
| Model returns non-JSON / empty summary | `ValueError` caught → `degraded=true` |
| Model returns an off-vocabulary sentiment | Snapped to `"neutral"`, flagged `enumCoerced=true` (SNICKERDOODLE P3 — a judgment about a judgment, surfaced not hidden) |
| Sector clustering: no non-degraded entity opinions this run | `degraded=true` sector record, `sectorNarrative=null` |
| A single HN item fetch (story or comment) fails or 404s | Silently skipped (`fetch_item` returns `None`) — one dead link must not fail the entity |

Verified (2026-07-22): fixture unit tests for HTML-cleaning/dedup/parsing (`tests/test_community_opinion.py`,
12/12 passing, no network) plus a live smoke test — `--demo` (offline comment fixture, real Groq
key present in this environment) exercised the true LLM call path and degrade path (a live 400
from the API was caught and returned as a clean `degraded=true` record, not a crash), and
`--sector --demo` produced a real clustered sector narrative from two fixture entity opinions.

## 5a. Known limitations (found during the first live n8n run, 2026-07-22)

**Story–entity misattribution (upstream; not a Week 9 bug).** The comment fetch targets each
entity's *top stories by points*. When a high-scoring story only *incidentally* mentions the
entity, the resulting Community Opinion is about the wrong subject. Observed in the first full run:
a "Show HN: Bento" (a single-file presentation tool that name-drops ChatGPT and Claude) was the #1
story for **both OpenAI and Anthropic**, so both entities' opinions summarized comments praising an
unrelated presentation tool, and the sector narrative inherited the false claim that "OpenAI and
Anthropic were praised for their presentation software." The analyzer itself behaved correctly — it
faithfully summarized the comments it was given and did not invent OpenAI-specific claims — but the
comments were misattributed upstream. This is the **story→entity relevance** problem (Algolia
phrase-matching an incidental mention), tracked as a **Week 10** fix in `plan.md`, not something to
patch inside the opinion analyzer.

**Interim mitigation shipped in Week 9 (bounds thin data only).** `Attach Opinions` now flags any
opinion built on fewer than 3 comments (`OPINION_MIN_COMMENTS = 3`) as `"lowConfidence": true`, and
`Build Sector Prompt` excludes low-confidence opinions from the sector clustering so a 1–2 comment
opinion cannot steer the sector narrative. This addresses **thin-data noise** (e.g. an NVIDIA
opinion built on a single tangential comment), but it does **not** fix misattribution — a
15-comment opinion about the wrong subject still passes the confidence floor. Do not read
`lowConfidence: false` as "correctly attributed"; it only means "enough comments to summarize."

## 6. Using the reference implementation

```bash
python community_opinion.py --demo                    # offline comment fixture, no network for comments
python community_opinion.py --entity "NVIDIA"          # live HN fetch (stories + comments) + Groq
python community_opinion.py --entity "OpenAI" --provider claude   # needs ANTHROPIC_API_KEY
python community_opinion.py --sector --demo            # sector-clustering demo, two fixture entities
python tests/test_community_opinion.py                 # fixture tests, no network
```
No new dependencies — `requests`, `python-dotenv`, and stdlib `html`/`re`, already available.

## 7. Database migration — **your step to apply**

`DATABASE_SETUP.md`'s schema already documents `community_opinions jsonb` on `hn_buzz_runs`
(added retroactively to that doc alongside the Week-4 table). The **live** table predates
this column (confirmed by the dashboard's `column hn_buzz_runs.community_opinions does not
exist` error during Week 8 wiring). Apply once, in the Supabase SQL editor:

```sql
alter table hn_buzz_runs add column if not exists community_opinions jsonb;
```

This is additive and backward-compatible — existing rows get `null` in the new column,
and the Week 8 dashboard's `.select()` (which currently omits this column) can add it back
once this migration has run and the n8n workflow is populating it.

## 8. n8n workflow integration — **steps for you to apply and verify**

> Based on reading the actual `Hacker News AI Tracker.json` (not a guess): your workflow
> already has the Week 7 branch wired as `Build Run Row → Explode Entities → HTTP Request1
> (Groq, credential type `groqApi`) → Merge3 (combine-by-position) → Attach Narratives →
> {Code in Python, If, Save Snapshot}`. Reuse that exact pattern three more times below —
> it's already proven working in your instance. n8n Code nodes still have no network access,
> so every HTTP call below is its own **HTTP Request** node; but note n8n runs a node once
> **per input item automatically** — you do NOT need `Split In Batches` just to call the
> same HTTP node for each entity/story/comment, only Code nodes to explode/group items.

**Step A — no new credential.** Your `HTTP Request1` node uses
`authentication: predefinedCredentialType`, `nodeCredentialType: groqApi` — a built-in Groq
credential, not manual Header Auth. Reuse that same credential on every new Groq HTTP node
below (select it in the node's Credential dropdown).

**Step B — capture more than one story per entity (small edit to `Get Metrics`).**
Today `Get Metrics` (your `metric_generation.py` port) only keeps a single `topStory`.
`Explode Entities` already defensively checks for `topStories` first (`e.get("topStories")
or ([e["topStory"]] ...)`) — so add the plural field and both Week 7 and Week 9 benefit.
In `Get Metrics`, right after `top_story = ...` is built, add:
```python
    top_stories = None
    if hits:
        ranked = sorted(hits, key=lambda h: h["points"], reverse=True)[:3]
        top_stories = [
            {"title": h["title"], "url": h["url"], "points": h["points"],
             "num_comments": h["num_comments"], "objectID": h["objectID"]}
            for h in ranked
        ]
```
and add `"topStories": top_stories,` to the returned `json` dict (next to `"topStory"`).

**Step C — new node chain, inserted between `Attach Narratives` and its three consumers.**
Today: `Attach Narratives → {Code in Python, If, Save Snapshot}`. New flow (rewire
`Attach Narratives`'s output to point at `Explode For Story Fetch` below; the *last* new
node, `Attach Sector Narrative`, then points at the original three consumers):

1. **`Explode For Story Fetch`** (Code, Python) — one item **per (entity, story)** pair
   (flattens, so no Code-node loop is needed downstream — n8n's HTTP node just runs once
   per item):
   ```python
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
   ```
2. **`Fetch Story Item`** (HTTP Request) — **GET**
   `https://hacker-news.firebaseio.com/v0/item/{{ $json.storyObjectID }}.json`. No
   credential needed (public API). Turn on **Continue On Fail** (a 404/removed story must
   not kill the run). Runs once per item from step 1 automatically.
3. **`Merge Story Kids`** (Merge) — **Mode = Combine**, **Combine By = Combine by Position**.
   Input 1 ← `Explode For Story Fetch` (carries `entity`/`ticker`/`row`/`storyObjectID`).
   Input 2 ← `Fetch Story Item` (carries `kids`). Same position-combine pattern (and the
   same "silent misalignment if an item gets dropped/reordered" risk) as Week 7's
   `Merge3` — keep **Continue On Fail** on upstream so a failed fetch still emits a
   same-slot item instead of collapsing the list.
4. **`Extract Comment IDs`** (Code, Python) — flattens **per (entity, story, comment)**,
   fetching a few extra IDs per story to survive dead/deleted/no-text comments (mirrors
   `fetch_comments_for_story`'s `top_n * 2` cushion in `community_opinion.py`, fixed here
   at 15 since n8n can't early-stop a fan-out the way a Python loop can):
   ```python
   def build(_items):
       out = []
       for it in _items:
           j = it["json"]
           for kid in (j.get("kids") or [])[:15]:
               out.append({"json": {"entity": j["entity"], "ticker": j["ticker"],
                                      "row": j["row"], "commentID": kid}})
       return out
   return build(_items)
   ```
5. **`Fetch Comment Item`** (HTTP Request) — **GET**
   `https://hacker-news.firebaseio.com/v0/item/{{ $json.commentID }}.json`, **Continue On
   Fail** on. Runs per item automatically.
6. **`Merge Comment Text`** (Merge, **Combine by Position**) — Input 1 ←
   `Extract Comment IDs` (`entity`/`ticker`/`row`/`commentID`), Input 2 ←
   `Fetch Comment Item` (`text`/`deleted`/`dead`).
7. **`Clean & Group Comments`** (Code, Python) — this is the one place to **port
   `clean_comment()`/`clean_and_dedupe()` from `community_opinion.py` verbatim** (pure
   `re`/`html` string processing, no `requests` — safe in the sandboxed Code node). Groups
   the flat per-comment items back up to **one item per entity**, applying the same
   ~30-comments-per-entity cap and skipping entities with zero usable comments (those are
   simply absent from this node's output — handled as degraded in step 10):
   ```python
   import html, re
   TAG_RE = re.compile(r"<[^>]+>")
   MAX_COMMENT_CHARS = 500

   def clean_comment(raw):
       if not raw:
           return None
       text = TAG_RE.sub(" ", raw)
       text = html.unescape(text)
       text = re.sub(r"\s+", " ", text).strip()
       return text[:MAX_COMMENT_CHARS] if text else None

   def build(_items):
       by_entity = {}
       for it in _items:
           j = it["json"]
           if j.get("deleted") or j.get("dead"):
               continue
           c = clean_comment(j.get("text"))
           if not c:
               continue
           ent = j["entity"]
           bucket = by_entity.setdefault(ent, {"ticker": j["ticker"], "row": j["row"],
                                                 "comments": [], "seen": set()})
           if c not in bucket["seen"]:
               bucket["seen"].add(c)
               bucket["comments"].append(c)
       out = []
       for ent, b in by_entity.items():
           out.append({"json": {"entity": ent, "ticker": b["ticker"], "row": b["row"],
                                  "comments": b["comments"][:30],
                                  "commentsAnalyzed": len(b["comments"][:30])}})
       return out
   return build(_items)
   ```
8. **`Build Opinion Prompts`** (Code, Python) — port `build_messages()` from
   `community_opinion.py`, one Groq request body per entity item from step 7:
   ```python
   SENTIMENTS = ["positive", "negative", "mixed", "neutral"]

   def build(_items):
       out = []
       for it in _items:
           j = it["json"]
           lines = [f"{i}. {c}" for i, c in enumerate(j["comments"], 1)]
           block = "\n".join(lines) if lines else "(no comments)"
           system = ("You are a technical-community analyst for an AI-sector attention "
               "tracker. You read verbatim Hacker News comment text about one entity and "
               "summarize the community's OPINION, grounded only in what commenters wrote. "
               "Never invent a fact, quote, or event not present in the comments. Reply "
               "with a single JSON object only.")
           user = (f"Entity: {j['entity']} (ticker {j.get('ticker')})\n"
               f"Top-level Hacker News comments on this entity's top stories:\n{block}\n\n"
               'Return JSON with keys: "summary" (2-3 sentences, grounded), '
               f'"sentiment" (one of {SENTIMENTS}), "themes" (<=5 short strings), '
               '"notableOpinions" (<=3 VERBATIM excerpts from the comments above).')
           body = {"model": "llama-3.3-70b-versatile", "temperature": 0.3,
               "response_format": {"type": "json_object"},
               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
           out.append({"json": {"entity": j["entity"], "row": j["row"], "groqBody": body,
                                  "commentsAnalyzed": j["commentsAnalyzed"]}})
       return out
   return build(_items)
   ```
9. **`Community Opinion (Groq)`** (HTTP Request) — identical config to `HTTP Request1`:
   **POST** `https://api.groq.com/openai/v1/chat/completions`, Authentication =
   **Predefined Credential Type → Groq API** (your existing credential), **Send Body** =
   On, **Body Content Type** = JSON, **Specify Body** = "Using JSON", JSON field =
   `{{ $json.groqBody }}`. Turn on **Continue On Fail**.
10. **`Merge Opinions`** (Merge, **Combine by Position**) — Input 1 ← `Build Opinion
    Prompts` (`entity`/`row`/`commentsAnalyzed`), Input 2 ← `Community Opinion (Groq)`
    (`choices`).
11. **`Attach Opinions`** (Code, Python) — parses each Groq response, coerces the
    sentiment enum, **and fills in a degraded record for every entity that never made it
    this far** (zero comments at step 7) by reading the full `row.leaderboard` — this is
    the important correctness step, since steps 7-10 silently drop comment-less entities:
    ```python
    import json
    SENTIMENTS = ["positive", "negative", "mixed", "neutral"]

    def build(_items):
        row = _items[0]["json"]["row"]
        opinions = {}
        for it in _items:
            j = it["json"]; ent = j.get("entity")
            try:
                content = j["choices"][0]["message"]["content"]
                o = json.loads(content)
                sentiment = o.get("sentiment") if o.get("sentiment") in SENTIMENTS else "neutral"
                opinions[ent] = {
                    "summary": (o.get("summary") or "").strip(), "sentiment": sentiment,
                    "themes": (o.get("themes") or [])[:5],
                    "notableOpinions": (o.get("notableOpinions") or [])[:3],
                    "commentsAnalyzed": j.get("commentsAnalyzed", 0), "degraded": False,
                }
            except Exception as ex:
                opinions[ent] = {"summary": None, "sentiment": None, "themes": [],
                                   "notableOpinions": [], "degraded": True, "reason": str(ex)}
        # Entities with zero comments never reached this node — fill degraded here.
        for e in row.get("leaderboard", []):
            ent = e.get("entity")
            if ent not in opinions:
                opinions[ent] = {"summary": None, "sentiment": None, "themes": [],
                                   "notableOpinions": [], "commentsAnalyzed": 0,
                                   "degraded": True, "reason": "no comments available"}
            e["communityOpinion"] = opinions[ent]
        row["community_opinions"] = opinions
        return [{"json": row}]
    return build(_items)
    ```
12. **`Build Sector Prompt`** (Code, Python) — **one item, not per-entity**: port
    `build_sector_messages()`, reading `row["community_opinions"]` for non-degraded entries:
    ```python
    def build(_items):
        row = _items[0]["json"]
        opinions = row.get("community_opinions", {})
        lines = []
        for ent, op in opinions.items():
            if not op or op.get("degraded") or not op.get("summary"):
                continue
            themes = ", ".join(op.get("themes") or [])
            lines.append(f"- {ent}: [{op.get('sentiment')}] {op['summary']} (themes: {themes})")
        block = "\n".join(lines) if lines else "(no non-degraded entity opinions this run)"
        system = ("You are a technical-community analyst summarizing this week's AI-sector "
            "discussion across tracked entities. Ground every statement in the summaries "
            "given; never invent facts about entities not listed. Reply with a single JSON "
            "object only.")
        user = (f"Per-entity Community Opinion summaries this window:\n{block}\n\n"
            'Return JSON with keys: "sectorNarrative" (2-4 sentences on cross-cutting '
            'themes/mood), "crossEntityThemes" (<=6 short strings).')
        body = {"model": "llama-3.3-70b-versatile", "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        return [{"json": {"row": row, "groqBody": body}}]
    return build(_items)
    ```
13. **`Cluster Sector Themes (Groq)`** (HTTP Request) — same config as node 9 (one call
    this time, since step 12 emits a single item).
14. **`Merge Sector Response`** (Merge, **Combine by Position**) — Input 1 ← `Build Sector
    Prompt` (`row`), Input 2 ← `Cluster Sector Themes (Groq)` (`choices`).
15. **`Attach Sector Narrative`** (Code, Python) — final node in the chain; wire its
    output to the **original three consumers** (`Code in Python`, `If`, `Save Snapshot`):
    ```python
    import json

    def build(_items):
        row = _items[0]["json"]["row"]
        try:
            content = _items[0]["json"]["choices"][0]["message"]["content"]
            o = json.loads(content)
            row["sectorNarrative"] = {"narrative": (o.get("sectorNarrative") or "").strip(),
                                        "crossEntityThemes": (o.get("crossEntityThemes") or [])[:6],
                                        "degraded": False}
        except Exception as ex:
            row["sectorNarrative"] = {"narrative": None, "crossEntityThemes": [],
                                        "degraded": True, "reason": str(ex)}
        return [{"json": row}]
    return build(_items)
    ```

**Step D — persist it.** In **`Save Snapshot`**, change:
```sql
INSERT INTO hn_buzz_runs (run_date, window_hours, watchlist_version, leaderboard, narratives, raw_metrics, complete)
VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6::jsonb, $7);
```
to add `community_opinions` (and, if you want the sector narrative persisted too, add a
column for it — not in the current schema; simplest is to fold it into the existing
`narratives` jsonb or add a `sector_narrative` jsonb column alongside the migration in §7):
```sql
INSERT INTO hn_buzz_runs (run_date, window_hours, watchlist_version, leaderboard, narratives, community_opinions, raw_metrics, complete)
VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6::jsonb, $7::jsonb, $8);
```
and extend `queryReplacement` with `{{ JSON.stringify($json.community_opinions) }}` in the
matching `$6` position (shifting `raw_metrics`/`complete` to `$7`/`$8`). **Apply the
migration in §7 before this**, or the insert fails with the same "column does not exist"
error the dashboard hit in Week 8.

**Step E — verify (Phase-1-style):**
- Run the workflow manually on the full watchlist; confirm each entity gains a
  `communityOpinion` on its leaderboard entry (or a clean `degraded=true` one for
  comment-less entities), the row's `community_opinions` map is non-null, and
  `sectorNarrative` is populated.
- Temporarily point the Groq credential at a bad key → confirm the run still completes
  with every entity degraded, not a hard failure.
- Confirm an entity whose top stories have zero comments (or all-deleted comments)
  degrades cleanly via step 11's fill-in, instead of silently vanishing from the run.
- Watch node 2/5's per-item call count — 3 stories × 15 comment-ID fetches × ~12 entities
  is up to ~540 comment-item HTTP calls per run; confirm this completes within your
  schedule-trigger's expected runtime and doesn't trip HN's (unstated but real) rate limits.
  If it's too slow, lower the `[:15]`/`[:3]` caps in steps 1/4.

**Not yet done:** all of Steps B–E above and the `alter table` migration in §7 — both
require your running n8n/Postgres instance to apply and verify, same as every other "apply
and verify" step in this plan. The dashboard's Community Opinion panel is still a
placeholder (`docs/dashboard_design.md`) until this pipeline is live and the column exists;
wiring the dashboard to it is a separate, later step once this analyzer is verified end to end.

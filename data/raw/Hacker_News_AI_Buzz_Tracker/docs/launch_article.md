# Reading the room: a Hacker News attention signal for the AI sector

*Part of the Mycroft project — "Using AI to Invest in AI."*

## The idea

AI launches, outages, funding rounds, and controversies get argued out on Hacker
News before they reach mainstream financial coverage. If the technical community
is where mindshare forms first, then the *volume and intensity* of that
discussion might be a leading indicator of attention — and attention sometimes
leads price.

That "might" is the whole point. This agent doesn't assume the thesis; it
measures the signal cleanly enough to **test** it, and says so honestly wherever
the evidence is thin.

## What it does

An n8n workflow runs daily against one free, no-key data source (Hacker News via
Algolia + the Firebase item API) and produces, per AI company on a versioned
watchlist:

- a deterministic **Buzz Score** (0–100) — how *much* attention, from story
  volume, engagement, front-page reach, and day-over-day acceleration;
- a **Community Opinion** — what people are actually *saying*, distilled by an LLM
  from the real comment text on each company's top stories (summary, sentiment,
  themes, notable opinions);
- a **narrative theme + tone**, a cross-entity **sector narrative**, and a ranked
  email digest that fires on breakout.

Two distinct outputs every run: a machine JSON signal for the coordination layer,
and a human HTML digest — never the same artifact for both audiences.

## Three things that broke, and what they taught

1. **Strict JSON mode fought the model.** Forcing the LLM into a strict
   `json_object` schema made it fail on quote-heavy comment text — every entity
   errored. The fix was to *loosen* the contract (parse leniently, ask for
   paraphrase) rather than fight the decoder. Fluency isn't the constraint; valid
   structure is.

2. **The model narrated a void.** When every entity had no usable comments, the
   sector step still confidently invented a "mood of the week." Now a gate skips
   the LLM entirely when there's nothing real to summarize. A pipeline should
   never let a model speak from nothing.

3. **Confident, well-formed, and wrong.** A viral "Show HN" post that merely
   name-dropped Claude and ChatGPT became the top story for both OpenAI and
   Anthropic — so their opinions described an unrelated slide tool. The code ran
   perfectly on the wrong input. The fix (require the company's name in the story
   *title*, not just anywhere in the post) is a relevance filter, and the honest
   lesson is that the hard problems here were judgment, not syntax.

## What's honest about it

- Sparse data is **labeled, not hidden**: low-confidence flags (<3 comments /
  <3 stories), an absolute-floor score for quiet entities, and a hard-zero
  cold-start velocity on first run.
- The investment framing is treated as a **hypothesis pending a backtest**, not a
  premise.
- Watchlist changes are **versioned clean breaks** so a new entity can't silently
  reset everyone's baseline.

## Try it

Import the workflow into a local n8n, point it at a free Supabase project and a
Groq key, and run once manually. Open the dashboard at `/webhook/dashboard`, or
pull the JSON contract at `/webhook/signal`. Everything is in `README.md` and the
`docs/` folder.

---

*Status: core agent, LLM narrative, Community Opinion, dashboard, and the
coordination-layer contract are live. Story-relevance filtering, the richer
digest, and the externalized watchlist config landed in the final month. Remaining
launch tasks: re-export `workflow.json`, record a short demo, open the final PR.*

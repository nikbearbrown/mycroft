# I Built an AI Agent That Reads $600B in Government Contracts So Analysts Don't Have To

### How I turned SAM.gov's daily firehose into a scored, Claude-powered analyst feed

---

*This is Sprint 13 of the Mycroft Project — my ongoing effort to build a full-stack competitive intelligence platform. Previous sprints: the OSS Engineering Health Agent and the Competitive Landscape Intelligence Agent. Each sprint ships a working tool. This one is the most immediately useful.*

---

Every day, the U.S. federal government quietly publishes hundreds of contract awards on a website called SAM.gov.

Most people have never heard of it.

Here's what SAM.gov tells you: which company just won a federal contract, which agency awarded it, how much it's worth, and what it's for. Updated daily. Completely public. Free to access.

Defense analysts read it. Most everyone else doesn't.

That's not a gap in awareness — it's a signal-to-noise problem. And signal-to-noise problems are exactly what AI agents are built to solve. Not replacing human judgment — taking a dataset too large and too noisy to monitor manually, turning it into a prioritized feed, and then using a language model to do what a language model is actually good at: synthesizing meaning from raw data.

That's what I built. Here's how.

---

## The Problem With SAM.gov

On any given day, there are hundreds of new award notices. The vast majority are completely irrelevant to anyone tracking the AI and defense-tech space — nuts and bolts for the Defense Logistics Agency, lawn mowing contracts for Army Corps facilities, medical supplies for the VA.

Buried inside that noise are the signals that actually matter: a $52M AI contract awarded to Palantir by the Defense Intelligence Agency, a $150M autonomous systems win for Anduril, a new AI training data deal with the Army.

By the time that kind of news makes it into a press release or a news article, everyone already knows. The edge is in reading it first — directly from the source, the day it's published.

The problem isn't access. The data is right there. The problem is that making it usable requires two things most teams never build: automation to filter the noise, and intelligence to interpret the signal.

---

## What I Built

The **Government Contract Awards Signal Agent** has four parts:

1. A **Python backend** that fetches live award data from the SAM.gov API, classifies each award by agency type, and scores it for relevance
2. A **signal scoring engine** that ranks every award 0 to 1 based on four observable factors
3. A **Claude-powered analyst layer** that generates a strategic brief for every high-scoring award
4. A **React dashboard** that surfaces the highest-scoring awards in real time, with live filters, score badges, and per-award AI analysis

The pipeline end to end:

```
SAM.gov API
    ↓
Fetch award notices (last 30 days, filtered by keyword)
    ↓
Classify agency type  →  DoD / Intel / Civilian
    ↓
Score for signal relevance  →  0.0 – 1.0
    ↓
Claude analyst brief  →  HIGH-signal awards only (≥ 0.70)
    ↓
Serve via FastAPI
    ↓
Display on live React dashboard
```

The whole system runs on demand, returns enriched and scored results in seconds, and shows you exactly why each award scored what it did — plus what it means strategically.

---

## The Scoring Engine

This is the first intelligence layer.

The core question is: *should an analyst pay attention to this award?*

Four observable factors with explicit weights:

| Factor | What it checks | Weight |
|--------|---------------|--------|
| **Tracked company** | Is the recipient on our watchlist? | +0.40 |
| **Contract size** | Is the award ≥ $10 million? | +0.25 |
| **AI NAICS code** | Is the work AI or software-related? | +0.20 |
| **Priority agency** | Is it DoD or an Intel agency? | +0.15 |

The weights reflect a deliberate editorial decision: *who* is winning matters more than *how much* they're winning.

Awards are surfaced on the dashboard as:

- **HIGH** (≥ 0.70) — something happened worth reading today
- **MEDIUM** (≥ 0.40) — interesting, worth a second look
- **LOW** (≥ 0.15) — on the radar, low priority
- **NONE** (< 0.15) — filtered noise

The model is transparent by design. Every score is explainable — you can look at any award and see exactly which factors fired and why.

---

## The Claude Layer — Where the Agent Actually Thinks

This is what separates a pipeline from an agent.

The scoring engine is deterministic. It applies fixed rules and produces a number. That's useful — but a number isn't analysis. It tells you *that* Palantir's DIA contract scored 1.0. It doesn't tell you *why that matters*.

For every award that scores HIGH, the system calls **Claude** (claude-opus-4-6) and asks it to reason about the contract as an analyst would:

> *"Write a 2–3 sentence analyst brief. Focus on what this award signals strategically — who won, what it means for their position, and why it matters to investors or competitors tracking this space."*

Here's what Claude actually produced for Palantir's $52M Defense Intelligence Agency award:

> *Palantir's $52 million award from the Defense Intelligence Agency for an AI/ML-driven intelligence analytics platform reinforces the company's entrenched position as the go-to vendor for mission-critical data fusion and threat detection across the IC, further widening its competitive moat against challengers like BAH, C3 AI, and emerging startups seeking to break into classified analytics work. The DIA contract signals continued institutional commitment to Palantir's ecosystem — likely expanding on existing deployments — at a time when the intelligence community is accelerating AI adoption timelines, which should give investors confidence in the durability of the company's government revenue pipeline. Competitors should note that each additional IC deployment deepens integration dependencies and raises switching costs, making future displacement efforts increasingly difficult and expensive.*

That's not a template. That's not fill-in-the-blanks. Claude read the contract data — recipient, agency, amount, NAICS code, description — and synthesized a judgment about competitive positioning, switching costs, and investor implications.

No rule could produce that. That's what the model is for.

### Why the threshold matters

Claude only runs on HIGH-scoring awards. That's deliberate.

The rules-based scorer acts as a pre-filter. You don't want to spend API calls asking Claude to analyze a janitorial services contract. The scoring engine handles the noise; Claude handles the signal.

This is the core pattern behind practical AI agent design: **rules narrow the problem space, the model reasons about what's left.**

---

## The Agency Classifier

SAM.gov returns agency names as full hierarchical paths — something like `DEPT OF DEFENSE.DEPT OF THE NAVY.NAVSEA.NAVSEA HQ` — which makes naive string matching useless.

The classifier resolves this with a specificity-first keyword matching system: longer, more precise keywords take priority over broader ones, so `DEFENSE INTELLIGENCE AGENCY` correctly resolves to **Intel** before the broader `DEPT OF DEFENSE` match fires as **DoD**. The mapping lives in a CSV — an analyst can add or reclassify any agency without touching code.

---

## Real Results

Here's a sample from a live run with tracked companies populated — these are the scores and Claude-generated briefs you see on the dashboard:

| Recipient | Agency | Amount | Score | Tag |
|-----------|--------|--------|-------|-----|
| Palantir Technologies | Defense Intelligence Agency | $52,000,000 | 1.00 | HIGH |
| Anduril Industries | Dept of the Air Force | $150,000,000 | 0.60 | MEDIUM |
| Booz Allen Hamilton | NAVSEA | $38,000,000 | 0.60 | MEDIUM |
| Scale AI | US Army | $22,500,000 | 0.60 | MEDIUM |
| L3 Technologies | Dept of the Navy | $147,498,082 | 0.40 | MEDIUM |
| GOV San Antonio LLC | GSA Public Buildings | $20,075,389 | 0.25 | LOW |

Palantir scores 1.0: tracked company (+0.40) + large contract (+0.25) + AI NAICS (+0.20) + Intel agency (+0.15). Every factor fires. Claude generates the brief automatically.

Anduril, Booz Allen, and Scale AI score 0.60: tracked company + large contract + DoD agency. The AI NAICS factor doesn't fire (no matching NAICS code in the raw data). One more factor and they'd all jump to HIGH.

---

## The Stack

**Backend:** Python + FastAPI + httpx (async SAM.gov calls) + Pydantic + Anthropic SDK

**Frontend:** React 18 + Vite + react-router-dom + Axios

**Data:** Two CSV files — agency mappings and tracked companies

**LLM:** Claude (claude-opus-4-6) via the Anthropic API — called only for HIGH-signal awards

No database. No message queue. No infrastructure to manage.

The backend is six services, each one independently replaceable:

```
fetcher.py      → async SAM.gov API client
classifier.py   → agency type resolver
scorer.py       → signal score calculator
parser.py       → CSV/JSON file parser
summarizer.py   → aggregate report generator
llm_briefer.py  → Claude analyst brief generator
```

---

## What's Next

**1. Tracked company intelligence — the highest-leverage move.**
The tracked companies list is already populated and driving the scoring. Expanding it with the full defense-tech ecosystem — every Palantir competitor, every AI-focused govcon player — turns this into a complete market surveillance feed.

**2. Daily digest alerts.**
A scheduled job that runs every morning, fetches the latest awards, filters to score ≥ 0.70, generates Claude briefs, and delivers a summary email. No more manual fetching.

**3. Historical tracking.**
Right now every fetch is stateless. Persisting awards to a database enables trend detection — is a company's contract count growing? Which agencies are increasing AI spending quarter over quarter?

**4. Deeper Claude analysis.**
The current brief is 2–3 sentences. The next version will include competitive context — who else has won contracts from this agency, what the contract size means relative to the company's known revenue, and what the NAICS code signals about the nature of the work.

---

## The Bigger Picture

The federal government spends over **$600 billion a year** on contracts.

That data is public, updated daily, and available via API. The people who would benefit most from reading it systematically — investors tracking defense-tech, analysts watching government AI spend, business development teams in the govcon space — mostly aren't reading it, because the volume and noise make it practically unusable without automation.

This is the problem Mycroft is built to solve, one sprint at a time: take high-value public datasets that are too large and too noisy to monitor manually, build a scoring engine to filter the noise, and deploy a language model to reason about what's left.

The rules handle the volume. Claude handles the judgment.

Sprint 13 is live. Sprint 14 is next.

---

*Follow along to see what gets built. If you're working in defense-tech, govcon, or competitive intelligence — reply with the companies or agencies you'd add to the watchlist. Real analyst input makes the scoring model sharper.*

---

**Tags:** `AI Agents` `Government Contracts` `Defense Tech` `Python` `Claude` `Competitive Intelligence`

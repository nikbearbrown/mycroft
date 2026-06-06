# Presentation Script — Government Contract Awards Signal Agent

**Estimated time: 6–8 minutes**
*Instructions in [brackets] are stage directions, not spoken aloud.*

---

## Opening — The Problem (45 seconds)

Every single day, the U.S. federal government publishes hundreds of contract awards on SAM.gov —
the official database for government procurement.

These awards tell you exactly which companies are winning government money, from which agencies,
and for how much.

For anyone tracking the AI and defense-tech space — investors, analysts, business development teams —
this is incredibly valuable intelligence.

But here's the problem: **there's no signal in the noise.**

You'd have to manually sift through hundreds of awards a day, most of which are completely
irrelevant — nuts and bolts, landscaping contracts, office supplies — to find the handful
that actually matter.

And even then — finding the award is only half the problem.
The other half is knowing what it *means*.

That's the problem I set out to solve.

---

## What I Built (30 seconds)

I built the **Government Contract Awards Signal Agent** —
a full-stack intelligence tool that automatically monitors SAM.gov in real time,
scores every award for relevance, and then deploys Claude — Anthropic's AI — to write
a strategic analyst brief for the awards that matter.

Think of it as an analyst sitting on top of a firehose of procurement data,
reading everything, ignoring the noise, and briefing you on what's worth your attention.

---

## How It Works — The Pipeline (90 seconds)

[Walk through the dashboard as you explain each step]

The system has six layers:

**First — Fetch.**
The agent pulls live award notices directly from the SAM.gov API.
Search by keyword — "artificial intelligence", "cybersecurity", "autonomous systems" —
and it queries the last 30 days of awards automatically.

**Second — Classify.**
Each award comes with a raw agency name — something like
"DEPT OF DEFENSE dot DEFENSE INTELLIGENCE AGENCY."
The classifier parses that full path and tags it as DoD, Intel, or Civilian.
That context feeds directly into the score.

**Third — Score.**
Every award gets a signal score between 0 and 1, built from four factors:
- Is the recipient a company we're tracking? That's worth 40 points.
- Is the award over $10 million? 25 points.
- Is the NAICS code AI or software related? 20 points.
- Is it a DoD or Intel agency? 15 points.

A $52M AI contract awarded to Palantir by the DIA scores a perfect 1.0.

**Fourth — Claude.**
This is the intelligence layer. For every award that scores HIGH — 0.70 or above —
the system calls Claude and says: analyze this as an analyst would.
What does this award signal strategically? What does it mean for the company's position?
Why should investors or competitors care?

Claude reads the contract data and produces a brief. Not a template — actual synthesis.

**Fifth — Serve.**
Everything is exposed through a FastAPI backend with clean REST endpoints.

**Sixth — Display.**
And it all lands on this React dashboard.

---

## Live Demo (75 seconds)

[Open the dashboard at localhost:5173, click Mock Data]

This is the live dashboard. I'm loading the mock dataset so we're not blocked by API rate limits —
the real SAM.gov data flows through the exact same pipeline.

At the top — summary stats. Six awards, one HIGH signal, $430 million in total contract value,
average signal score of 0.58 across the set.

[Point to the table]

The table is sorted by signal score. Palantir at the top — HIGH 1.00.
Every factor fired: tracked company, large contract, AI NAICS code, Intel agency.

Below that, Anduril, Booz Allen, and Scale AI all score MEDIUM 0.60 —
tracked company, large contract, DoD agency. One more factor and they'd jump to HIGH.

[Click the Palantir row]

This is where the agent layer comes in.

[Scroll to the AI Analyst Brief section]

That card — "AI Analyst Brief" — was written by Claude.

Not a template. Not fill-in-the-blanks. Claude read the award data —
$52 million, Defense Intelligence Agency, AI/ML analytics platform —
and produced this:

*"Palantir's $52 million award from the Defense Intelligence Agency for an AI/ML-driven
intelligence analytics platform reinforces the company's entrenched position as the go-to
vendor for mission-critical data fusion and threat detection across the IC, further widening
its competitive moat against challengers like BAH, C3 AI, and emerging startups...
Competitors should note that each additional IC deployment deepens integration dependencies
and raises switching costs, making future displacement efforts increasingly difficult and expensive."*

That's the model doing what the model is good at — synthesizing a judgment from raw data.
No rule could produce that.

Below the brief, you have the Signal Breakdown — which factors fired, and why.

---

## What Makes This an Agent (45 seconds)

I want to be specific about this, because the word "agent" gets overused.

Most of this system is deterministic. The fetcher, the classifier, the scorer — they follow rules.
That's a pipeline, not an agent.

The agent is `llm_briefer.py` — the layer that calls Claude.

The key distinction: **the scoring engine tells you that an award matters.
Claude tells you why.**

And Claude only runs on HIGH-scoring awards. The rules act as a pre-filter.
You don't want to spend model inference on a janitorial services contract.
The scoring engine handles the noise; Claude handles the signal.

This is the core pattern behind practical AI agent design:
**rules narrow the problem space, the model reasons about what's left.**

---

## What's Next (30 seconds)

The most immediate unlock is scheduled alerting.
Instead of fetching on demand, a job runs every morning, pulls the latest awards,
scores them, generates Claude briefs for anything HIGH, and sends a digest email.
No more manual checking.

After that:
- Historical tracking — store awards over time to detect momentum shifts
- Deeper Claude analysis — competitive context, trend commentary, NAICS interpretation
- Competitor monitoring — get notified the morning after a rival wins a government contract

---

## Closing (15 seconds)

The federal government spends over $600 billion a year on contracts.
That data is public. It's updated daily. And almost nobody is reading it systematically.

This agent changes that — filtering the noise with rules, and deploying Claude
to reason about the signal.

Thank you.

---

## Q&A Prep — Likely Questions

**Q: How often does the data update?**
The SAM.gov API is updated daily. The dashboard fetches on demand — you click Fetch
and get the latest data within the last 30 days. Scheduled fetches are the next priority.

**Q: What's the SAM.gov rate limit?**
The public API key has a daily quota. When you hit it, the dashboard shows a yellow
warning with the exact reset time and keeps showing your last fetched data.
The Mock Data button lets you test the full Claude pipeline even when quota is exceeded.

**Q: Why does Claude only run on HIGH awards?**
Cost and relevance. Running Claude on every award would be expensive and mostly useless —
you don't need an analyst brief on a facilities management contract. The scoring engine
acts as a pre-filter so Claude only sees what's worth analyzing.

**Q: How accurate is the scoring?**
The scoring is rules-based and transparent — you can see exactly why each award
scored what it did. It's a starting point, not a black box. Analysts can tune
the weights or add new factors as needed.

**Q: How accurate is the Claude brief?**
Claude reasons from the data it's given. If SAM.gov provides thin descriptions,
the brief reflects that. For well-described contracts with recognizable companies,
the output is analyst-grade — as you saw with the Palantir example.

**Q: Can it track competitor activity?**
Yes — that's the primary use case. Add competitors to tracked_companies.csv
and every time one of them wins a government contract, it surfaces at the top
of the feed and gets a Claude brief automatically.

**Q: Can this work for sectors other than AI?**
Absolutely. The keyword search, NAICS code list, and tracked companies are all configurable.
Point it at cloud infrastructure, biotech, cybersecurity — just update the config files.

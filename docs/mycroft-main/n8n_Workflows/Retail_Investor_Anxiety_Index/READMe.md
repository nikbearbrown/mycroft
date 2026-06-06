# Retail Investor Anxiety Index

![Dashboard Preview](preview.png)

> A behavioral intelligence dashboard that analyzes Reddit crowd 
> sentiment using AI-powered multi-signal analysis across 
> r/wallstreetbets, r/investing, and r/stocks.

Built with **n8n** · **Claude AI** · **Supabase** · **Chart.js**

---

## What Is This?

Most sentiment tools stop at simple positive/negative scoring. 
This project goes further — it analyzes the *behavioral patterns* 
of retail investors by combining 5 distinct signals extracted 
from Reddit post language every 6 hours.

The result is a live dashboard that answers:
- How fearful or greedy is the crowd right now?
- What narratives are gaining momentum fastest?
- Which stocks are being discussed across all communities simultaneously?
- Are investors making bold calls or hedging nervously?
- Where are we in the crowd psychology cycle?

---

## Dashboard Preview

The dashboard runs at:
```
http://localhost:5678/webhook/dashboard
```

### Panels

| Panel | Signal | What It Shows |
|---|---|---|
| Anxiety Index | Fear/greed score 0-100 | Overall crowd anxiety + 7-day trend |
| Crowd Cycle Stage | Psychology classification | Current market narrative stage |
| Conviction vs Uncertainty | Language assertiveness | Bold claims vs hedging ratio |
| Narrative Velocity | Topic momentum | Fastest rising themes this run |
| Herd Detection | Cross-subreddit overlap | Tickers discussed across all 3 communities |
| Subreddit History | Per-community trend | 7-day anxiety per subreddit |
| Conviction History | Assertiveness over time | How crowd confidence shifts |
| Most Fearful Posts | Top scored posts | The 3 highest fear-scoring posts |

---

## Signal Design

### Layer 1 — Scoring Pipeline

Every post title goes through a two-stage scoring process:

**Stage A — Keyword Pre-Scorer**
A weighted keyword matcher runs first on every post:

| Category | Weight | Example Keywords |
|---|---|---|
| Fear (high) | +20pts | crash, margin call, recession, rekt, capitulate |
| Fear (mid) | +10pts | sell, correction, bearish, tariff, crisis, volatile |
| Greed (high) | -20pts | moon, yolo, diamond hands, short squeeze |
| Greed (mid) | -10pts | buy the dip, bullish, rally, profit |
| Amplifiers | ×1.2 | massive, historic, unprecedented, critical |

Posts are tagged with a zone:
- `CLEAR_FEAR` (61-100) — keyword score confident
- `AMBIGUOUS` (40-60) — escalated to Claude for scoring
- `CLEAR_GREED` (0-39) — keyword score confident

**Stage B — Claude Anxiety Scoring**
Ambiguous posts are sent to Claude Sonnet with explicit 
scoring rules to avoid clustering around 50. Posts about 
war, large losses, or market crashes must score 65+.

### Layer 2 — Beyond Scoring

**Narrative Velocity**
Claude extracts the top 10 topics from the current batch 
and compares them to the previous run. The velocity score 
measures rate of change — not raw frequency. A topic 
appearing for the first time scores higher than one that 
has been consistently discussed.

**Herd Detection**
Claude identifies tickers, company names, and macro themes 
appearing across multiple subreddits simultaneously. When 
the same asset is being discussed in r/wallstreetbets, 
r/investing, AND r/stocks at the same time, that convergence 
is a behavioral signal regardless of sentiment direction.

**Conviction vs Uncertainty**
Claude scores the ratio of assertive language ("I'm buying", 
"this will crash") vs uncertain language ("should I?", 
"not sure", "maybe"). A high conviction score during fear 
suggests strong bearish conviction. High conviction during 
greed suggests euphoria.

**Crowd Cycle Stage**
Claude classifies the entire batch into one of 6 stages:

| Stage | Description |
|---|---|
| Euphoria 🚀 | Extreme optimism, FOMO, everyone is winning |
| Complacency 😴 | Calm, passive, low urgency |
| Anxiety 😰 | Worried but not panicking, lots of questions |
| Denial 🙈 | Ignoring bad signs, rationalizing losses |
| Panic 💥 | Extreme fear, selling everything, catastrophic language |
| Hope 🌱 | Cautious optimism after a down period |

---

## Architecture

### Workflow Paths

```
PATH 1 — Dashboard (serves HTML page)
GET /webhook/dashboard
  → Build Dashboard Response (embedded HTML)
  → Serve Dashboard HTML
  → Browser renders dashboard, fetches live data from Supabase

PATH 2 — Scheduled Pipeline (every 6 hours, silent)
Schedule Trigger
  → Fetch WSB + Fetch Investing + Fetch Stocks (3 parallel HTTP calls)
  → Merge Reddit Feeds (waitForAll)
  → 1A: Raw Merge & Structural Clean
      Extract: id, title, subreddit, score, upvoteRatio
      Remove: duplicates, empty titles
  → 1B: Linguistic & Relevance Filter
      Extract tickers ($AAPL and AAPL format)
      Strip: URLs, emojis, special characters
      Flag: isQuestion, wordCount
      Remove: posts under 4 words
  → Keyword Pre-Scorer
      Tag each post: CLEAR_FEAR / AMBIGUOUS / CLEAR_GREED
  → Aggregate for Claude
      Group tickers by subreddit
      Load previousTopics from static data
  → 5 Claude AI calls (parallel):
      Claude 1: Anxiety Score (AMBIGUOUS posts only)
      Claude 2: Narrative Velocity (all posts)
      Claude 3: Herd Detection (tickers by subreddit)
      Claude 4: Conviction vs Uncertainty (all posts)
      Claude 5: Crowd Cycle Stage (all posts)
  → Merge Claude Outputs (waitForAll, 5 inputs)
  → Signal Aggregator
      Merge Claude scores back to posts
      Calculate averages per subreddit
      Extract top 3 fearful posts
  → Persist to File (static data, 7-day rolling window)
  → Generate Quickchart URLs (4 chart image URLs)
  → Write output.json (static data)
  → Insert to Supabase (REST API POST)
  → Check Trigger Type (IF node)
      → Schedule path: ends silently
      → Webhook path: Pipeline Response (JSON)

PATH 3 — On-demand Trigger
GET /webhook/run-pipeline
  → same pipeline as Path 2
  → Returns JSON: { status, anxietyScore, date, postCount }
```

### Data Flow

```
Reddit JSON API (public, no auth)
      ↓
n8n pipeline (clean → score → analyze)
      ↓
Supabase PostgreSQL (stores every run)
      ↓
dashboard.html (reads latest 7 rows on load)
      ↓
Chart.js renders all panels
```

### Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Workflow engine | n8n | Visual pipeline, built-in scheduler, webhook support |
| AI model | Claude Sonnet 4 | Best-in-class for nuanced language understanding |
| Database | Supabase (PostgreSQL) | Free tier, instant REST API, jsonb columns |
| Charts | Chart.js 4.4 | Lightweight, no build tools, all chart types needed |
| Frontend | Vanilla JS | Zero dependencies, fast load, single file |
| Chart images | Quickchart.io | Server-side chart URLs for embedding |

---

## Setup Guide

### Prerequisites

- Node.js 18 or higher
- npm
- Anthropic API account (claude.ai/settings → API Keys)
- Supabase account (supabase.com — free tier works)

### Step 1 — Install and Start n8n

```bash
npm install -g n8n
npx n8n
```

Open http://localhost:5678 and create an account.

### Step 2 — Create Supabase Database

1. Go to supabase.com → New project
2. Open SQL Editor and run:

```sql
create table anxiety_runs (
  id uuid default gen_random_uuid() primary key,
  created_at timestamptz default now(),
  date text,
  timestamp text,
  post_count integer,
  anxiety_score integer,
  subreddit_scores jsonb,
  top3_fearful_posts jsonb,
  narrative_velocity jsonb,
  herd_detection jsonb,
  conviction jsonb,
  cycle_stage jsonb,
  anxiety_chart_url text,
  velocity_chart_url text,
  herd_chart_url text,
  conviction_chart_url text,
  herd_tickers jsonb,
  conviction_score integer,
  uncertainty_score integer,
  conviction_ratio float,
  dominant_post_titles jsonb
);

alter table anxiety_runs disable row level security;
```

3. Go to Project Settings → API
4. Copy: Project URL and anon public key

### Step 3 — Configure Credentials

In workflow.json replace these placeholders:

| Placeholder | Where to get it |
|---|---|
| `YOUR_ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `YOUR_SUPABASE_ANON_KEY` | Supabase → Project Settings → API |
| `YOUR_SUPABASE_URL` | Supabase → Project Settings → API |
| `YOUR_REDDIT_USERNAME` | Your Reddit username (or any string) |

In dashboard.html replace:

| Placeholder | Value |
|---|---|
| `YOUR_SUPABASE_URL` | Your Supabase project URL |
| `YOUR_SUPABASE_ANON_KEY` | Your Supabase anon key |

### Step 4 — Import Workflow into n8n

1. Open http://localhost:5678
2. Workflows → Import from file → select workflow.json
3. Open workflow → find all Anthropic Model nodes
4. Add credential: name it exactly "Anthropic account 3"
5. Update Build Dashboard Response node with 
   your updated dashboard.html content
6. Toggle workflow Active (top right)

### Step 5 — First Run

Click the dropdown next to Execute Workflow → 
select "Execute workflow from Schedule Trigger"

Watch all nodes turn green (~60 seconds).

Check Supabase Table Editor → anxiety_runs → 
confirm a new row appeared.

### Step 6 — Open Dashboard

```
http://localhost:5678/webhook/dashboard
```

---

## Usage

### Automatic Mode
Once active, the workflow runs every 6 hours silently.
Open the dashboard anytime to see the latest data.

### On-Demand Mode
Trigger a fresh pipeline run instantly:
```
http://localhost:5678/webhook/run-pipeline
```
Returns JSON confirmation when complete:
```json
{
  "status": "success",
  "message": "Pipeline completed",
  "anxietyScore": 52,
  "date": "2026-04-06",
  "postCount": 68
}
```
Switch back to the dashboard tab → click Refresh Now.

### Dashboard Auto-Refresh
The dashboard auto-refreshes every 30 minutes.
It also refreshes when you switch back to the tab.

---

## Data Schema

Each run stored in Supabase:

```json
{
  "date": "2026-04-06",
  "post_count": 71,
  "anxiety_score": 52,
  "subreddit_scores": {
    "wallstreetbets": 53,
    "investing": 51,
    "stocks": 55
  },
  "top3_fearful_posts": [
    { "title": "...", "score": 80 }
  ],
  "narrative_velocity": [
    { "topic": "Iran conflict", "velocityScore": 85 }
  ],
  "herd_detection": [
    { "ticker": "OIL", "isHerd": true, "mentions": {...} }
  ],
  "conviction": {
    "convictionScore": 72,
    "uncertaintyScore": 28,
    "ratio": 2.57
  },
  "cycle_stage": {
    "stage": "Anxiety",
    "confidence": 0.85,
    "reasoning": "..."
  }
}
```

---

## Project Structure

```
Retail_Investor_Anxiety_Index/
├── workflow.json        # n8n workflow — import this
├── dashboard.html       # Standalone dashboard (local fallback)
├── README.md            # This file
└── .gitignore           # Excludes personal data files
```

---

## Limitations

- Anxiety score tends toward neutral (45-55) on low-signal days
- Historical charts need 2+ days of runs to show trends
- n8n must be running locally for webhook URLs to work
- Reddit rate limits may occasionally affect fetch nodes
- Supabase free tier has 500MB storage limit

---

## Possible Extensions

- Add Google Trends as a third data source
- Compare anxiety index against actual price data
- Add email/Slack alert when anxiety crosses threshold
- Deploy n8n to a cloud server for 24/7 availability
- Add more subreddits (r/options, r/stocks, r/economy)
- Build a mobile-friendly version

---

## License

MIT — free to use, modify, and distribute.

---

## Built By

**Sahiti Nallamolu**  
[linkedin.com/in/sahitinallamolu](https://www.linkedin.com/in/sahitinallamolu/)

Built as part of the **Humanitarians AI Fellows Program** — exploring 
unconventional data sources for behavioral finance signals.

# Patent Filing Velocity Tracker

> An AI-powered pipeline that tracks patent filing acceleration across major AI chip companies — finding signals in public USPTO data before they appear in analyst reports.

Built with **n8n** · **Claude AI** · **Supabase** · **Chart.js** · **USPTO PatentsView API**

---

## What Is This?

Companies file patents before products ship. When a company goes from filing 3 AI chip patents per quarter to 23, something has changed internally — new research direction, new product line, new competitive strategy. That change becomes public knowledge when the product ships or when analysts pick it up. The patent record exists before both.

This pipeline tracks patent filing velocity for 5 major AI chip companies (NVIDIA, AMD, Intel, Google, Apple) and surfaces 5 behavioral signals from their filing patterns every time it runs.

---

## Signals

| Signal | Claude Call | What It Detects |
|---|---|---|
| Velocity Score | Claude 1 | How aggressively each company is filing (0-100) |
| Concept Novelty | Claude 2 | New technical terms appearing for the first time |
| Inventor Network | Claude 3 | Team expansion signals in inventor lists |
| Cross-Company Convergence | Claude 4 | Technology areas all companies are targeting simultaneously |
| Strategic Intent | Claude 5 | Defensive / Expansive / Foundational / Incremental / Exploratory |

---

## Architecture

```
PATH 1 — Pipeline (on-demand)
GET /webhook/run-patent-pipeline
  → Fetch Patent Data (USPTO PatentsView API)
  → 1A: Structural Clean
  → 1B: Category Classifier + Velocity Pre-Scorer
  → Aggregate for Claude
  → 5 Claude calls (parallel)
  → Merge Claude Outputs (waitForAll)
  → Signal Aggregator
  → Insert to Supabase
  → Pipeline Response (JSON confirmation)

PATH 2 — Dashboard
GET /webhook/patent-dashboard
  → Build Dashboard HTML
  → Serve Dashboard HTML
  → Browser renders, fetches from Supabase
```

---

## Prerequisites

- Node.js 18+
- n8n installed globally
- Anthropic API key
- Supabase account (free tier works)
- No USPTO API key needed — PatentsView API is free and open

---

## Setup

### Step 1 — Install and Start n8n

```bash
npm install -g n8n
npx n8n
```

Open `http://localhost:5678`

---

### Step 2 — Create Supabase Database

1. Go to [supabase.com](https://supabase.com) → New project
2. Name it `patent-velocity-tracker`
3. Open SQL Editor and run:

```sql
create table patent_runs (
  id uuid default gen_random_uuid() primary key,
  created_at timestamptz default now(),
  date text,
  timestamp text,
  leaderboard jsonb,
  convergence jsonb,
  quarterly_stats jsonb,
  total_patents_analyzed integer
);

alter table patent_runs disable row level security;
```

4. Go to **Project Settings → API**
5. Copy: **Project URL** and **anon public key**

---

### Step 3 — Configure Credentials

In `workflow.json` replace these placeholders:

| Placeholder | Where to get it |
|---|---|
| `YOUR_ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| `YOUR_ANTHROPIC_CREDENTIAL_ID` | n8n → Credentials → your Anthropic credential ID |
| `YOUR_ANTHROPIC_CREDENTIAL_NAME` | n8n → Credentials → your Anthropic credential name |
| `YOUR_SUPABASE_URL` | Supabase → Project Settings → API → Project URL |
| `YOUR_SUPABASE_ANON_KEY` | Supabase → Project Settings → API → anon public key |

In `workflow.json` the dashboard HTML section also contains:
```javascript
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
```
Replace both with your actual values.

---

### Step 4 — Import Workflow into n8n

1. Open `http://localhost:5678`
2. Workflows → Import from file → select `workflow.json`
3. Open the workflow
4. Click each **Anthropic Model** node (1-5) and select your Anthropic credential
5. Toggle workflow **Active** (top right)

---

### Step 5 — First Run

With n8n running and workflow active, open browser and go to:

```
http://localhost:5678/webhook/run-patent-pipeline
```

Wait 60-90 seconds. You will see:

```json
{
  "status": "success",
  "message": "Pipeline completed",
  "date": "2026-04-20",
  "totalPatents": 847,
  "topCompany": "NVIDIA",
  "topVelocityScore": 82
}
```

---

### Step 6 — View Dashboard

```
http://localhost:5678/webhook/patent-dashboard
```

---

## URLs

| URL | Purpose |
|---|---|
| `http://localhost:5678/webhook/run-patent-pipeline` | Trigger fresh pipeline run |
| `http://localhost:5678/webhook/patent-dashboard` | View live dashboard |

---

## Dashboard Panels

| Panel | Description |
|---|---|
| Velocity Leaderboard | Companies ranked by filing acceleration with QoQ change |
| Strategic Intent | What each company's patents suggest about their strategy |
| Cross-Company Convergence | Shared focus areas and differentiation zones |
| Filing Velocity Over Time | 8-quarter trend lines per company |
| Emerging Concepts | New technical vocabulary appearing this run |

---

## Data Source

**USPTO PatentsView API** — free, no authentication required, updated weekly.

- Endpoint: `https://api.patentsview.org/patents/query`
- Documentation: [patentsview.org/apis](https://patentsview.org/apis)
- Rate limit: 45 requests per minute (pipeline stays well within this)

**CPC Codes tracked:**
- `G06N` — AI/ML Algorithms
- `G06N3` — Neural Networks
- `G06N3/063` — AI Hardware
- `H01L` — Semiconductor Devices

---

## Known Limitations

**Company name normalization** — Patent assignees are filed under different legal names. Google files under "Google LLC", "Alphabet Inc", "DeepMind Technologies". The pipeline checks multiple aliases but may miss some subsidiaries.

**Filing date vs grant date** — The pipeline uses patent filing date, not grant date. Filing dates are earlier and better for signal detection, but patents aren't public until 18 months after filing. PatentsView data reflects published patents only.

**Abstract quality varies** — Some patents have detailed technical abstracts; others are vague. Claude's concept extraction quality depends on abstract richness.

**First run baseline** — Concept novelty and inventor network signals require at least 2 runs to produce meaningful comparisons. First run establishes the baseline.

---

## Extending This Pipeline

**Add more companies:** In the `Fetch Patent Data` node, add entries to the `companies` array with their USPTO filing names.

**Add more categories:** Add CPC codes to the `CPC_CODES` array and update `CPC_CATEGORIES` mapping.

**Add more technology verticals:** Clone the workflow and change the company list and CPC codes. The architecture works for any patent-filing industry — biotech, clean energy, quantum computing.

**Add price correlation:** After accumulating 4+ quarters of velocity data, compare velocity scores against stock price movements to test whether acceleration precedes analyst coverage.

---

## Project Structure

```
Patent_Filing_Velocity_Tracker/
├── workflow.json    ← import into n8n
├── README.md        ← this file
└── .gitignore       ← excludes personal data
```

---

## Part of the Mycroft Project

This agent is part of [Mycroft](https://github.com/Humanitariansai/Mycroft) — an open-source financial intelligence research initiative by [Humanitarians AI](https://www.humanitarians.ai/).

---

## License

MIT

---

*Developed by [Sahiti Nallamolu](https://www.linkedin.com/in/sahitinallamolu/), Fellow at Humanitarians AI. For educational and research purposes. Not financial advice.*
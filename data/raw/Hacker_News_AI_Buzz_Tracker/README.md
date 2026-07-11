# Hacker News AI Buzz Tracker

> **Developed by:** Om Mali (mali.om@northeastern.edu)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/Humanitariansai)

Part of the **Mycroft** project — *"Using AI to Invest in AI."*

## What Is This

The Hacker News AI Buzz Tracker is an n8n agent that turns developer discussion on Hacker News
into a quantified, comparable **developer-attention signal** for the AI sector. It watches a
watchlist of AI companies and products, scores how much attention each is getting over a trailing
window, and reports the daily movers.

The thesis: mindshare leads price in the AI sector, and the technical community is where mindshare
forms first. AI launches, model releases, outages, and controversies get debated on Hacker News
before they reach mainstream financial coverage. This agent makes that early, scattered attention
visible as a clean number. **It measures attention, not direction** — it is one disciplined input
among many, not a trade trigger.

## Signals

| Signal | Source | Description | Status |
|--------|--------|-------------|--------|
| **Buzz Score** | Code node | Overall HN attention per entity, 0–100 (deterministic). | ✅ Live |
| **Buzz Velocity** | Code node | Acceleration vs. the previous run (`20 × clamp(Δ/prior_base, −1, 2)`). | ✅ Live (Week 4) |
| **Front Page Breakouts** | Code node | Count of stories crossing a high points threshold. | ✅ Live |
| **Narrative Theme** | LLM | launch, outage, funding, research, controversy, or hiring. | 🔜 Week 7 |
| **Reception Tone** | LLM | bullish, bearish, or neutral developer reception. | 🔜 Week 7 |
| **Community Opinion** | LLM (comment-text) | Comment-grounded opinion summary, sentiment, and themes per entity. | 🔜 Week 9 |

The workflow produces two **distinct** outputs each run: a machine-readable **JSON signal** for the
coordination layer, and a human-readable **HTML email digest** of the top movers (sent on breakout).

See `design.md` for the full data model and `docs/scoring_logic.md` for the Buzz Score formula.

## Architecture

```
Schedule Trigger (daily) / Manual Trigger
  → Watchlist (entities, query terms, ticker, thresholds)
  → Loop Over Entities (Split In Batches)
      → Entity Term Pair → HTTP Request: HN Algolia search_by_date (trailing window)
      → Get Metrics: aggregate + dedupe per-entity metrics, retain top-3 stories
  → Postgres (Supabase): Get Previous Run (latest complete snapshot)   ── before scoring
  → Merge (current metrics + previous run)
  → Code: compute Buzz Score + Velocity vs. previous run
  → Build Run Row (collapse to one snapshot row)
      ├→ Postgres (Supabase): Save Snapshot (parameterized jsonb insert)  ── after scoring
      ├→ Build JSON Signal (coordination-layer contract)
      └→ IF: any entity breakout? → Build Digest HTML → Send Email
  → [separate workflow] Error Trigger → Send Email (pipeline-failure alert)

  Planned: LLM narrative/tone (Week 7), Community Opinion (Week 9),
           dashboard webhook GET /webhook/dashboard (Week 8).
```

## Prerequisites

- **n8n** running locally (Docker recommended):
  ```bash
  docker volume create n8n_data
  docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
  ```
  Then open http://localhost:5678.
- **Supabase** free-tier project (Postgres) for snapshots — **required** (see `DATABASE_SETUP.md`).
- **SMTP** credentials (e.g. a Gmail app password) for the email digest and failure alerts.
- A free **Groq API key** (or an Anthropic/Claude key) for the LLM narrative layer — *needed from Week 7*.
- No key is needed for the Hacker News Algolia data source.

## Setup

1. Copy `.env.example` to `.env` and fill in your keys (kept out of git).
2. Create the Supabase project and `hn_buzz_runs` table — follow **[`DATABASE_SETUP.md`](DATABASE_SETUP.md)**.
3. Import the workflow into n8n (**Workflows → Import from File**), plus the separate
   error-alert workflow.
4. Configure credentials: **Postgres** (Supabase) and **SMTP** (email). Set the main workflow's
   **Settings → Error Workflow** to the error-alert workflow.
5. Edit the **Watchlist** node (or `watchlist.json`) to set your entities and thresholds.
6. Run a manual execution to verify, then activate the schedule.

## Schema

Snapshots are stored in Supabase Postgres in the `hn_buzz_runs` table — **one row per run**.
Full setup, credential config, and the read/insert queries are in
**[`DATABASE_SETUP.md`](DATABASE_SETUP.md)**.

```sql
create table hn_buzz_runs (
  id                 uuid default gen_random_uuid() primary key,
  created_at         timestamptz default now(),
  run_date           text,        -- window-start date (UTC)
  window_hours       int,         -- lookback window (default 24)
  complete           boolean default true,  -- false = partial run; excluded from velocity baseline
  leaderboard        jsonb,       -- ranked entities: score, velocity, components, top stories
  narratives         jsonb,       -- per-entity narrative, theme, tone (Week 7)
  community_opinions jsonb,       -- per-entity comment-grounded opinion (Week 9)
  raw_metrics        jsonb        -- volume, points, comments, front-page counts
);
```

## License

MIT License — see repository for full license text.

## Support

- **Email:** mali.om@northeastern.edu
- **GitHub Issues:** [Mycroft Repository Issues](https://github.com/Humanitariansai/Mycroft/issues)

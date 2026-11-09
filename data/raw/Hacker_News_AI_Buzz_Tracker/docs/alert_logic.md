# Alert logic (Week 10)

Two independent alert channels. They must stay distinct so a silent outage is
never mistaken for a quiet news day (plan.md, Phase 1 error-handling).

## 1. Entity breakout alert (content signal)

- **Trigger:** the `If` node evaluates
  `{{ $json.leaderboard.some(e => e.breakout === true) }}`.
- **`breakout`** is set per entity in `Computer Buzz Score`:
  `buzz_score >= breakoutThreshold`. Thresholds live per entity in the watchlist
  (`breakoutThreshold`: 70 for high-profile entities, 60 for smaller-profile ones
  such as Palantir, Apple Intelligence, Anthropic, Mistral).
- **Action (True branch):** send the HTML digest (`Code in Python1`) via
  `Send an Email`.
- **False branch:** no email — the snapshot and JSON signal are still written, so
  the coordination layer always has data even on a quiet day.

### Alert-fatigue tuning

- The digest fires only when **at least one** entity breaks out, not every run,
  so routine quiet days don't email.
- `breakout` uses the entity-specific `breakoutThreshold`, not a single global
  cut, so a smaller-profile entity can break out on a proportionally smaller
  score without lowering the bar for the majors.
- Sparse entities (`lowConfidence`, <3 stories) are scored on the absolute floor
  and rarely cross threshold, so a single slow-week story won't trip an alert.
- **Suggested future guard (not yet wired):** suppress a breakout alert for an
  entity that was already in breakout on the previous run (alert on the *edge*,
  not the *level*), to avoid re-alerting a multi-day story. Requires reading the
  previous snapshot's breakout state — a small extension of the existing
  `Get Previous Run` lookup.

## 2. Pipeline-failure alert (health signal)

- **Purpose:** a *separate* maintainer alert for infrastructure failure — API
  down, DB write failure, or an upstream schema/shape change — distinct from a
  legitimate "no breakouts" day.
- **Signals to alert on:**
  - a node error (HTTP non-2xx after retry, Postgres write failure), and/or
  - `complete == false` on the run row (`Build Run Row` sets
    `complete = len(leaderboard) == len(_items) and > 0`), which also excludes the
    run from the velocity baseline so a half-finished run never becomes "yesterday."
- **Wiring (human/canvas task):** attach an **Error Trigger** workflow (or the
  node-level *Error Workflow* setting) that emails the maintainer. This is a
  separate path from the breakout `Send an Email` node and should never share its
  template.

## Why two channels, not one

A breakout alert says *"something is happening in the market."* A pipeline-failure
alert says *"the sensor is broken."* Collapsing them means a broken sensor looks
like a calm market — the single most dangerous failure mode for an attention
signal. They are kept on separate triggers with separate templates.

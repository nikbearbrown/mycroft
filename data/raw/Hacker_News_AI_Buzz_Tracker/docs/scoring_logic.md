# Buzz Score Scoring Logic

## Overview

Each entity tracked in the WatchList receives a **buzzScore** in the range [0, 100] computed daily from Hacker News data. The score is a weighted sum of four components.

---

## The Four Components

| Component | Range | Source |
|---|---|---|
| Volume | 0 → 30 | Number of HN stories mentioning the entity |
| Engagement | 0 → 30 | Total points + total comments across all stories |
| Front Page | 0 → 20 | Number of times stories reached the HN front page |
| Acceleration | −20 → +40 | Change vs. the previous run (cold-start: 0 until a prior run exists) |

The first three components (**"base"**, 0–80) measure the current window in isolation.
Acceleration adds a run-over-run momentum term: `20 × clamp(Δ/prior_base, −1, 2)`, so it can
**subtract up to 20** on a sharp decline or **add up to 40** on a breakout. The final
`buzzScore = base + acceleration` is clamped to **[0, 100]**.

**Cold-start observable maximum: 80 points** (acceleration is uniformly zero until a prior run exists).

---

## Why Log Normalization

Volume and Engagement use log normalization instead of a linear scale:

```
volume_score = 30 × clamp(log(1 + storyCount) / log(1 + VOLUME_REF))
```

HN activity follows a power-law distribution — a viral story can generate 10× the points of a typical one. A linear scale would compress everything into the low end and make the score meaningless for ordinary days. The log scale compresses outliers so that going from 5 → 15 stories feels meaningfully different from going from 150 → 160 stories, which is the right intuition for "buzz."

---

## Calibration Constants

The `*_REF` constants define the input value that earns the full 30/20 points for that component. Inputs above the ref are clamped at the ceiling.

| Constant | Value | Meaning |
|---|---|---|
| `VOLUME_REF` | 30 | 30 stories/day → full volume score |
| `ENGAGEMENT_REF` | 1000 | 1000 combined points+comments → full engagement score |
| `FRONTPAGE_REF` | 5 | 5 front-page appearances → full front-page score |

### Why Fixed Constants, Not Cross-Entity Maxima

An earlier spec draft defined normalization using the busiest entity in the current run as the denominator — a relative leaderboard where every entity is scored against today's field. That approach was deliberately rejected.

Mycroft's coordination layer consumes buzz scores as a time-series signal: it computes velocity, trailing averages, and acceleration across days. A relative scale breaks this — a quiet week inflates every score and a busy week compresses them, making cross-day comparisons meaningless. An entity that scores 60 on a quiet Tuesday and 40 on a busy Friday would appear to be declining when the underlying activity was identical.

Fixed constants produce an absolute scale: the same activity always produces the same score regardless of what other entities did that day. This is what time-series comparability requires. **Do not change normalization to cross-entity maxima** — it would break velocity and acceleration computation in the live phase.

### How the Fixtures Justified These Values

Four fixture cases were used to validate that the bands are well-separated and intuitive:

| Fixture | storyCount | engagement | frontPage | lowConf | Score | Band |
|---|---|---|---|---|---|---|
| Busy | 30 | 4500 | 6 | false | 80.0 | 75–90 |
| Moderate | 10 | 600 | 1 | false | 52.7 | 40–60 |
| Sparse | 2 | 30 | 0 | true | 38.0 | < 45 |
| Zero-hit | 0 | 0 | 0 | true | 0.0 | exactly 0 |

The constants were chosen so that:
- A "busy" entity saturates volume and engagement (both hit the log ceiling) and scores ~80.
- A "moderate" entity sits clearly in the middle band without clustering near busy or zero.
- At least a 14-point gap separates each band, making the leaderboard ranking meaningful.

---

## Sparse-Entity Floor (Low-Confidence Path)

When an entity has **fewer than 3 stories** in the lookback window, the log scale becomes unreliable — a single story is too noisy to normalize against a 30-story reference. These entities are flagged `lowConfidence: true` upstream and scored on an **absolute linear scale** instead:

```
volume_score     = 30 × clamp(storyCount / 3)
engagement_score = 30 × clamp(engagement / 50)
front_page_score = 0   # suppressed entirely; one front-page hit on 1 story is noise
```

This floor path ensures sparse entities:
- Can still score nonzero (a single story with 20 points isn't worthless).
- Never outscore moderate entities due to a lucky viral hit on thin volume.
- Are visually identifiable in the output via `lowConfidence: true`.

---

## Acceleration and Velocity (Week 4 — live)

The acceleration component measures **run-over-run momentum** — how much an entity's base
score changed compared to the **previous run**. This requires a historical baseline, which is
read back from Supabase before scoring (see `DATABASE_SETUP.md`).

### Cold start

When no prior run exists for the entity (the first ever run, or an entity newly added at a
watchlist-version boundary), acceleration is a uniform hard zero:

```python
accel_score = 0.0   # coldStart = True
```

The uniformity is deliberate: every entity reads zero, so early scores are comparably
conservative rather than variably distorted. Those entities carry `coldStart: true`.

### Live computation

Once a prior run is available, acceleration compares **base score to base score**, where
`base = volume + engagement + frontPage` (the acceleration term itself is excluded on both
sides, so an entity's acceleration never compounds its own prior acceleration):

```python
prev = prev_by_entity.get(entity)          # looked up in the previous run's leaderboard
if prev is None:
    accel_score = 0.0                      # cold start (see above)
else:
    yesterday_base = base_of(prev)         # volume + engagement + frontPage from the stored snapshot
    if yesterday_base <= 0:
        accel_score = 0.0                  # zero-denominator guard: no baseline to grow from
    else:
        delta = today_base - yesterday_base
        accel_score = 20 * clamp(delta / yesterday_base, -1.0, 2.0)
```

**Negative velocity is allowed** (`clamp(..., -1.0, 2.0)`). Unlike an earlier draft that floored
acceleration at zero, the shipped model lets a declining entity lose up to 20 points and a
breakout gain up to 40 (`+200%` growth). The per-entity `velocity` field emitted in the
leaderboard **is** this acceleration value, exposed for the digest and the JSON signal.

- `delta / yesterday_base` is the fractional run-over-run change in base score.
- Bounds: `−1.0` (base collapsed to 0 → −20 points) to `+2.0` (base tripled → +40 points).
- `coldStart` flips to `false` once a prior run exists for the entity.

> **Baseline is the previous complete run, not a trailing average.** Phase 1 compares against
> the single most recent `complete` snapshot. A trailing-average baseline becomes possible once
> the Week 5 historical backfill lands, and is a candidate refinement then — but the shipped
> Phase 1 behavior is previous-run delta.

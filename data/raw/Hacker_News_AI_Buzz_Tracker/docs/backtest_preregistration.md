# Signal-Validation Backtest — Pre-Registration

**Written:** 2026-07-16 (Week 6), **before** any correlation was computed.
**Author:** Om Mali · **Watchlist version:** v1 · **Recipe:** HN AI Buzz Tracker signal validation

> Why a pre-registration exists at all: a lag window or a metric chosen *after*
> seeing which one "worked" is not evidence — it is curve-fitting. This file
> commits to the design first. `signal_validation.md` reports what that fixed
> design produced. If anything below changes after results are seen, that is a
> protocol deviation and must be logged as one in `logs/RUN_LOG.md`, not quietly
> edited here.

---

## 1. Hypothesis under test

Hacker News discussion volume for an AI entity is a **leading indicator** of that
entity's stock price move — i.e. a buzz spike in week *t* is followed by an
above-average price move in week *t+n* for some small *n*. The null is that buzz
neither leads price nor is led by it (or that any same-week association is pure
co-reaction to shared news).

## 2. Data

- **Buzz:** `backfill_output/backfill_v1.json` — 12 entities × 13 weekly runs
  (2026-04-11 → 2026-07-03), `raw_metrics.storyCount` per entity-week.
- **Price:** `backfill_output/prices_v1.json` — daily closes from Alpha Vantage
  for the **9 of 12** entities that have a public ticker (NVDA, GOOGL, MSFT,
  META, AMD, PLTR, AMZN, AAPL, TSLA). The 3 private comparables (OpenAI,
  Anthropic, Mistral) have no ticker and are **excluded from all price tests**.

> **Correction to plan.md's "~156 observations."** That figure assumed all 12
> entities. Only 9 are investable, so the price panel is at most 9 × 13 = **117
> entity-weeks**, and fewer after lag trimming (below). This is stated here so
> the report does not imply a larger sample than exists.

## 3. Variables (fixed here, not after results)

- **Buzz variable `bz(t)`** = `storyCount` for the entity in week *t*,
  **z-scored within that entity** across its 13 weeks: `(x − mean_i) / std_i`.
  - *Why storyCount:* it is point-in-time safe. Algolia returns *current*
    point/comment totals at fetch time, so a backfilled week's `totalPoints` /
    `totalComments` reflect activity accrued up to today — a look-ahead leak
    (Week 5 finding). A story's existence and post date are fixed, so
    `storyCount` has no such leak. Points/comments are **secondary only** and
    carry this caveat wherever shown.
  - *Why within-entity z-score:* it captures a "spike relative to that entity's
    own baseline" (Anthropic ~316 stories/wk vs. Tesla ~1.2/wk are not
    comparable in raw units), which is what "buzz spike" means, and it makes
    entities poolable.
- **Price variable `r(t)`** = weekly **log return** `ln(P(t) / P(t−1))`, where
  `P(t)` is the closing price on the **last trading day at or before** the week's
  `run_date` (handles weekends and the 2026-07-03 market holiday). Also
  **z-scored within entity** before pooling.
  - *Why returns, not price levels:* price levels are non-stationary (trending),
    which manufactures spurious correlation. Returns are the actual "price move"
    the hypothesis is about.
  - *Why z-score returns too:* so a high-volatility name (e.g. PLTR) does not
    dominate the pooled variance; each entity contributes comparably (a within
    estimator).

## 4. Pre-registered lag windows and test family

Weekly steps are indexed by the 13 `run_date`s (treated as one week apart).

**Forward — does buzz lead price?** `corr( bz(t), r(t+n) )` for:
- `n = 0` — same week (co-movement; *not* predictive, included as a baseline)
- `n = 1` — 1-week lead
- `n = 2` — 2-week lead
- `n = 4` — 4-week lead

**Reverse — does price lead buzz (shared-cause / buzz-lags check)?**
`corr( r(t), bz(t+n) )` for:
- `n = 1`, `n = 2`, `n = 4` (reverse `n = 0` is identical to forward `n = 0`)

**Family size = 7 tests.** No other lags will be tested; adding one later is a
protocol deviation.

## 5. Test statistic and multiple-comparison correction

- **Statistic:** Pearson correlation `r` on the pooled panel (all entity-weeks
  stacked), two-sided p-value. Pairwise deletion of NaNs per lag (weeks with no
  `t−1` or no `t+n` within the 13-week window are dropped for that lag only).
- **Correction:** **Benjamini-Hochberg FDR** at `q = 0.05` across all 7 tests,
  via `statsmodels.stats.multitest.multipletests(method="fdr_bh")`. Testing
  several lags inflates the chance of a spurious "hit"; BH controls the expected
  false-discovery rate across the family.

## 6. Primary vs. exploratory

- **Primary:** the pooled-panel Pearson tests in §4–5. These are the only tests
  that carry an inferential claim.
- **Exploratory / descriptive only:** per-entity correlations (9 entities × the
  lag set). With 13 weekly points each, per-entity power is far too low to
  validate individually; they are reported for color, not as evidence, and are
  **not** FDR-corrected as confirmatory results.

## 7. Interpretation rules (committed in advance)

| Pattern across FDR-surviving tests | Reading |
|---|---|
| Forward lead (`n≥1`) survives, reverse does **not** | Evidence buzz **leads** price (supports thesis) |
| Reverse survives, forward lead does **not** | Buzz **lags** price (thesis downgraded) |
| Both survive at similar `|r|` | **Shared cause** (co-reaction to news), not prediction |
| Only same-week (`n=0`) survives | Contemporaneous co-reaction, not a leading signal |
| Nothing survives | No detectable lead-lag at this sample size |

## 8. Weight-tuning decision rule (pre-committed)

Per plan.md, the backtest is supposed to decide whether to tune the Buzz Score
weights (vs. keeping the uniform-ish initial weights). Decision rule, fixed now:

> **Tune weights only if** the pooled **forward** buzz→price lead at `n≥1`
> **survives FDR** *and* has practically meaningful strength `|r| ≥ 0.20` *and*
> is stronger than the reverse direction at the same lag. Otherwise, **keep the
> initial weights unchanged** — there is no validated target to tune toward, and
> tuning to a null result would be overfitting.

## 9. Known limitations (disclosed up front, not after)

1. **Survivorship bias.** The v1 watchlist was chosen with present-day knowledge
   of which AI entities matter; results describe correlation among entities
   known *today* to be relevant, not a blind historical universe.
2. **Serial autocorrelation.** Buzz levels are autocorrelated week to week, so
   pooled Pearson p-values are **optimistic** (effective N < nominal N). p-values
   are treated as descriptive, not exact; the direction/consistency of the sign
   matters more than a threshold cross.
3. **Small sample.** 13 weeks, 9 tickers, shrinking with lag — low power. A null
   result is "not detected here," not "proven absent."
4. **Points/comments look-ahead** (see §3) — excluded from the primary test.

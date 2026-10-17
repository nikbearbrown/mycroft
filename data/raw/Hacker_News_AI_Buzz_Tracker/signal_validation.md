# Signal Validation Backtest — Does HN Buzz Lead Price?

**Date:** 2026-07-16 (Week 6, early Phase 2) · **Author:** Om Mali
**Watchlist:** v1 · **Buzz data:** `backfill_output/backfill_v1.json` (12 entities × 13 weeks, 2026-04-11 → 2026-07-03)
**Price data:** `backfill_output/prices_v1.json` (Alpha Vantage daily closes, 9 public tickers)
**Reproduce:** `python run_backtest.py` → `backfill_output/backtest_results.json`

---

## TL;DR (the honest verdict)

**No evidence that Hacker News buzz leads price at this sample size.** Across the
pre-registered lag family, **zero of seven tests survive Benjamini-Hochberg FDR
correction.** The forward "buzz leads price" correlations (1-, 2-, 4-week leads)
are all statistically indistinguishable from zero and, if anything, slightly
*negative*. The single largest raw correlation points the **reverse** way —
price(t) → buzz(t+2), r = 0.23 — which, even though it too fails FDR, is more
consistent with buzz **reacting to** price-moving news than **predicting** it.

**Consequence:** the investment framing ("buzz is a leading indicator") is **not
supported** by this backtest and is downgraded to *unproven*. Per the
pre-committed decision rule, **the Buzz Score weights are left unchanged** — there
is no validated target to tune them toward.

This is the "building to learn" outcome the plan anticipated: we tested the
thesis rather than assuming it, and the test came back null. That is a result,
not a failure.

---

## 1. The design was fixed before any number was computed

The full pre-registration is in [`docs/backtest_preregistration.md`](docs/backtest_preregistration.md),
written and committed **before** correlations were run. In brief:

- **Buzz variable** `bz(t)` = `storyCount`, z-scored **within each entity**.
  `storyCount` is the primary metric because it is point-in-time safe;
  `totalPoints`/`totalComments` are not (Algolia returns *current* totals at
  fetch time, a look-ahead leak — Week 5 finding). Within-entity z-scoring
  captures "spike vs. the entity's own baseline" and lets entities of wildly
  different scale (Anthropic ~316 stories/wk vs. Tesla ~1.2) be pooled.
- **Price variable** `r(t)` = weekly **log return** `ln(P(t)/P(t−1))`,
  z-scored within entity. Returns (not price levels) because levels trend and
  would manufacture spurious correlation. `P(t)` = last close at/before the
  week's `run_date` (handles weekends and the 2026-07-03 market holiday).
- **Lag family (7 tests):** forward `corr(bz(t), r(t+n))` for n ∈ {0,1,2,4};
  reverse `corr(r(t), bz(t+n))` for n ∈ {1,2,4}.
- **Statistic:** pooled-panel Pearson r; **Benjamini-Hochberg FDR at q = 0.05**
  across all 7 tests.
- **Primary = pooled panel; per-entity = descriptive only.**

## 2. Primary result — pooled panel (9 public-ticker entities)

Entities pooled: NVDA, GOOGL, MSFT, META, AMD, PLTR, AMZN, AAPL, TSLA.
(OpenAI, Anthropic, Mistral are private — no ticker — and are excluded from all
price tests. This is why the panel is **9**, not the 12 in plan.md.)

| Direction | Lag | Pearson r | p-value | BH q-value | Survives FDR? | N pairs |
|---|---|---|---|---|---|---|
| buzz → price | same-week (n=0) | +0.123 | 0.205 | 0.416 | no | 108 |
| buzz → price | 1-week lead | −0.115 | 0.238 | 0.416 | no | 108 |
| buzz → price | 2-week lead | −0.058 | 0.572 | 0.800 | no | 99 |
| buzz → price | 4-week lead | −0.020 | 0.862 | 0.866 | no | 81 |
| price → buzz | 1-week | +0.017 | 0.866 | 0.866 | no | 99 |
| price → buzz | 2-week | **+0.233** | 0.027 | 0.187 | **no** | 90 |
| price → buzz | 4-week | −0.150 | 0.209 | 0.416 | no | 72 |

**Reading it against the pre-registered interpretation table:**

- **Forward leads (n ≥ 1) are ~0 or negative.** There is no leading-indicator
  signal. A buzz spike this week tells you essentially nothing — and if anything
  marginally the *opposite* — about next week's return.
- **The one nominally "significant" cell (price→buzz, 2-week, p = 0.027) does not
  survive FDR** (q = 0.19). With 7 tests, one raw p ≈ 0.03 is expected by chance;
  BH correctly refuses to promote it. Its *direction* (price leading buzz) is the
  reverse of the thesis, i.e. it hints at buzz being a lagging co-reaction, not a
  predictor — but it is not strong enough to claim even that.
- **Same-week (n=0) is +0.12, not significant.** Even contemporaneous
  co-movement is weak here.

**Bottom line:** the pattern matches the "nothing survives" row of the
pre-registered interpretation table. → *No detectable lead-lag relationship at
this sample size.*

## 3. Secondary metric (totalPoints) — flagged, not confirmatory

For completeness the same 7 tests were run on `totalPoints`. **This metric is not
point-in-time safe** (look-ahead leak, §1), so it is descriptive only and is
**not** FDR-corrected. It tells the same story: all forward correlations ≈ 0
(max |r| = 0.07), reverse correlations slightly positive but non-significant
(max r = 0.19 at 4-week). It does not change the verdict. Full numbers in
`backtest_results.json` under `secondary_caveated`.

## 4. Per-entity correlations (exploratory / descriptive ONLY — not validated)

Per plan.md these are reported for color, **not** as evidence: 13 weekly points
per entity is far too few to validate any single entity, and running 9 entities ×
7 lags = 63 tests guarantees a few "significant"-looking hits by chance.

- **Forward 1-week lead ranges from −0.46 (MSFT) to +0.50 (TSLA)** with the
  signs canceling out — no consistent cross-entity direction, none significant
  after accounting for how many were tried.
- The largest single per-entity correlation is **GOOGL price→buzz 2-week,
  r = 0.75 (p = 0.013)** — but that is 1 of 63 exploratory tests (≈3 expected
  below p=0.05 by chance) and is again in the *reverse* direction. Treat as noise.

Full per-entity table: `backtest_results.json` → `primary.per_entity`.

## 5. Limitations (disclosed, per the pre-registration)

1. **Survivorship bias — explicit.** The v1 watchlist was chosen with *present-day*
   knowledge of which AI entities matter. This backtest measures correlation among
   entities known *today* to be relevant, **not** a blind historical universe. A
   truly leading signal could be hidden in entities we would only have added after
   they mattered, and conversely today's "obvious" names may correlate for reasons
   unrelated to the signal's real-time usefulness.
2. **Serial autocorrelation → optimistic p-values.** Buzz levels are
   autocorrelated week to week, so the effective sample is smaller than the
   nominal N and the reported p-values are *optimistic* — biased **downward, toward
   significance** (a lowered bar for rejecting the null). The forward leads fail to
   clear even that lowered bar, so a proper autocorrelation-robust test (which would
   push the p-values **up**) would leave them **more** clearly null, not less. In
   other words the bias runs *against* the null, yet the null still holds — which
   makes the null verdict more secure, not less. (Same logic weakens the one
   nominally-significant cell, reverse n=2, further.)
3. **Small sample / low power.** 13 weeks, 9 tickers, shrinking with lag (down to
   N=72 at the 4-week reverse lag). A null here means "not detected in this
   window," **not** "proven absent." A larger backfill (more weeks) could still
   surface a weak effect.
4. **`totalPoints`/`totalComments` look-ahead** — excluded from the primary test
   (§1, §3).

## 6. Weight-tuning decision (pre-committed rule applied)

The pre-registration (§8) committed the rule in advance:

> Tune weights only if the pooled **forward** buzz→price lead at n ≥ 1 **survives
> FDR** *and* |r| ≥ 0.20 *and* is stronger than the reverse direction. Otherwise,
> keep the initial weights.

**Outcome:** no forward lead survives FDR; the largest forward |r| at n ≥ 1 is
0.115 (below the 0.20 floor); and the strongest signal is in the reverse
direction. **Decision: keep the Buzz Score's initial weights unchanged**
(Volume 30 / Engagement 30 / Front-page 20 / Acceleration 20). Tuning them to fit
a null result would be overfitting to noise. The weights remain "explicit initial
choices, not validated parameters," exactly as plan.md framed them — the backtest
did not license promoting them to "validated."

**Re-evaluation trigger:** revisit this decision when the backfill covers
materially more weeks (e.g. ≥ 26), which would give the pooled panel enough power
to detect a weak effect if one exists.

## 7. What this means for the project

- The Buzz Score stays a **descriptive attention metric**, not a claimed
  price-leading signal. The digest/leaderboard framing should describe *how much
  attention* an entity is getting — not imply it predicts the stock.
- The coordination layer should consume the JSON signal as one *attention* input
  among many, **not** weight it as a validated alpha source.
- This is a clean, honest negative result and should be presented as such in the
  Month 2 milestone PR.

---

### Open risk carried from Week 5 (not blocking Week 6)

`watchlist_version` is still only metadata on the backfill table; the live
`hn_buzz_runs` table has no such column and the velocity lookup has no version
check. Per the Week 5 notes this **must be resolved before the Week 11 watchlist
v2 expansion**, but it does not affect this week's backtest (which reads the
backfill table directly).

### Artifacts

- `docs/backtest_preregistration.md` — the pre-registered design (written first)
- `fetch_prices.py` — Alpha Vantage price pull (rate-limit-aware, cached)
- `run_backtest.py` — the backtest (implements the pre-registration exactly)
- `backfill_output/prices_v1.json` — fetched daily closes (9 tickers)
- `backfill_output/backtest_results.json` — full pooled + per-entity numbers

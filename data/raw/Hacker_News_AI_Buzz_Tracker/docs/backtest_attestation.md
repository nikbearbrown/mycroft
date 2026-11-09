# Attestation — Signal-Validation Backtest (Week 6)

- Artifact: `signal_validation.md` + `run_backtest.py` + `docs/backtest_preregistration.md`
- Data: `backfill_output/backfill_v1.json`, `backfill_output/prices_v1.json`
- Watchlist: v1 · Recipe version: Week 6 signal-validation backtest
- By: **Om Mali** · **2026-07-16**

> Attestation is the human record of having judged the running system (SNICKERDOODLE
> Verification Stack, layer 3). Machine conformance already passed (scripts run, JSON
> valid); this record is the human adequacy judgment. There is no "PASS" field — this
> record is the justification.

## Tested

| Ran | Saw | Expected |
|---|---|---|
| `python run_backtest.py` on my own machine | 0 of 7 pooled tests survive BH-FDR; every r/p/q value matches the table in `signal_validation.md` exactly (e.g. fwd n=0 r=0.123 p=0.205 q=0.416; rev n=2 r=0.233 p=0.027 q=0.187) | Reproducible; report reflects the actual run, no invented numbers |
| Hand-checked one entity-week: NVIDIA, run_date 2026-04-17 | `storyCount = 31` in the backfill (leaderboard row and `raw_metrics` agree); NVDA close = 201.68 in `prices_v1.json` for the same date | Report/backtest read the source files as-is, no fabricated values |
| Break attempt — are the private (non-ticker) entities leaking into the price test? | Pooled panel prints **9** entities (NVDA, GOOGL, MSFT, META, AMD, PLTR, AMZN, AAPL, TSLA); OpenAI, Anthropic, Mistral excluded | Only the 9 public-ticker entities are tested; matches the report's "9 not 12" correction |
| Break attempt — does the market-holiday date break the price lookup? | run_date 2026-07-03 (July-4 holiday, no bar) falls back to the 2026-07-02 close (194.83), not a NaN or a wrong date | "last close at/before run_date" lookup works on non-trading days |
| Read the pre-registration date vs. the results | `docs/backtest_preregistration.md` fixes lags/metric/FDR/decision-rule and is dated before the results were computed | Design was pre-registered, not chosen after seeing what "worked" |

## Did not test

- Whether Alpha Vantage `TIME_SERIES_DAILY` "close" is split/dividend-adjusted. It is the
  raw close, so a stock split inside the 13-week window could distort that entity's weekly
  return. Not checked against a corporate-actions source.
- Longer horizons or more weeks. The sample is only 13 weeks × 9 tickers (shrinking with
  lag), so this is low power — a null here means "not detected in this window," not "absent."
- The per-entity correlations. They are exploratory/descriptive only and were not
  individually validated (accepted as such, per the pre-registration).
- The optimistic-p-value caveat (serial autocorrelation) was not quantified with a
  block-bootstrap or cluster-robust test; it is disclosed in the report and only cuts
  toward the null, so it does not change the verdict.

## Broke during testing, fixed

- None. The run reproduced cleanly and the spot-checked values matched the source data.

## Judgment

The design is sound and was genuinely pre-registered; the numbers reproduce; the two
hand-checks and two break-attempts hold. I accept the **null verdict** (no evidence HN buzz
leads price at this sample size) and the **decision to keep the Buzz Score weights unchanged**
as adequate for Week 6. The investment framing is honestly downgraded to *unproven*, to be
re-tested when the backfill reaches ≥26 weeks.

**[GATE CLEARED]** — Om Mali, 2026-07-16.

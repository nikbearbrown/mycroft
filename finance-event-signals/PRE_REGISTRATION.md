# Pre-registration — finance-event-signals

**Purpose:** fix what "working" and "accurate" mean *before* the grading loop runs, so results
cannot be reshaped after the fact to look good (P8). Extend this file (append, do not rewrite)
before each week's measurement.

---

## Week 1 — data spine (committed before `make up`)

Date committed: 2026-08-30

### Predictions (what a correct Week-1 run looks like)

| Check | Prediction |
|---|---|
| gateway first cycle | `fetched > 0`; hundreds of 8-Ks over a 1-day lookback |
| overlap between sources | some events appear in **both** `edgar_fts` and `edgar_atom` → dedup drops the second |
| steady state | after ~2 cycles, `published` per cycle drops toward 0 (most events already seen), `dupes` rises |
| Postgres | `SELECT count(*) FROM events` climbs on cycle 1, then plateaus |
| sources present | `SELECT source, count(*) FROM events GROUP BY source` shows both `edgar_fts` and `edgar_atom` |

### Break-test predictions (what SHOULD happen on bad input / failure)

| Scenario | Expected |
|---|---|
| `EDGAR_USER_AGENT` unset | WARN logged; SEC may 403 → `fetchFTS`/`fetchAtom` error logged; **no fabricated events**; next cycle retries |
| kill `persistence-svc` mid-batch, restart | offsets not committed past the failure → batch reprocessed → **zero duplicate rows** (`ON CONFLICT DO NOTHING`) |
| malformed JSON on `events.raw` | `enrichment-svc` logs `bad_json`, commits past it, keeps running |
| Redis down | gateway exits non-zero on startup ping (fail fast); no partial state |
| SEC returns 429 | request returns status 429 to caller → cycle logs the error → token bucket already limits us well under 10/s |

### What would FALSIFY the Week-1 spine

- a duplicate `event_key` row in `events` after any restart
- the gateway writing an event with an empty `event_key`
- an event on `events.enriched` missing the `raw` provenance object
- the pipeline continuing to "succeed" while a source has been erroring for >5 cycles

### After the run

Record actual vs. predicted in `logs/RUN_LOG.md`. Any mismatch is investigated and explained,
never silently corrected.

---

## Week 4 — grading accuracy (to be committed before `outcome-grader` first runs)

_Predicted precision by `event_type`, expected withhold-rate, and the falsification criterion
("withhold-rate ≈ 0% while grading accuracy is at chance") go here — before any signal is
graded._

---

## Week 2 — GIGO gate + agent + human gate

> Documented **after** the Week-2 build (not a true pre-registration — Week 2 has no
> measured accuracy claim, only pass/fail gate checks). Recorded here for the log. The
> binding pre-registration is Week 4, below, and must be committed before the grader runs.

### Gate checks (all must pass to call Week 2 done)

| Check | Expected |
|---|---|
| malformed / stale / missing-field event | -> `events.deadletter` with a specific `reject_reason`; envelope preserved; never silently dropped |
| agent on an ambiguous filing | `signal.status = "withheld"` with a reason; **never** a fabricated direction |
| `ClearGate` without a reviewer | rejected (400 / InvalidArgument) |
| `ClearGate` with a reviewer | `gate_decisions` row written; `signals.status` flips; event on `events.actionable` |
| second `ClearGate` on same signal | rejected (409 / FailedPrecondition) |
| invariant | zero `signals` with `status='actionable'` and no `gate_decisions` row |
| graph branch tests | 6/6 (emit, self-consistency-withhold, unclear-withhold, low-conf-withhold, verify-withhold, classify) — run in the image build |

### FALSIFY Week 2 if

- any message on `events.actionable` without a matching `gate_decisions` row
- the agent emits a non-`unclear` direction on a filing whose metadata does not support one
- a rejected event vanishes (not on `events.deadletter`, not processed)
- `ClearGate` succeeds without a reviewer name

---

## Week 4 — grading accuracy  *(BINDING — committed before `outcome-grader` first runs)*

Date committed: 2026-08-30, before `services/outcome-grader` was written or executed.

### Live state this prediction is made against

- `LLM_PROVIDER=deterministic` for every signal in scope (no `ANTHROPIC_API_KEY` set this run).
- 26 signals were in `pending_review`. **I reviewed each one by hand** (real gate decisions,
  reviewer `sachin`, logged in `gate_decisions`): 19 cleared **actionable** (17 delisting +
  2 bankruptcy, all confidence 0.85 — Nasdaq/exchange deficiency and bankruptcy notices are
  well-established negative catalysts), 7 **rejected** (confidence 0.6 — agreement
  terminations, restructuring costs, an auditor change, a debt acceleration — genuinely
  ambiguous without reading the full filing text; I did not trust the machine's "down" read
  enough to act on it). This is the honest reviewer judgment call, not a rubber stamp — see
  `logs/RUN_LOG.md` Week 4 entry for the per-signal notes.
- Sanity check against Yahoo Finance (`query1.finance.yahoo.com/v8/finance/chart`) confirms
  the most recent available daily close, as of this commit, is **2026-08-28** (Friday) — 08-29
  and 08-30 are the weekend.

### Grading rule (fixed now, not adjustable after seeing results)

- `price_at_publish` = the closing price on the trading day at-or-before the signal's
  `published_at` date.
- `price_after` = the close **1 trading day** after `price_at_publish`'s date (`holding_days=1`,
  chosen because these are same-week filings — a longer window is future work, not retrofitted
  here).
- `realized_direction` = `down` if `pct_move <= -0.5%`, `up` if `>= +0.5%`, else `flat`
  (dead zone to avoid grading noise as a directional call).
- A signal is **gradeable only if both bars exist** in the fetched history. Given the
  Aug-28 ceiling above: the 6 actionable signals published **2026-08-27** (SOBR, BCAB, BBCQU,
  LTRYW, ONFO, RNTX) ARE gradeable now (Aug-28 close exists). The other 13 actionable signals
  published **2026-08-28** are **NOT YET gradeable** — their `price_after` bar (2026-08-31)
  doesn't exist yet. The grader must report these as `pending — insufficient time elapsed`,
  **never** impute or guess a value for them (P3).

### Predictions

| Scope | Prediction |
|---|---|
| gradeable now (6 signals, Aug-27 filings) | predicted precision on "down" calls: **>= 4/6 correct** — delisting notices are close to consensus-negative, so I expect the agent's blanket "down" read to hold most of the time, not because the model is calibrated but because the event class itself is one-sided |
| not-yet-gradeable (13 signals, Aug-28 filings) | grader marks all 13 `pending`, `correct = NULL`, with `grading_note = "insufficient time elapsed"` — **zero** of these should get a real correct/incorrect value on this run |
| rejected signals (7) | **excluded from grading entirely** — a rejected signal never became actionable, so there is nothing to score; the grader must not touch `status='rejected'` rows |
| overall accuracy figure | **not to be quoted as "the system's accuracy"** — n=6 gradeable is not a sample size anyone should generalize from; the scorecard must say so explicitly |

### FALSIFY Week 4 if

- the grader reports a `correct` value for any Aug-28-published signal on this run (would mean
  it fabricated or misdated the "after" price)
- the grader silently drops a signal instead of marking it `pending`
- the scorecard implies a general accuracy claim from n=6
- `withhold-rate ~= 0%` while graded accuracy is at chance (would suggest the deterministic
  provider stopped being conservative without anyone changing it)

### After the run

Record actual vs. predicted in `logs/RUN_LOG.md`. Any signal that grades differently than
predicted gets named, not smoothed over.

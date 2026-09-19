# Private AI Valuation Agent

Most of the AI sector's value sits in companies you cannot buy and cannot see into — OpenAI,
Anthropic, xAI, Databricks, Anduril. No ticker, no earnings call, no 10-K.

But US registered funds must disclose **every** portfolio position on SEC Form N-PORT,
including private ones, with a dollar value and a share count. Divide one by the other and
you have a price per share for a company with no public price.

This project reads those filings and turns them into an open, reproducible price history —
and measures how a new valuation **propagates** across independent fund managers, which is
possible because fund fiscal quarter-ends are staggered across the calendar.

## Status

**Week 8 complete — four measurements, and two of them contradict the plan's own
expectations.** `docs/findings.md` is generated from the panel; every figure traces to a filed
holding.

| | measured | plan.md expected |
|---|---|---|
| Consecutive observations unchanged | **25.0%** | 30–40% |
| Same-date spread across managers, median | **10.8%** | "they mostly don't disagree" |
| A new price level reaching half its holders | **30 days** | not quantified |
| Cerebras Level 3 → Level 1 event study | **not runnable** | "free, clean, no additional data" |

**Marks move more often than the thesis assumed** — 75% of consecutive observations change,
and the result survives treating any move under 1% as flat (29.6%). It varies enormously by
company: Anthropic and OpenAI re-mark at nearly every observation, X.AI and SpaceX carry
forward a third to a half of the time.

**Managers on the same date disagree by a median of 10.8%, but 92 of 130 same-date groups
contain more than one price level** — so the disagreement is mostly about which round has been
reflected, not what a round is worth. That is propagation seen side-on, and the propagation
measurement confirms it: **half the eventual holders of a new level report it within a month,
and for the largest events — Databricks at $190.00 across 20 managers, OpenAI at $687.6869
across 12 — half of them report it on the same period end.**

**The Cerebras event study cannot be run, for two structural reasons** rather than an
oversight: the private layer is filtered to Level 3, so Level 1 rows never entered the
database; and the Level 1 observation's period end is in unpublished 2026Q3. The measurable
Level 3 run-up is reported instead: $21.46 to $100.26, +367%.

**The harness is built and tested anyway**, so the study runs itself when the archive catches
up. Scanning all fourteen quarters at every fair value level found 10,566 non-Level-3 rows and
**zero genuine Level 1 observations** — 10,126 of them are false positives, every one of the
7,175 Level 1 rows being **Coherent Corp** caught by the `%COHERE%` canary. That is a finding
in its own right: the Level 3 filter had been doing double duty as a *precision* filter, and
the public lane must route through the matcher rather than the frozen name patterns.

**Week 7 complete — the marks panel is built, and the split detector caught a real split
before it entered a price series.** `price_per_share = value_usd / balance`, computed once
per security, fund and period end: **5,479 marks** over 232 securities, 55 period ends and
861 company/manager/period rows. Every filed holding reconciles — 5,806 = 28 rejected in
Week 6 + 72 superseded by amendments + 5,706 aggregated into marks. Nothing is dropped for
being awkward.

| | marks |
|---|---|
| Priced | 5,185 |
| Unpriced on purpose | 294 |
| Blocked from any change series | 305 |
| Re-marked against the prior period | 3,067 |
| Carried forward unchanged | 1,019 |

**Six of `plan.md`'s seven end-to-end checks pass and the seventh is unreachable, not
failed.** The Anthropic Fidelity position reproduces to the cent from accession
`0000035402-26-003406` (46,814 shares, $12,131,380, $259.14); **ten** manager families agree
at $259.14 where the plan expected four; Perplexity's 695 → 58 is flagged and quarantined;
SpaceX's 10x is recorded as a unit artifact with no price published; World Labs Series C and
C Prime stay apart. The ~$589 pair sits in 2026Q3, which the SEC has not published.

**All three suspected splits are adjudicated** by Om Mali on 2026-09-11, and the share count
settled every one. Perplexity is a real 10:1 split — five T. Rowe Price funds show the share
count multiplied by exactly ten with the value unchanged to the cent. Anthropic is not: ARK
holds 89,078 shares in all thirteen periods and the 4.02 rise reverses the next quarter.
SpaceX is not: share counts constant while value doubles exactly.

One case is worth the detail. ARK's Perplexity step reads **11.93** because a 10:1 split and a
16% markdown fell in the same period. The adjudicated factor is **10**; dividing by 11.93 would
erase a real price move, which is why the panel records the adjudicated factor separately from
the detected ratio.

**The split rule was wrong and is now corrected.** Week 6 used an absolute window that
missed `plan.md`'s own verification case — a ratio of 11.93 against a window of ±0.02 around
12. Both the queue trigger and the detector now share one relative 1% rule under a cap of 20.
Read [`docs/marks_panel.md`](docs/marks_panel.md).

**Week 6 complete — the review queue was built, run, and worked to empty. Every one of the
5,806 universe holdings now carries a resolution decision.** A LangGraph graph with a
Postgres checkpointer resolves what it can and stops at what it cannot, holding the paused
state in the database rather than in a process.

| | holdings | share |
|---|---|---|
| Decided without a human | **4,537** | 78.1% |
| Decided by a human | **1,269** | 21.9% |
| Undecided | **0** | — |

42 paused cards collapsed to **8 actual questions**, answered in seven commands by Om Mali on
2026-09-04. One answer retires a whole group: X.AI alone reached the queue under 24 spellings,
and the answer is recorded against the company so a 25th spelling never asks again.

Two things the queue caught on its own. The 28 `%COHERE%` canary holdings that Week 4 logged
as contaminating the universe layer arrived as the only `unresolved` trigger and are now
formally rejected. And **a genuine 10:1 stock split** in Perplexity — share count 6,081 →
60,810 with the dollar value unchanged at $4,228,994 — caught before it could enter a price
series as a 90% crash. The SpaceX and Anthropic steps that looked similar are *not* splits,
and §10.8 says why for each.

Every decision is now a regression test: a later matcher change that would overturn a human
answer fails a test instead of silently winning. The working is in
[`docs/entity_resolution.md`](docs/entity_resolution.md) §10.

These numbers are from **Supabase Postgres 17.6**, the project's own database. The queue
was first built against a local stand-in while Supabase was unreachable, and re-running it
on the real server reproduced every count exactly — same 231 questions, same 189
auto-accepts, same 8 open questions — with no state migrated. That is what a deterministic
graph is for.

**Week 5 complete — a local LLM was measured against the matcher and not adopted.** An 8B
model (`llama3.1:8b`, Q4_K_M, local) given the same evidence **costs 5.1 points of
precision**: it fixed one holding and broke fourteen, every break a resemblance promoted to a
company — `HYPERSCALE DATA INC` to Scale AI, a Fidelity internal security code to X.AI. Its
confidence was 1.000 on 315 of 322 answers, and 12 of the 15 answers that disagree with the
label came back at 0.95 or above, so it cannot even be used to triage a review queue. 3.2 s per call, zero failures. Full working in
[`docs/entity_resolution.md`](docs/entity_resolution.md) §9.

| System | Precision | Recall | F1 |
|---|---|---|---|
| **Deterministic matcher v1** | **0.9959** | **1.0000** | **0.9979** |
| + LLM in the review band | 0.9449 | 1.0000 | 0.9717 |
| LLM alone | 0.9447 | 0.9958 | 0.9696 |

`plan.md` wrote the rule for this case — *"if there is no lift, keep the deterministic matcher
and say so"* — so that is what happens.

**Week 4 complete — golden set labelled, attested in part, and the matcher baseline
measured.** 322 labelled issuer strings covering 7,276 holdings, in
[`tests/fixtures/golden_set_v1.json`](tests/fixtures/golden_set_v1.json). A human has
attested to **8 of them**; the other 314 have not been reviewed by anyone. See
[`docs/entity_resolution.md`](docs/entity_resolution.md) §6 and §8.

Two systems scored on the same labels:

| System | Precision | Recall | Errors |
|---|---|---|---|
| Frozen Week 2 name patterns | 0.9916 | 0.9792 | 2 false positives, 5 false negatives |
| Deterministic matcher v1 | **0.9959** | **1.0000** | 1 false positive |

Net: 85 wrongly-missed holdings and 28 wrongly-included ones removed, one wrongly-included
one introduced. The `%X.AI%` pattern was missing Fidelity's `XAI CORP` spelling — 85
holdings, and Fidelity is X.AI's largest holder.

**The attestation immediately reversed one label, which is the best evidence the process
works.** `OPENAIR.COM` had been labelled "not one of ours" on a reason that was factually
wrong; it is five BlackRock and New York Life holdings titled `OpenAir.com, Series C` at
687.6869, which is OpenAI's Series C consensus to four decimals. Matcher v1 had been
throwing it away — worse than the frozen patterns on that row — and the fix is in §2.

The confidence threshold is a **band, not a number**: the only false positive scores 0.80
and so do three *correct* blended SpaceX SPVs, so nothing separates them. Auto-accept at
≥ 0.90, review 0.80–0.90 (4 issuer strings per full re-resolution), reject below.

**Week 3 is only half done.** The deterministic matcher exists because Week 4's metrics
require it; the live EDGAR current-quarter path does not, so no current-quarter filing has
been through this matcher.

**Week 2 complete — 14 quarters ingested and loaded.** Gate cleared 2026-08-15.
See [`docs/worklog.md`](docs/worklog.md).

80,571,213 source holding rows across 2023Q1–2026Q2, reconciling exactly at every
boundary down to 5,806 universe marks in Postgres. The Anthropic series runs 33 period
ends from 2023-04-28 to 2026-04-30, and **43 distinct registrant CIKs** reproduce the
$259.14 mark that Week 1 verified by hand on six.

```
$ python scripts/reconcile.py --db

  quarter    source rows    private  universe   as-of window
  2023q1       6,255,353  2,323,449       187   2022-11-30 .. 2023-01-31
  ...
  2026q2       5,347,869    693,951       948   2025-07-31 .. 2026-04-30
  TOTAL       80,571,213 22,041,937     5,806

  raw_holdings 5,806   funds 183   filings 1,512   (PostgreSQL 17.6)
```

Period ends land in **12 of 12 calendar months**, which is what makes propagation
lag measurable at all.

**Week 1 — feasibility verified.** See [`docs/feasibility.md`](docs/feasibility.md).
19 Anthropic PBC positions across 6 fund families, verified by hand from EDGAR.

```
$ python scripts/verify_week1_marks.py

  2026-03-31  Fidelity, T. Rowe Price    259.1364, 259.1400   spread 0.0014%
  2026-04-30  ARK, Alger                 259.1364, 259.1400   spread 0.0014%
  2026-05-29  BlackRock                  589.0095
  2026-05-31  Capital Group              589.0095
```

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows
pip install -r requirements.txt

cp .env.example .env            # then fill it in
```

The SEC requires a real name and email in the `User-Agent` header; requests without one
return HTTP 403. Set `EDGAR_NAME` and `EDGAR_EMAIL`. For the database, see
[`DATABASE_SETUP.md`](DATABASE_SETUP.md) — `DATABASE_URL` must be the Postgres **URI**,
not the Supabase project URL.

## Running it

```bash
python -m src.ingest.download_bulk 2026q2    # ~450 MB, resumable
python -m src.ingest.build_parquet --all     # 14 quarters -> Parquet
python -m src.db.connect                     # create the schema
python -m src.db.load --all                  # Parquet -> Postgres
python scripts/reconcile.py                  # the reconciliation table
python scripts/check_fund_complexes.py       # who actually holds the universe

python -m scripts.build_golden_candidates    # the golden-set sampling frame
python -m scripts.label_golden_set           # frame -> labelled fixture
python -m scripts.score_matcher              # precision, recall, threshold sweep

python -m scripts.run_adjudication --check   # is a local model reachable
python -m scripts.run_adjudication --run     # call it, cache every reply
python -m scripts.run_adjudication --score   # lift and throughput, from the cache

python -m scripts.review_queue --run         # resolve what can be resolved; pause the rest
python -m scripts.review_queue --status      # what was decided, and by what method
python -m scripts.review_queue --report      # the queue as Markdown, for a human
python -m scripts.review_queue --list        # what is waiting
python -m scripts.review_queue --show 3      # one review card in full
python -m scripts.review_queue --decide 3 \
    --verdict company --company "Databricks, Inc." \
    --reviewer "<your name>" --rationale "<why>"
python -m scripts.review_queue --export-fixture   # decisions -> regression tests

python -m scripts.build_marks --build        # securities, marks, split detector
python -m scripts.build_marks --verify       # plan.md's end-to-end checks
python -m scripts.build_marks --panel        # company / manager / period
python -m scripts.build_marks --report       # docs/marks_panel.md, for a human

python -m scripts.analyze --run              # the four Week 8 measurements
python -m scripts.analyze --findings         # docs/findings.md, for a human

pytest -q                                    # 189 regression tests, none needing a GPU
                                             # 11 of them need a Postgres and skip loudly
                                             # without one; REVIEW_TEST_DB_URL points them
                                             # at a server, and DATABASE_SETUP.md has a
                                             # no-administrator local cluster recipe
```

Every step is idempotent; the safe recovery from any failure is to run it again.

## What the bulk path cannot reach

The DERA sets are indexed by **filing** quarter, and filings lag their period by ~56
days, so the newest as-of date in the 2026Q2 set is **2026-04-30**. The $589.0095
Anthropic repricing verified in Week 1 (period ends 5/29 and 5/31, filed late July) sits
in 2026Q3, which the SEC has not published. Bulk alone is structurally about two months
further behind than the quarter label suggests — which is what the Week 3 live-EDGAR
path is for.

## What this project does not claim

- **No company valuations.** N-PORT gives the fund's share count, never the company's total
  shares outstanding. Any valuation would only be as good as an imported third-party share
  count. This project publishes price per share and nothing more.
- **Nothing timely.** Filings lag fiscal quarter end by ~55–60 days; bulk data sets lag those
  by up to another ~90. Structurally unsuitable as a trading signal.
- **No novelty of the data source.** Caplight commercializes this, and the academic
  literature (Agarwal et al. 2023; Gornall & Strebulaev 2020; Chernenko et al.; Kwon et al.)
  has answered several of the interesting questions. The contribution is **open,
  reproducible infrastructure**, not discovery.
- **Not complete coverage.** Some exposure sits behind opaque SPVs that cannot be seen
  through. The project reports the count rather than pretending they aren't there.

## Layout

```
docs/feasibility.md       Week 1 verification, findings, and open risks
docs/entity_resolution.md normalisation, the matcher, the LLM measurement, the queue
docs/review_queue.md      generated — the questions waiting on a human
docs/marks_panel.md       generated — the price panel, and what is quarantined
docs/findings.md          generated — re-mark, dispersion, propagation, Cerebras
docs/worklog.md           dated log — what was done, decided, blocked
DATABASE_SETUP.md         connection string, schema, a local cluster, idempotency, disk
scripts/                  reconcile · check_fund_complexes · verify_week1_marks
                          build_golden_candidates · label_golden_set · score_matcher
                          run_adjudication · review_queue (the reviewer's view)
                          build_marks (the panel, the detector, the checks)
                          analyze (the four measurements, the findings report)
src/ingest/               download_bulk · universe (frozen patterns) · build_parquet
src/db/                   schema.sql · connect · load · seed (companies)
src/resolve/              normalize (names, share classes) · match (matcher v1)
                          adjudicate (matcher v2, four policies) · llm (Ollama + stub)
src/graphs/               resolve_graph — the review queue, checkpointed to Postgres
src/marks/                build (securities, marks) · splits (the detector)
                          verify (plan.md's end-to-end checks)
src/signal/               findings — re-mark, dispersion, propagation, Cerebras
tests/                    regression tests; fixtures/golden_set_v1.json is the ground truth
data/parquet/<qtr>/   private_holdings · universe_holdings · reconciliation.json
plan.md               the full project plan and 12-week schedule
```

## Governance

This agent lives inside the Mycroft repository and follows `SNICKERDOODLE.md`: verified data
before external lookup, provenance on every number, gates cleared by a named human, and
meaningful runs logged.

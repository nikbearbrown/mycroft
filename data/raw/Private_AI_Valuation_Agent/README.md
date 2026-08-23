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

pytest -q                                    # 89 regression tests
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
docs/entity_resolution.md Week 4 — normalisation, the matcher, measured metrics
docs/worklog.md           dated log — what was done, decided, blocked
DATABASE_SETUP.md         connection string, schema, idempotency, disk
scripts/                  reconcile · check_fund_complexes · verify_week1_marks
                          build_golden_candidates · label_golden_set · score_matcher
src/ingest/               download_bulk · universe (frozen patterns) · build_parquet
src/db/                   schema.sql · connect · load
src/resolve/              normalize (names, share classes) · match (matcher v1)
src/{marks,graphs,signal}/   Weeks 7-11
tests/                    regression tests; fixtures/golden_set_v1.json is the ground truth
data/parquet/<qtr>/   private_holdings · universe_holdings · reconciliation.json
plan.md               the full project plan and 12-week schedule
```

## Governance

This agent lives inside the Mycroft repository and follows `SNICKERDOODLE.md`: verified data
before external lookup, provenance on every number, gates cleared by a named human, and
meaningful runs logged.

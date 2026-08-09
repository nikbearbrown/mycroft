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

**Week 1 — feasibility verified.** See [`docs/feasibility.md`](docs/feasibility.md).

19 Anthropic PBC positions across 6 fund families were verified by hand from EDGAR. Four
independent managers priced Anthropic identically to the cent; after a new round, two more
landed on the same figure to four decimal places, two days apart.

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
return HTTP 403. Set `EDGAR_NAME` and `EDGAR_EMAIL`.

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
docs/feasibility.md   Week 1 verification, findings, and open risks
docs/worklog.md       dated log — what was done, decided, blocked
scripts/              standalone verification and utility scripts
src/{ingest,resolve,marks,graphs,signal}/
tests/fixtures/       hand-verified filing data; seed of the golden set
plan.md               the full project plan and 12-week schedule
```

## Governance

This agent lives inside the Mycroft repository and follows `SNICKERDOODLE.md`: verified data
before external lookup, provenance on every number, gates cleared by a named human, and
meaningful runs logged.

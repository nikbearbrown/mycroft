# Grading scorecard — 2026-08-31 01:30 UTC

**19** actionable signals graded-or-attempted. **3** gradeable now (enough time
has elapsed): **3/3 (100%)** correct. **16** still pending (insufficient time
elapsed, or a real data gap — see below).

> **n=3 is not a sample size to generalize an accuracy claim from.** See
> `PRE_REGISTRATION.md` — Week 4's own falsification criterion says exactly this.
> This scorecard reports what was found; it does not say the system "works."

## Outcome breakdown

| grading_note (blank = graded) | count |
|---|---|
| insufficient time elapsed | 15 |
| (graded) | 3 |
| no close on or before 2026-08-27 in the fetched window | 1 |


## By event_type

| event_type | correct | count |
|---|---|---|
| bankruptcy |  | 2 |
| delisting | t | 3 |
| delisting |  | 14 |


## Graded signals (detail)

| signal_id | ticker | predicted | realized | pct_move | correct | priced_at | priced_after |
|---|---|---|---|---|---|---|---|
| sig_0001193125-26-371260 | RNTX | down | down | -2.68 | t | 2026-08-27 | 2026-08-28 |
| sig_0001477932-26-005300 | SOBR | down | down | -5.51 | t | 2026-08-27 | 2026-08-28 |
| sig_0001213900-26-094172 | ONFO | down | down | -4.93 | t | 2026-08-27 | 2026-08-28 |


## Not yet graded (detail)

| signal_id | ticker | event_type | reason |
|---|---|---|---|
| sig_0001437749-26-029183 | AZIO | delisting | insufficient time elapsed |
| sig_0001213900-26-094397 | BBCQU | delisting | insufficient time elapsed |
| sig_0001539497-26-002373 | BCAB | delisting | insufficient time elapsed |
| sig_0001104659-26-102570 | BTAI | bankruptcy | insufficient time elapsed |
| sig_0001437749-26-029184 | GOVX | delisting | insufficient time elapsed |
| sig_0001193805-26-001155 | GURE | delisting | insufficient time elapsed |
| sig_0001493152-26-040577 | JUNS | delisting | insufficient time elapsed |
| sig_0001829126-26-009454 | KALA | delisting | insufficient time elapsed |
| sig_0001493152-26-040591 | MYSZ | delisting | insufficient time elapsed |
| sig_0001493152-26-040478 | NCPL | delisting | insufficient time elapsed |
| sig_0001493152-26-040645 | OGEN | delisting | insufficient time elapsed |
| sig_0000944075-26-000073 | SCKT | delisting | insufficient time elapsed |
| sig_0001193125-26-374328 | SGMOQ | bankruptcy | insufficient time elapsed |
| sig_0001493152-26-040622 | SHPH | delisting | insufficient time elapsed |
| sig_0001493152-26-040647 | YYAI | delisting | insufficient time elapsed |
| sig_0001493152-26-040421 | LTRYW | delisting | no close on or before 2026-08-27 in the fetched window |


## Caveats

- Holding period is 1 trading day (`PRE_REGISTRATION.md`, fixed before this ran).
- A `flat` realization (move within ±0.5%) counts as incorrect against a directional call —
  that is a design choice, not a bug: "down" that didn't move is not a validated call.
- Two Aug-27 signals (BBCQU, LTRYW) could not be priced at all — both are exotic security
  types (a SPAC-unit ticker and a warrant ticker); Yahoo Finance's symbol convention for
  those often differs from the one in SEC's own ticker file. Not a grading-logic bug;
  a ticker-resolution gap, left open rather than papered over.
- Every row here traces to a `gate_decisions` row with a named reviewer — see
  `logs/RUN_LOG.md`.

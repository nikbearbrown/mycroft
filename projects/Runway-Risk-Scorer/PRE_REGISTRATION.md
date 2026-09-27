# Pre-registration note — runway-risk-scorer (Row 5)

**Committed BEFORE running the Row 5 checks.** Purpose: fix what "correct" means
in advance, so results cannot be reshaped after the fact to look good (P8).

Date committed: 2026-08-24

## Predictions for the sample set (written BEFORE the run)

| company      | prediction                                    | reasoning                        |
|--------------|-----------------------------------------------|----------------------------------|
| harbor-ai    | total $45M, 1 distress (layoff)               | Series B + a layoff signal       |
| lumen-labs   | total $12M, 0 distress, very stale (>4y old)  | only 2022 signals                |
| vela-systems | total $120M, 0 distress, fresh                | Series C in 2026                 |
| orphan-co    | all UNKNOWN                                    | only signal is unvalidated       |

## Break-test predictions (what SHOULD happen on bad input)

- broken money string ("$4X million")  -> total_raised = UNKNOWN, no crash
- future date (2099)                    -> runs, no crash
- empty company                         -> all UNKNOWN, no crash
- missing source_url                    -> signal dropped as malformed
- unvalidated signal                    -> dropped (P2)
- malformed date ("not-a-date")         -> no crash

## What would FALSIFY a metric (prove it wrong)

- a company with only old signals showing as "fresh"
- any bad input causing a crash instead of UNKNOWN
- the tool ever emitting a verdict ("at risk") instead of a number

## After the run

Record actual vs predicted in RUN_LOG.md. Any mismatch is investigated and
explained, never silently corrected.

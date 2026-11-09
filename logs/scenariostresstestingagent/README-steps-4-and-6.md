# Scenario Stress Testing Agent: how to run steps 4 and 6 (sample mode)

These are the checks and results for steps 4 (transform and quality check) and 6 (produce human report) of
`recipes/scenariostresstestingagent.md`, built 2026-11-01 on top of steps 1, 3 and 5 (see `README.md` in this folder). Everything runs on the
same invented corpus; **nothing calls Groq, Alpha Vantage or any other service**, and nothing is written outside this recipe's own paths.
Python 3.9+ standard library only. Run from the repository root.

| Step | Command | Expected |
|---|---|---|
| 4 quality check | `python3 scripts/gigo/scenariostresstestingagent-transform-quality-check.py` | exit 0: 11 stress results reconcile on every check, 1 stopped at the Groq handoff, 0 duplicates, 11 advisory flags |
| 4 on the defective set | `python3 scripts/gigo/scenariostresstestingagent-transform-quality-check.py --verified-dir data/verified/scenariostresstestingagent/defective` | exit 1 **by design**: 10 rejects carried from step 3, nothing to check |
| 6 human report | `python3 scripts/tools/scenariostresstestingagent-produce-human-report.py --now 2026-11-01T09:00:00Z` | exit 0: writes `reports/generated/scenariostresstestingagent-2026-11-01.md` and `logs/scenariostresstestingagent-2026-11-01.json` |
| 6 on the defective set | `python3 scripts/tools/scenariostresstestingagent-produce-human-report.py --folder defective --now 2026-11-01T09:00:00Z` | exit 0: the same pair with `-defective` added; the report says nothing ran |
| evidence | `python3 scripts/tools/scenariostresstestingagent-report-self-test.py` | exit 0: 30 of 30 checks as expected, including 12 deliberate breaks and 3 refusals |

Step 6 needs step 4's output first (it refuses, exit 2, if `quality-check.json` is missing or does not account for exactly the requests step 3
accepted and step 5 ran, or if the run envelope declares live calls). `--now <ISO time>` pins the date and `generated_at`; with it pinned, two
runs give identical bytes. `--no-write` on step 6 prints the result without writing the report or the log.

## What step 4 checks

For every stress result it re-derives, from the workflow's own template shocks, each position's shock, loss and final value, the total loss,
final value, drawdown and risk level, and checks the weights (within 0.01 of 1.0 after the workflow's rescale), the order of the positions, the
top three losers and the scenario name. It looks for duplicates by id and by content (the same holdings under the same scenario). It raises
advisory flags for a human, which are not failures: weights rescaled, a majority holding, at least half the book in tickers the workflow's sector
map does not list, a drawdown within 0.05 points of a risk line, a defaulted scenario, a handoff. It does not call the step-5 engine and does not
judge whether the template shocks or risk lines are sound.

## What step 6 writes

The report follows the recipe's Output Contract: the reader, the decision it enables, and fifteen sections in order (run summary through decision
recommendation). The six phase gates are judged from evidence, findings the data supports are kept apart from readings of the invented sample
(labelled inferred), and the recommendation can only approve a sample-mode next phase: live execution stays blocked while no approval record exists.

## Stop conditions

The recipe's four stop conditions are judged from evidence, not assumed: a scan of this recipe's scripts, raw data and recipe for a quoted literal
assigned to an api key, secret, token, password or authorization (or an `sk-` key or a Bearer token); the run envelope and the approval record; the
sample folder and its manifest; and the report's provenance sections. Each gets a `triggered` value and its own `evidence` string in the agent log,
and the report's run summary says how many triggered, so the log and the report say the same thing. If one triggers, the recommendation to approve
becomes NO.

## What is in this folder

- `report-self-test-results.json` and `.md`: every check, what was expected, what was seen.
- Beside it, in `data/verified/scenariostresstestingagent/{clean,defective}/`: `quality-check.json` and `quality-notes.md`.
- In `reports/generated/` and `logs/`: the report and agent log for each folder, dated 2026-11-01.

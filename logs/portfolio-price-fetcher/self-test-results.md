# Self-test: Portfolio Visualization Agent (closed steps)

15 of 15 checks behaved as expected.

| Section | Ran | Saw | Expected | As expected |
|---|---|---|---|---|
| A step 1 | price fetcher provenance, as declared | exit 0 | exit 0, result pass | yes |
| A step 1 | dashboard provenance, as declared | exit 0 | exit 0; placeholder workflow id recorded as a note | yes |
| A step 1 break | workflow file missing | exit 1 | exit 1 (stop) | yes |
| A step 1 break | a workflow node renamed (node table drift) | exit 1; - in the workflow but not the recipe's node table: Fetch Prices (renamed) (httpRequest) | exit 1, the renamed node named in the findings | yes |
| A step 1 break | the two portfolio definitions disagree (NVDA shares 50 vs 55) | exit 1 | exit 1, portfolio_consistent false | yes |
| A step 1 break | a fixture edited after the manifest froze it | exit 1 | exit 1, the fixture named | yes |
| A step 1 break | dashboard calls a different workflow by name | exit 1 | exit 1, calls_price_fetcher false | yes |
| B step 3 | clean set | exit 0; 5 promoted, 0 rejected | exit 0; 5 promoted, 0 rejected | yes |
| B step 3 | price fallback (JavaScript ||) | previousClose used for ['GOOGL', 'META'] | GOOGL (null) and META (0) fall back | yes |
| B step 3 | defective set: every catalogued defect | exit 1; caught 5/5 | exit 1; every defect in the manifest rejected, none promoted | yes |
| C step 5 | refuses a set step 3 rejected | exit 1 | exit 1, nothing written | yes |
| C step 5 | clean set | exit 0; total 65098.13 | exit 0; 65098.125 rounds to 65098.13 as toFixed does (Python's default gives .12) | yes |
| D parity | port vs the original JavaScript, clean set | parity pass: 5/5 holdings and the summary agree with the original JavaScript (excluded: lastUpdatedFormatted) | exit 0; every holding and the summary agree | yes |
| D parity break | a port that rounds like Python, not JavaScript | broken port ran: True; - summary.totalGainLoss: original '11298.13', port '11298.12' | the broken port runs, then parity exits 1 naming the totalCurrentValue difference | yes |
| E rerun | steps 3 and 5 run again | byte-identical | byte-identical outputs | yes |

## Did not test

- Any live call: Yahoo Finance is never fetched; the live handoff is recorded, not executed.
- Steps 2, 4 and 6 of the price fetcher and steps 2–6 of the dashboard: still `[TODO: DEV]`.
- `lastUpdatedFormatted` against the original: toLocaleString depends on the host's locale.
- Real market data: every price in the sample corpus is invented.

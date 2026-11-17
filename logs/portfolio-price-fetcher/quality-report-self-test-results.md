# Self-test results: portfolio-price-fetcher, steps 4 and 6

24 of 24 checks behaved as expected. Each row says what was run, what was seen and what was expected; the break tests are the rows in sections D and H.

| Section | Ran | Saw | Expected | As expected |
|---|---|---|---|---|
| A step 4 clean | step 4 on the clean set | exit 0; 5 verified; flags ['GOOGL:PRICE_FELL_BACK', 'META:PRICE_FELL_BACK']; rejects 0 | exit 0; 5 verified; exactly the two fallbacks (GOOGL null price, META zero price); no rejects | yes |
| A step 4 clean | the order of verified_records | NVDA, MSFT, GOOGL, META, AMD | the workflow's own order: NVDA, MSFT, GOOGL, META, AMD | yes |
| A step 4 clean | NVDA's derived numbers | day 1.32%, price/buy 1.121 | day +1.32% (504.5625 / 498), price/buy 1.121 (504.5625 / 450) | yes |
| B defects | step 4 on quality-duplicate (two NVDA responses that disagree, each valid alone; step 3 passed both) | exit 1; rejects ['NVDA-restated.json', 'NVDA.json']; flags ['GOOGL:PRICE_FELL_BACK', 'META:PRICE_FELL_BACK', 'NVDA:HOLDING_MISSING'] | exit 1; BOTH NVDA files rejected (nothing says which is right); NVDA reported HOLDING_MISSING; output still written | yes |
| B defects | step 4 on quality-missing (no AMD response) | exit 0; [('AMD', 'high')]; coverage missing ['AMD'] | exit 0; AMD HOLDING_MISSING, severity high, cost basis 7,200.00 named; coverage.missing = [AMD] | yes |
| B defects | step 4 on quality-move (AMD 40% under its previous close) | exit 0; flags ['AMD:DAY_MOVE_LARGE', 'GOOGL:PRICE_FELL_BACK', 'META:PRICE_FELL_BACK'] | exit 0; AMD DAY_MOVE_LARGE added to the two fallbacks | yes |
| B defects | step 4 on quality-far (META 3.44x its buy price) | exit 0; flags ['GOOGL:PRICE_FELL_BACK', 'META:FAR_FROM_BUY_PRICE'] | exit 0; META FAR_FROM_BUY_PRICE; META's own fallback flag gone (its price is live) | yes |
| C identical duplicate | a byte-identical second NVDA response | exit 0; duplicates [('NVDA', True)]; verified 5; rejects 0 | exit 0; one identical duplicate collapsed to the first file; 5 verified; no rejects | yes |
| D break step 4 | step 4 on the defective set (step 3 rejected five responses) | exit 1; quality-checked.json written: False | exit 1; nothing written (quality checks read promoted data only) | yes |
| D break step 4 | step 4 where step 3 never ran | exit 2 | exit 2 and a message naming step 3 | yes |
| D break step 4 | step 4 run twice on the clean set | output hash same | byte-identical | yes |
| E what step 4 adds | steps 3 and 5 on quality-duplicate (both NVDA responses valid), then step 4's verdict on the same set | step 5 priced NVDA at 504.5625, one of the two prices, with no complaint; step 4 rejected 2 records | step 5 uses one of the two prices (504.5625 or 530) without noticing (step 3 judges each file alone); step 4 is where the pair is seen | yes |
| F step 6 clean | step 6 on the clean set | exit 0; 15 sections | exit 0; the fifteen contract sections, in order | yes |
| F step 6 clean | the agent log's fields | 16 fields; stop conditions triggered 0; steps [1, 3, 4, 5, 6] | the contract's sixteen fields in order; none of the four stop conditions triggered; steps 1, 3, 4, 5, 6 | yes |
| F step 6 clean | the recommendation | approves sample mode only | approves the next phase in sample mode only and blocks live execution | yes |
| F step 6 clean | step 6 run twice with --now pinned | same | byte-identical report and log | yes |
| G step 6 flagged | step 6 on quality-duplicate | exit 0; recommends fixes: True; mentions the conflict: True | exit 0; the report recommends fixes and blocks live execution; the NVDA conflict is quoted | yes |
| H break step 6 | an envelope that declares live calls approved | exit 2; step 6 stop: the run envelope declares live calls or a mode other than sample (a stop condition in the recipe); wrote nothing: True | exit 2, nothing written, message names live calls | yes |
| H break step 6 | step 4's output removed | exit 2; step 6 stop: <tmp>/no4/clean/quality-checked.json not; wrote nothing: True | exit 2, nothing written, message names run step 4 first | yes |
| H break step 6 | step 4's verified NVDA price tampered to 1.0 | exit 2; step 6 stop: step 4's verified price for NVDA does not match step 3's promoted record; wrote nothing: True | exit 2, nothing written, message names does not match step 3 | yes |
| H break step 6 | step 5's total value tampered to 70000.00 | exit 2; step 6 stop: step 5's totals 70000.00/53800.00 do not match the sum of its own stocks ('65098.13', '53800.00'); wrote nothing: True | exit 2, nothing written, message names do not match the sum | yes |
| H break step 6 | a hardcoded key planted in a copy of one of this recipe's scripts | exit 0; credential stop condition triggered: True | the report is still written, and the agent log records stop condition 1 as triggered, naming the file | yes |
| H break step 6 | an approval record present (the script reports sample runs only) | exit 2; step 6 stop: an approval record exists at logs/gate-decisions/portfolio-price-fetcher-appr | exit 2 and a message naming the approval record | yes |
| I existing steps | step 3 rerun into a temp folder against the committed clean output | byte-identical | byte-identical (this contribution changes no existing file) | yes |

## Did not test

- Any live call (there is no approval record, and the Yahoo Finance request is never made).
- Any real market data: every price in the sample corpus is invented.
- Whether the three numeric lines in step 4 (15% day move, 3x and one third of the buy price) are the right lines for a real portfolio; they are labelled our judgment.
- Step 2 (ingest), which has no script yet, and the recipe's status and TODO markers, which this contribution did not edit.

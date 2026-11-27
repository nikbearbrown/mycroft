# Step 2 self-test results: portfolio-price-fetcher

28 of 28 checks behaved as expected. Each row: what was run, what was seen, what was expected.

| Section | Ran | Saw | Expected | As expected |
|---|---|---|---|---|
| clean set | step 2 on the clean set (the envelope's fixture_set) | exit 0; 5 ingested, 0 rejected; sample_mode True | exit 0; 5 ingested; 0 rejected; sample_mode true | yes |
| clean set | compare each ingested body and SHA-256 with the file on disk and the frozen manifest | bodies identical: True; hashes agree: True | both true: the body is kept unchanged | yes |
| clean set | read fetched_at | 2026-10-10T00:00:00Z (the envelope's as_of is 2026-10-10T00:00:00Z) | equal, so reruns are byte-identical | yes |
| all sets | step 2 with --set all | exit 1; (ingested, rejected) by set: {'clean': (5, 0), 'defective': (4, 1), 'quality-duplicate': (6, 0), 'quality-far': (5, 0), 'quality-missing': (4, 0), 'quality-move': (5, 0)} | exit 1 (the defective set has one file that is not JSON); counts {'clean': (5, 0), 'defective': (4, 1), 'quality-duplicate': (6, 0), 'quality-far': (5, 0), 'quality-missing': (4, 0), 'quality-move': (5, 0)} | yes |
| all sets | the one reject in the defective set | [{'file': 'defective/truncated-json.txt', 'reason': 'not valid JSON (Invalid control character at)'}] | truncated-json.txt, not valid JSON | yes |
| against step 3 | the files step 3 reads in each set versus the files step 2 ingests or rejects | identical in all 6 sets: True | the same file population in every set (step 2 neither adds nor loses a file) | yes |
| against step 3 | the defective set: records step 2 ingests versus records step 3 promotes | step 2 ingests 4; step 3 promotes 0 of the same files | step 2 ingests the four that are valid JSON and step 3 promotes none (ingest does not judge a response) | yes |
| against step 3 | the quality-duplicate set: two valid NVDA responses | ingested 2 (NVDA-restated.json, NVDA.json); rejects 0 | both ingested, no reject: choosing between them is step 4's work | yes |
| naming ledger | the quality-missing set | holdings with no named file: ['AMD']; files named for no holding: [] | AMD has no file; no stray file | yes |
| naming ledger | the quality-duplicate set, files named for NVDA | ['NVDA-restated.json', 'NVDA.json'] | NVDA.json and NVDA-restated.json (both claim NVDA by name) | yes |
| source check | every source-bearing node the workflow names | {'Manual Trigger': 'available', 'Define Portfolio': 'available', 'Fetch Stock Prices': 'approval-required'} | Manual Trigger and Define Portfolio available; Fetch Stock Prices approval-required | yes |
| source check | the live request row | live_call_performed False; approved_for_live_action False; approval record present False | false; false; false (no approval record exists) | yes |
| source check | the holdings Define Portfolio declares | read from the workflow itself: 5 holdings (AMD, GOOGL, META, MSFT, NVDA) | five holdings: AMD, GOOGL, META, MSFT, NVDA | yes |
| break: changed a byte | change one digit of clean/NVDA.json, then ingest | exit 1; ingested 4; reject: differs from the SHA-256 frozen in manifest.json (frozen 2633560d6573, | exit 1; 4 ingested; the changed file rejected for differing from its frozen SHA-256 | yes |
| break: removed a file | delete clean/AMD.json, then ingest | exit 1; reject: listed in manifest.json but missing | exit 1; AMD.json reported as listed in the manifest but missing | yes |
| break: added a file | add clean/TSLA.json (not in any manifest), then ingest | exit 1; ingested 5; reject: not listed in a frozen manifest, so its origin is not vouche | exit 1; the five frozen files ingested; the stray file rejected as not listed | yes |
| break: broken JSON with a matching hash | replace clean/MSFT.json with truncated JSON and re-freeze its hash, then ingest | exit 1; reject: not valid JSON (Expecting value) | exit 1; rejected as not valid JSON (the hash check alone would not catch it) | yes |
| break: envelope mode live | set the run envelope to mode live, then ingest | exit 1; ["STOP: the run envelope declares mode 'live'; this step implements sample mode only"] | exit 1 with a STOP naming the envelope; no live action | yes |
| break: envelope live calls approved | set the run envelope to live calls approved, then ingest | exit 1; ['STOP: the run envelope declares live_calls_approved: True; sample mode needs false'] | exit 1 with a STOP naming the envelope; no live action | yes |
| break: no envelope | delete the run envelope, then ingest | exit 1; ['STOP: the run envelope is missing (data/raw/portfolio-price-fetcher/run-envelope.json); no scope was declared'] | exit 1: no scope was declared | yes |
| break: workflow without the fetch node | remove Fetch Stock Prices from the workflow copy, then ingest | exit 1; ["STOP: the workflow has no 'Fetch Stock Prices' node"] | exit 1: the source this step must account for is gone | yes |
| break: a manifest is missing | delete quality-manifest.json, then ingest --set all | exit 1; ['STOP: the manifest data/raw/portfolio-price-fetcher/sample/quality-manifest.json is missing'] | exit 1: nothing is trusted without its frozen hashes | yes |
| break: a set that does not exist | ingest --set no-such-set | exit 2 | exit 2 | yes |
| approval record | add a stand-in approval record, then ingest | approval_record_present True; approved_for_live_action False; live_call_performed False | true; false; false (this step never makes the call, with or without a record) | yes |
| rerun | ingest --set all twice into separate copies and compare every output file | 13 files; byte-identical: True | byte-identical | yes |
| rerun | the same with --now pinned to another time | 13 of 13 files differ (the ones that carry the time) | only files carrying fetched_at or checked_at change | yes |
| reach | search the script for network, process and environment access | found: none | none: it cannot reach the network or read a credential | yes |
| committed outputs | regenerate data/raw/portfolio-price-fetcher/ingest/ and compare with what is committed | 13 files; identical: True | identical | yes |

## Did not test

- Any live call: this step makes none, and no approval record exists in the repository.
- Real market data: every price in the fixtures is invented and says so.
- Whether the frozen manifests list the right files: that is a human judgment about the fixtures, not something this step can check.
- Reading a very large response or a slow disk: the fixtures are tiny.

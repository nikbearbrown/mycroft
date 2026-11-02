# Self-test, steps 4 and 6: scenariostresstestingagent

30 of 30 checks came out as expected. A check passes only if what was observed is what was expected; the deliberate breaks are meant to be caught. Every break ran on a temporary copy of the tree.

| Check | Expected | Observed | Result |
|---|---|---|---|
| 4 clean set: exit 0, 11 reconciled, 1 handed off, no failures, no duplicates | exit 0; 11; 1; 0; 0 | exit 0; 11; 1; 0; 0 | as expected |
| 4 clean set: the corpus's designed edge cases raise their flags | default-sector, handoff, majority-holding, on-threshold, rescaled, scenario-defaulted | default-sector, handoff, majority-holding, on-threshold, rescaled, scenario-defaulted | as expected |
| 4 idempotent: a second run gives the same bytes | identical | identical | as expected |
| 4 defective set: exit 1, 0 verified, 10 rejects | exit 1; 0; 10 | exit 1; 0; 10 | as expected |
| 4 break caught: a position's loss is off by 1 | exit 1; failure `position-loss` recorded | exit 1; ['position-final', 'position-loss', 'top-losers', 'total-loss'] | as expected |
| 4 break caught: a position's shock_pct is off by 1 | exit 1; failure `position-shock` recorded | exit 1; ['position-loss', 'position-shock', 'top-losers'] | as expected |
| 4 break caught: total_loss is off by 5 | exit 1; failure `total-loss` recorded | exit 1; ['drawdown', 'final-value', 'total-loss'] | as expected |
| 4 break caught: final_portfolio_value is off by 10 | exit 1; failure `final-value` recorded | exit 1; ['final-value'] | as expected |
| 4 break caught: risk_level says LOW for a 78% drawdown | exit 1; failure `risk-level` recorded | exit 1; ['risk-level'] | as expected |
| 4 break caught: top_losers in the wrong order | exit 1; failure `top-losers` recorded | exit 1; ['top-losers'] | as expected |
| 4 break caught: a weight changed so the book adds to 0.9 | exit 1; failure `weights-sum` recorded | exit 1; ['position-initial', 'top-losers', 'weights-sum'] | as expected |
| 4 break caught: scenario_name is not the template's | exit 1; failure `scenario-name` recorded | exit 1; ['scenario-name'] | as expected |
| 4 break caught: the same id twice | exit 1; a duplicate of kind `id` | exit 1; ['id', 'content'] | as expected |
| 4 break caught: the same holdings and scenario under another id | exit 1; a duplicate of kind `content` | exit 1; ['content'] | as expected |
| 4 break caught: an accepted request with no step-5 result | exit 1; failure `ran` | exit 1; ['ran'] | as expected |
| 4 refuses an unreadable validated.json: exit 2, nothing written | exit 2; quality-check.json not written | exit 2; written: False | as expected |
| 6 clean report: exit 0 and the Output Contract's fifteen sections, in order | exit 0; Run summary, Purpose, Source inventory, Inputs used, Phase-gate results, Steps completed, Records seen, Rejects, Duplicates, Flags, Typed TODOs, Human approvals, Verified findings, Inferred findings, Decision recommendation | exit 0; ['Run summary', 'Purpose', 'Source inventory', 'Inputs used', 'Phase-gate results', 'Steps completed', 'Records seen', 'Rejects', 'Duplicates', 'Flags', 'Typed TODOs', 'Human approvals', 'Verified findings', 'Inferred findings', 'Decision recommendation'] | as expected |
| 6 agent log: the contract's sixteen fields | workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path | workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path | as expected |
| 6 the report's counts equal the files' counts | 12 requests in; 11 reconciled; 11 flags | 12 request(s) read; 11 reconciled; 11 advisory flag | as expected |
| 6 the recommendation always blocks live execution while no approval record exists | contains 'Block live execution: YES' | yes | as expected |
| 6 gates: 4 reads 5 of 6 scripts with step 2 open; 6 passes | 5 of 6; step(s) 2; gate 6 PASS | (True, True) | as expected |
| 6 stop conditions: four judged from evidence, none triggered, each with its own evidence | 4 conditions; none triggered; four different evidence strings, none the old placeholder | 4 conditions; triggered: [False, False, False, False]; distinct evidence: 4 | as expected |
| 6 the credential scan does not flag the report script itself | condition 1 says none found and names no script | et, token, password or authorization, an `sk-` key or a Bearer token: none found | as expected |
| 6 the person's page and the machine's page agree on stop conditions | report: 'Stop conditions: 0 of 4 triggered'; log: 0 triggered | report line present: True; log triggered: 0 | as expected |
| 6 idempotent: a second run (clock pinned) gives the same bytes | identical | identical | as expected |
| 6 defective set: exit 0, nothing ran, nothing to approve | exit 0; 'Approve for the next phase (sample mode only): NO' | exit 0; NO | as expected |
| 6 break caught: a hardcoded key planted in a script trips stop condition 1, both pages say so, and approve turns NO | log: condition 1 triggered, others not; report: 'Stop conditions: 1 of 4 triggered'; 'sample mode only): NO' | exit 0; triggered: [True, False, False, False]; report line: True; approve NO: True | as expected |
| 6 refuses when step 4's output is missing | exit 2; no report written | exit 2; report written: False | as expected |
| 6 refuses when step 4's output does not account for the accepted requests | exit 2; no report written | exit 2; report written: False | as expected |
| 6 refuses when the run envelope declares live calls | exit 2; no report written | exit 2; report written: False | as expected |

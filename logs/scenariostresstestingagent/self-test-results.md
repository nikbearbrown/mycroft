# Self-test: scenariostresstestingagent

Written by `scripts/tools/scenariostresstestingagent-self-test.py`. A check passes when what was seen is what was expected; each deliberate break must be caught.

- Checks: 27/27 as expected (0 skipped); deliberate breaks caught: 12/12
- node found: True

| Group | Check | Expected | Observed | As expected |
|---|---|---|---|---|
| provenance | recipe node table = workflow nodes; connections = the wiring the port assumes; ported nodes have the language  | OK | OK | yes |
| validator | clean set: all 12 accepted | 12 | 12 | yes |
| validator | defective set: all 10 rejected, each with a reason | 10 | 10 | yes |
| validator | each defect is rejected for its own reason | True | True | yes |
| port | 12 clean requests: 11 stress-tested, 1 stopped at the Groq handoff | (11, 1) | (11, 1) | yes |
| coverage | all five template scenarios reached | 5 | 5 | yes |
| coverage | all four risk levels reached | ['CRITICAL', 'HIGH', 'LOW', 'MODERATE'] | ['CRITICAL', 'HIGH', 'LOW', 'MODERATE'] | yes |
| coverage | both sides of the rescale rule: some requests rescaled, some left alone | (True, True) | (True, True) | yes |
| coverage | tickers both inside and outside the workflow's sector map | (True, True) | (True, True) | yes |
| coverage | the 10-percent threshold is hit exactly (and is LOW: the rule is 'above 10') | ('LOW', -10.0) | ('LOW', -10.0) | yes |
| port | a handoff is recorded for each live service, none approved or performed | True | True | yes |
| port | rejected data is refused: the tools exit 1 and write nothing | (1, False) | (1, False) | yes |
| untouched | the 8 generated per-node scripts are byte-identical to upstream/main | [] | [] | yes |
| parity | port = original code on every request and every node (compared cases mismatching) | 0 | 0 | yes |
| parity | cases compared (21 requests + 3 direct engine inputs; 1 not modelled and refused by the gate) | (24, 1) | (24, 1) | yes |
| deliberate break | a port that skips the weight rescale: parity must catch it | True | True | yes |
| deliberate break | a port with a wrong CRITICAL threshold (25, not 30): parity must catch it | True | True | yes |
| deliberate break | a port that treats exactly 10.0 as MODERATE ('>=' for '>'): parity must catch it | True | True | yes |
| deliberate break | a port that rounds positions to 1 decimal, not 2: parity must catch it | True | True | yes |
| deliberate break | a port that also applies the all_sectors shock the engine never reads: parity must catch it | True | True | yes |
| deliberate break | a port whose default scenario is rate_hike, not tech_crash: parity must catch it | True | True | yes |
| deliberate break | a port with NVDA in the wrong sector: parity must catch it | True | True | yes |
| deliberate break | a port that sends a custom scenario down the template branch: parity must catch it | True | True | yes |
| deliberate break | a renamed node: provenance must fail | False | False | yes |
| deliberate break | a rewired connection (the engine skipped): provenance must fail | False | False | yes |
| deliberate break | a tampered fixture: provenance must fail and the validator must stop (exit 2) | (False, 2) | (False, 2) | yes |
| deliberate break | a holding without a ticker: the gate must reject it with the node's own message | True | True | yes |

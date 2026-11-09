# Self-test: what-if-simulation-agent

18/18 checks came out as expected; 10 of them are deliberate attempts to break it.
Written by `scripts/tools/what-if-simulation-agent-self-test.py`. Each row pairs what was run with what was seen and what was expected.

| Ran | Saw | Expected | As expected |
|---|---|---|---|
| provenance as declared: verify-provenance on the declared workflow | exit 0; node table True, chain True, fixtures True | exit 0; all True | yes |
| BREAK: a node renamed in the workflow: rename 'Sim 1' in a copy of the workflow, run verify-provenance | exit 1; node table False; findings 2 | exit 1; node table False | yes |
| BREAK: Sim 3 skipped in the connections: rewire Sim 2 straight to Aggregate in a copy, run verify-provenance | exit 1; chain False | exit 1; chain False | yes |
| BREAK: a fixture changed after it was frozen: change one digit in c01, run verify-provenance | exit 1; fixtures False | exit 1; fixtures False | yes |
| BREAK: the validator on the changed fixture: same copy, run validate-data-shape | exit 2; validated.json written: False | exit 2; nothing written | yes |
| clean set validates: validate-data-shape on sample/clean | exit 0; 15 accepted, 0 rejected, record_count 15 | exit 0; 15 accepted, 0 rejected | yes |
| every catalogued defect rejected, for its own reason: validate-data-shape on sample/defective | exit 1; 10/10 rejected; wrong or missing reasons: none | exit 1 (by design); 10/10 rejected, each for its catalogued reason | yes |
| the contract has not drifted from the workflow's own rules: compare the validator's five messages with the errors.push() messages in the Parse & Validate Input node | workflow 5 messages, validator 5; equal: True | the same five messages in the same order | yes |
| approved tools run on the clean set: run-approved-tools on the validated clean set | exit 0; 15 results, each with an aggregate and a prompt: True | exit 0; 15 results | yes |
| the clean set reaches every branch: read the results: matrix cells, risk appetites, horizons, final recommendations | 9/9 matrix cells; 3/3 risk appetites; 3/3 horizons; 5/5 final recommendations | 9/9; 3/3; 3/3; 5/5 | yes |
| rerun is byte-identical: run-approved-tools twice | identical: True | identical | yes |
| BREAK: the tools are handed rejected requests: run-approved-tools on the defective validated.json | exit 1; anything written: False | exit 1; nothing written | yes |
| BREAK: a clean file hand-edited to hold a rejected request: add one rejected entry to the clean validated.json, run-approved-tools | exit 1 | exit 1 | yes |
| parity with the original JavaScript: parity-check: original JS vs the port, 23 requests (15 clean, 8 object-shaped defective) | parity: 23/23 requests identical to the original JavaScript, 0 different | 23/23 identical | yes |
| BREAK: rounding with Python's round() (half goes to even): parity-check on a copy of the port with that one change | parity: 22/23 requests identical to the original JavaScript, 1 different | exit 1; the parity check must catch it | yes |
| BREAK: toFixed with Python's format (ties go to even): parity-check on a copy of the port with that one change | parity: 19/23 requests identical to the original JavaScript, 4 different | exit 1; the parity check must catch it | yes |
| BREAK: Math.min/Math.max replaced by Python's min/max (NaN is not contagious): parity-check on a copy of the port with that one change | parity: 21/23 requests identical to the original JavaScript, 2 different | exit 1; the parity check must catch it | yes |
| BREAK: numbers printed the Python way (100.0 for 100): parity-check on a copy of the port with that one change | parity: 6/23 requests identical to the original JavaScript, 17 different | exit 1; the parity check must catch it | yes |

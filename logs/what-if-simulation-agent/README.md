# What-If Simulation Agent: how to run the closed steps

`recipes/what-if-simulation-agent.md` (steps 1, 3 and 5, and the two script mappings for the Parse & Validate Input and
Aggregate & Score nodes), in sample mode. Python 3.9+ standard library only; no network, no keys. The parity check also
needs `node`. Run every command from the repository root.

## Run it

```bash
python3 scripts/tools/what-if-simulation-agent-verify-provenance.py          # step 1
python3 scripts/gigo/what-if-simulation-agent-validate-data-shape.py         # step 3 (clean set)
python3 scripts/gigo/what-if-simulation-agent-validate-data-shape.py --sample-dir data/raw/what-if-simulation-agent/sample/defective   # exits 1 by design
python3 scripts/tools/what-if-simulation-agent-run-approved-tools.py         # step 5 (reads step 3's clean output)
python3 scripts/tools/what-if-simulation-agent-parity-check.py               # the port vs the original JavaScript
python3 scripts/tools/what-if-simulation-agent-self-test.py                  # every check, recorded
```

Add `--now 2026-10-17T00:00:00+00:00` to the provenance script, and `--now 2026-10-17` to the step-5 script, to reproduce
the committed records' file names.

## What each one does, and where it writes

| Script | Stops when | Writes |
|---|---|---|
| `what-if-simulation-agent-verify-provenance.py` | the declared workflow is missing or unparseable; its nodes differ from the recipe's node table; its connections do not form the chain the port assumes; a ported node has no code; a fixture no longer matches `sample/manifest.json` (exit 1, the record is still written) | `logs/what-if-simulation-agent-provenance-<date>.json` |
| `what-if-simulation-agent-validate-data-shape.py` | any request breaks the contract (exit 1; every finding is still reported); a fixture changed since the manifest froze it (exit 2, nothing written) | `data/verified/what-if-simulation-agent/<set>/validated.json` and `validate-audit.md` |
| `what-if-simulation-agent-run-approved-tools.py` | step 3 rejected anything, or the input is not the validator's output (exit 1, nothing written) | `data/verified/what-if-simulation-agent/<set>/simulation-results.json` and `logs/what-if-simulation-agent-run-approved-tools-<date>.json` |
| `what-if-simulation-agent-parity-check.py` | the port and the original JavaScript differ on any field of any result, or on one character of the prompt (exit 1) | `logs/what-if-simulation-agent/parity-results.json` |
| `what-if-simulation-agent-self-test.py` | any check does not behave as expected, or a deliberate break is not caught | `logs/what-if-simulation-agent/self-test-results.{json,md}` |

## The sample corpus

`data/raw/what-if-simulation-agent/sample/` holds simulation requests shaped as the workflow's webhook receives them.
**Every company, ticker and number is invented.**

- **`clean/` (15):** chosen to reach every branch of the six ported nodes and to sit exactly on the workflow's thresholds
  (growth 0.25 and 0.10, sentiment 0.65 and 0.40, P/E and debt/equity limits): all nine growth-and-sentiment cells,
  all three risk appetites, all three horizons, all five final recommendations (the self-test checks this), an empty body (every default), a webhook `body` wrapper, numbers sent as text,
  zeros kept as values (JavaScript's `??`), and the values where JavaScript and Python round differently (`Math.round(12.5)` is
  13; `(25.25).toFixed(1)` is "25.3"; `(0.625).toFixed(2)` is "0.63"; `(34.5).toFixed(0)` is "35").
- **`defective/` (10):** each of the workflow's five rules broken, two broken at once, two values that parse to NaN (which the
  workflow's own range checks let through; this gate does not), a list instead of an object, and a truncated file stored as `.txt`
  so the repository's conformance gate, which parses every `.json`, stays green.
- **`manifest.json`:** the SHA-256 of every file. Step 1 and step 3 refuse fixtures that changed after it was frozen.

`data/raw/what-if-simulation-agent/run-envelope.json` declares sample mode: no live calls, no network, no database writes.

## Not covered yet

- Steps 2, 4 and 6, and the script mappings for the respond-to-webhook and human-report nodes: still `[TODO: DEV]`. The recipe
  stays `DRAFT`, with `todos_open: 5`.
- Live mode. There is no approval record. The Groq call and the PostgreSQL write are only recorded handoffs
  (`approved_for_live_action: false`); the nodes after the prompt (Parse Groq Response, Prepare DB Record, Build Final Response)
  are not ported.
- Whether the simulators' investment logic is sound. It is ported faithfully, not judged.

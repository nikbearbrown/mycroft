# Portfolio Price Fetcher: step 2 (ingest declared inputs), sample mode

Adds the script the recipe names for step 2 (`scripts/ingest/portfolio-price-fetcher-ingest-inputs.py`), with its outputs and a
self-test. With steps 4 and 6 (added earlier), every step the recipe's main table names now has a script. Python 3.9+ standard
library only; no network, no keys. Run every command from the repository root. **Nothing that was already in the repository was
edited:** the recipe, the earlier scripts, `logs/RUN_LOG.md` and every earlier output are byte-identical; this change is new files only.

## Run it

```bash
python3 scripts/ingest/portfolio-price-fetcher-ingest-inputs.py --sample              # the envelope's set (clean); exit 0
python3 scripts/ingest/portfolio-price-fetcher-ingest-inputs.py --set all             # all six sets; exits 1 by design (one file is not JSON)
python3 scripts/tools/portfolio-price-fetcher-ingest-self-test.py                     # every check, recorded
```

## What step 2 does

It is the conductor's "Source and Credential Check" and the recipe's "ingest declared inputs". It reads the run envelope (sample mode,
live calls not approved), the workflow the recipe declares, the fixtures and the SHA-256 frozen in `manifest.json` (clean, defective)
and `quality-manifest.json` (the four quality sets), and writes under `data/raw/portfolio-price-fetcher/ingest/`:

| File | What it holds |
|---|---|
| `<set>/ingested.json` | the recipe's step-2 fields (`records`, `source_name`, `source_type`, `fetched_at`, `sample_mode`, `rejects`) plus `record_count`, each record's SHA-256 and the manifest that froze it, a naming ledger, and the step-1 record it follows |
| `<set>/ingest-audit.md` | the same, for a person to read |
| `source-check.json` | every node the workflow names that carries a source (Manual Trigger and Define Portfolio **available**; Fetch Stock Prices **approval-required**, never called), and step 1's result beside them |

A file is ingested only if it is listed in a frozen manifest, matches its SHA-256 and parses as JSON; otherwise it goes to `rejects` with
the reason, and the exit code is 1. `fetched_at` is the envelope's `as_of`, so reruns are byte-identical.

## What step 2 leaves to the steps after it

It ingests; it does not judge. A response with no price, an unknown ticker or an empty result is valid JSON and is ingested; two valid
responses for one ticker are both ingested. Step 3 judges each response and step 4 judges the set (see `README-steps-4-6.md`). The naming
ledger lists file names against the five declared holdings and says nothing about what is inside a file.

| Set | Ingested | Rejected | Note |
|---|---|---|---|
| clean | 5 | 0 | |
| defective | 4 | 1 | `truncated-json.txt` is not JSON; the other four are valid JSON that step 3 later rejects |
| quality-duplicate | 6 | 0 | two valid NVDA responses (`NVDA.json`, `NVDA-restated.json`) both ingested |
| quality-missing | 4 | 0 | the ledger shows AMD has no file |
| quality-move | 5 | 0 | |
| quality-far | 5 | 0 | |

## Checks

`scripts/tools/portfolio-price-fetcher-ingest-self-test.py`: 28 checks, all as expected, results in
`logs/portfolio-price-fetcher/ingest-self-test-results.{json,md}`. They include break tests (a changed byte, a removed file, a stray
file, truncated JSON whose hash was re-frozen, a live-mode envelope, an envelope that approves live calls, no envelope, a workflow without
the fetch node, a missing manifest, an unknown set), a stand-in approval record that must not become a live call, a comparison with step 3
(the same file population in every set), reruns that are byte-identical, a search showing the script cannot reach the network or read a
credential, and a regeneration check that the committed outputs are what the script writes.

## Seams left for the maintainers (please read)

- The recipe still shows step 2 with `[TODO: DEV]` and `todos_open: 3`, because the recipe was not edited. Closing step 2 (and steps 4
  and 6) and updating the status fields is a small edit to that one file; the text to add to step 2 would be: the script above is built
  and exercised in sample mode; input and output as listed here; where output goes `data/raw/portfolio-price-fetcher/ingest/`.
- `snickerdoodle check portfolio-price-fetcher` reports `built-not-documented` flags for this script's options (`--set`, `--raw-dir`,
  `--out-dir`, `--now`, `--no-write`, `--repo`), since the recipe's step-command table lists only `--sample`, which the script accepts. The
  rows to add are the options in the Run it block above.
- Steps 3 and 5 still read the fixtures or step 3's output directly, as before; step 2's self-test checks that it sees the same files.
- Not covered: any live call, real market data (every price is invented and says so), and whether the manifests list the right fixtures.

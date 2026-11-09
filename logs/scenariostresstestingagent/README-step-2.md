# Scenario Stress Testing Agent: how to run step 2 (sample mode)

These are the checks and results for step 2 (ingest declared inputs) of `recipes/scenariostresstestingagent.md`, built 2026-11-09 on top of steps 1, 3, 4, 5 and 6
(see `README.md` and `README-steps-4-and-6.md` in this folder). It is the conductor's "Source and Credential Check": it ingests the sample requests and reports every
source and credential the workflow names, without a live call. Everything runs on the same invented corpus; **nothing calls Groq, Alpha Vantage or any other service**,
no credential value is read, and nothing is written outside this recipe's own paths. Python 3.9+ standard library only. Run from the repository root.

| What | Command | Expected |
|---|---|---|
| Step 2 | `python3 scripts/ingest/scenariostresstestingagent-ingest-inputs.py --sample --now 2026-11-09T00:00:00+00:00` | exit 0: 12 clean and 10 defective requests read, 0 rejected; webhook available, chat skipped, Alpha Vantage and Groq approval-required; four files written under `data/raw/scenariostresstestingagent/ingest/` |
| Step 2, nothing written | the same with `--no-write` | exit 0, no file written |
| Step 2 self-test | `python3 scripts/tools/scenariostresstestingagent-ingest-self-test.py` | exit 0: every check as expected, results in `ingest-self-test-results.md` |
| The whole recipe | `node scripts/snickerdoodle.mjs run scenariostresstestingagent --sample` | `All 6 steps completed.` (transcript: `full-sample-run-2026-11-09.md`) |
| The runner's own contract check | `node scripts/snickerdoodle.mjs check scenariostresstestingagent` | no contract defects: every step has a script and its flags match |

## What step 2 does
- **Ingests:** reads each of the 22 frozen fixtures, trusts it only if its SHA-256 matches the manifest, and keeps its body exactly as it was (`records`, `source_name`, `source_type`, `fetched_at`, `sample_mode`, `rejects`, the recipe's step-2 fields). It does not judge a request's shape: a defective request is valid JSON and ingests like any other; step 3 judges shape.
- **Checks sources and credentials:** reads the workflow the recipe declares and lists each node that brings something in (the webhook, the chat trigger, the Alpha Vantage request, the Groq call) as available, skipped with a reason, or approval-required. The environment is asked only whether `ALPHA_VANTAGE_API_KEY` and `GROQ_API_KEY` are set (a yes or no), and the answer is the only thing kept.
- **Stops before transformation** (exit 1, files still written) if the run envelope is missing, is not sample mode or allows live calls, network or database writes; if the workflow or the manifest is missing; or if a fixture is missing, unlisted, changed since it was frozen, or not valid JSON.

## Deliberate breaks the self-test catches (each on a temporary copy)
A fixture changed by one letter; a fixture deleted; an unlisted fixture added; a fixture that is not JSON with the manifest updated to match; the manifest removed; the run envelope set to live, to allow network, to allow live calls, or removed; the workflow removed; the workflow without a webhook; a credentialed node of an unrecognised type (held back, never passed as available); an HTTP request to another host (approval-required, no credential name guessed); an approval record present (noticed, sample mode unchanged). It also checks that the script imports nothing that can reach a network, that the environment is only ever asked through `bool(os.environ.get(...))`, and that a dummy credential value set in the environment appears in no output file and not on the screen.

## What is not covered
- The live Alpha Vantage fetch and the Groq call: named as approval-required handoffs and never made; no approval record exists.
- Steps 3 to 6 still read the fixture folder directly, as built. The ingested records are those same bytes (the self-test checks all 22), so nothing differs, but they do not yet read step 2's output.
- The chat entry point is not exercised: the invented corpus has no chat-message fixture.
- The two preserved script-mapping lines in the recipe's "Existing Recipe Notes" are left as they were.
- No human has cleared any gate for this run, and `status` stays `DRAFT`.

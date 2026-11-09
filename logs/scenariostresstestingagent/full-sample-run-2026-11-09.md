# Full sample run, 2026-11-09: scenariostresstestingagent, all six steps through the CLI

**What this is.** The repo's own runner, `node scripts/snickerdoodle.mjs run scenariostresstestingagent --sample`, run for the first time with every step built. Until step 2 existed the runner stopped there ("this step is not built yet"). It was run on a **scratch copy of the working tree** (3,157 files, `.git` left out), so no existing output in the repo was rewritten; the step outputs worth keeping from this work are the ones committed beside this file (step 2's `ingest/` folder, step 6's report and agent log for 2026-11-09).

**Command and result:** exit 0; the runner printed `All 6 steps completed.`

```
ScenarioStressTestingAgent  ·  6 steps  ·  mode dialogic
  --sample not declared for this step in the recipe — not passed
→ verify-provenance  scripts/tools/scenariostresstestingagent-verify-provenance.py
OK: node table match True, chain match True, ported nodes True, fixtures True; 0 finding(s) -> logs/scenariostresstestingagent-provenance-2026-11-09.json
→ ingest-inputs  scripts/ingest/scenariostresstestingagent-ingest-inputs.py
ingested: clean 12 read, 0 rejected; defective 10 read, 0 rejected
sources: Webhook Trigger available; When chat message received skipped; Groq Chat Model approval-required; Fetch_Data approval-required
handoff condition met: every source is available, skipped with a reason, or approval-required
  --sample not declared for this step in the recipe — not passed
→ validate-data-shape  scripts/gigo/scenariostresstestingagent-validate-data-shape.py
clean: 12 in, 12 accepted, 0 rejected -> <scratch copy>/data/verified/scenariostresstestingagent/clean
  --sample not declared for this step in the recipe — not passed
→ transform-quality-check  scripts/gigo/scenariostresstestingagent-transform-quality-check.py
quality-check clean: 12 accepted, 11 reconciled, 1 handed off, 0 failures, 0 duplicates, 0 rejects, 11 flags -> data/verified/scenariostresstestingagent/clean/quality-check.json
  --sample not declared for this step in the recipe — not passed
→ run-approved-tools  scripts/tools/scenariostresstestingagent-run-approved-tools.py
clean: 12 request(s), 11 stress-tested, 1 stopped at the Groq handoff; risk levels {'CRITICAL': 7, 'HIGH': 1, 'MODERATE': 1, 'LOW': 2} -> data/verified/scenariostresstestingagent/clean/stress-results.json
  --sample not declared for this step in the recipe — not passed
→ produce-human-report  scripts/tools/scenariostresstestingagent-produce-human-report.py
report clean: 12 request(s), gate 6 PASS -> reports/generated/scenariostresstestingagent-2026-11-09.md and logs/scenariostresstestingagent-2026-11-09.json

All 6 steps completed.
  Completing is not passing. Gate decisions are a separate, human act:
    snickerdoodle gate scenariostresstestingagent --gate 1 --decision approve --note "..."
```

## Reading it
| Step | Script | What it reported |
|---|---|---|
| 1 | `verify-provenance` | node table, chain, ported nodes and fixtures all match; 0 findings |
| 2 | `ingest-inputs` (new) | 12 clean and 10 defective requests read, 0 rejected; webhook available, chat skipped, Groq and Alpha Vantage approval-required; handoff condition met |
| 3 | `validate-data-shape` | clean: 12 in, 12 accepted, 0 rejected |
| 4 | `transform-quality-check` | 12 accepted, 11 reconciled, 1 handed off at the Groq call, 0 failures, 0 duplicates, 11 flags |
| 5 | `run-approved-tools` | 12 requests, 11 stress-tested, 1 stopped at the Groq handoff |
| 6 | `produce-human-report` | gate 6 PASS; report and agent log written |

## What this does and does not show
- It shows the six steps run in order, each exiting 0, in sample mode: no network, no model call, no credential read.
- The runner passes `--sample` only to a step whose Flags cell in the recipe lists it, which is why it says "not passed" for steps 1, 3, 4, 5 and 6; those steps are sample-only already.
- The default run covers the clean folder for steps 3 to 6 (the runner's own default); the defective folder is exercised by each step's self-test and by step 6 with `--folder defective`.
- **Completing is not passing.** The runner says so itself: gate decisions are a separate, human act, and none has been made. This file is evidence for a person to read; it is not a gate clearance, and the recipe's `status` stays `DRAFT`.

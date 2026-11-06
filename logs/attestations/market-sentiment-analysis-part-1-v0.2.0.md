# Attestation — Market Sentiment Analysis - Part 1

## Attestation

- Recipe: `market-sentiment-analysis-part-1` v0.2.0
- By: Uday Sonawane · 2026-10-02
- Scope: **sample mode over the frozen fixture corpus only.** This attestation does not cover
  live execution, which has never run and is recorded as denied in
  `logs/gate-decisions/market-sentiment-analysis-part-1-gate-5.json`.
- Evidence: `logs/RUN_LOG.md#2026-09-25`, `logs/RUN_LOG.md#2026-10-02`,
  `logs/gate-decisions/` (5 records), `data/verified/.../runs/*/\*-audit.md`.

### Tested

| Ran | Saw | Expected |
|---|---|---|
| All six steps, clean fixture set | step 1 exit 0; steps 2–6 exit 0; 10 rows seen, 10 promoted, 0 rejects, 0 duplicates, 0 flags | A clean corpus produces no findings |
| All six steps, defective fixture set | steps 2, 5, 6 exit 0; steps 3 and 4 exit **1** after reporting every finding; 19 rows seen, 13 promoted, 6 withheld, 5 duplicates, 6 quality flags | Nonzero exit *after* full reporting, never an early halt |
| Defect coverage against `fixture-manifest.json` | **18/18** detected at their exact declared locators — 8 in step 3, 10 in step 4 | Every catalogued defect found in the step and output field the manifest names |
| Negative check: does step 3 catch step 4's defects? | 0 of step 4's 10 leaked into step 3's output | Each step detects only what it owns, so neither masks the other |
| `expected_totals` comparison | price 1, news 1-by-id + **2-by-headline**, reddit 1 duplicate; 1 type violation and 1 stale row per stream — all match | Declared totals reproduce exactly |
| **Break test:** short-circuit the news dedupe after identity match | headline duplicates fell 2 → 1 | Confirms the second pass is load-bearing, not decorative |
| **Break test:** repair the `.json.broken` fixture to valid JSON | step 1 verdict `UNEXPECTEDLY_PARSED`, run halted | A fixture that stops being broken invalidates the catalogue and must stop the run |
| **Break test:** run step 1 against an empty root | status `stop`, 12 stop conditions, exit 1 | Missing required sources are a hard stop, not a warning |
| **Break test:** live mode in the run envelope | step 2 stopped, exit 1, named the required env vars, `live_call_performed: false` | Live mode refuses rather than half-fetching |
| **Break test:** step 5 coercion paths unreachable via the corpus | constructed inputs in a temp root: missing `05. price`, `"N/A"` change percent, empty streams, 25-row news set — each fired its named flag | Flags that the fixtures cannot reach are still proven to work |
| **Break test:** gate 4 — delete-nothing satisfiability | old test passed with zero scripts present; new test compiles all six and fails if any is missing | A gate with no failure path is not a gate |
| **Break test:** gate 5 — four cases | no-call/no-record PASS; no-call/**deny** PASS; **live-call/deny FAIL**; live-call/approve PASS | A recorded refusal must not clear the gate |
| Reproducibility | report and audit byte-identical across reruns; agent log differs only in the contract-required `generated_at`; `scores_digest` stable | Frozen clock makes runs reconstructable |
| Trace chain re-verification | all 6 cited script hashes and all 3 cited source hashes re-verify against their committed blobs | A reviewer can confirm the files the report cites |
| Contract coverage | report 15/15 required sections; agent log 16/16 required fields | Output contract met exactly |
| `node scripts/conformance.mjs` | all conform | Machine half of P4 |
| Gate tests 1–6, as literally written in the recipe | all pass | Gate 5 passes because nothing ran, not because live action was cleared |

### Did not test

- **Live execution. At all.** No network call, model call, Slack message, or email has ever been
  made by this recipe. Live mode is unimplemented and step 2 hard-stops before any fetch.
- **Whether the sentiment score is correct.** Nothing here asserts the number means anything. The
  weights, thresholds and keyword lists are inherited from the source workflow with no derivation,
  backtest, or author. That is a human adequacy judgment (P1) and it has not been made.
- **Wrong-entity signals** — a row that is well-formed, fresh, unique and complete but belongs to a
  *different company*. No check in this pipeline catches it. `DATA_CONTRACT.md` records that this
  class cost 782 purged rows and reached a finished brief on 2026-08-26. The corpus cannot exercise
  it: ticker `FAKE` is unambiguous by construction.
- **Upstream HTTP failure modes** — 401, 403, 429, timeout, empty 200 body. Envelope-level rather
  than record-level, and absent from the fixture set entirely.
- **Encoding defects** — mojibake, lone surrogates, BOM. The source workflow JSON is itself
  cp1252-hostile UTF-8, so this is a live risk rather than a theoretical one.
- **Volume and pagination.** The largest fixture holds 8 rows. Nothing tests the `limit=50` ceiling
  or any paging behaviour.
- **The `redditMentions > 20` branch** in the ported scoring. The corpus has at most 6 social rows,
  so two findings in the original can never fire here.
- **Any independent test suite.** There are no unit tests for the six scripts. Everything above was
  exercised through the pipeline itself or by hand-constructed inputs, and CI runs none of it.
- **Cross-platform behaviour.** Everything ran on Windows with a patched `python3`. The scripts have
  never executed on Linux or macOS, and two line-ending defects have already surfaced from exactly
  that gap.
- **Concurrency, partial writes, or interrupted runs.** Every run was clean and sequential.

### Broke during testing, fixed

- **`python3` resolved to the Microsoft Store alias stub** — printed an install message and exited 0,
  so conformance's Python and YAML checks silently did nothing for the first half of the build, and
  `archive-guard.sh` failed open. Fixed by putting a real `python3` ahead of it on PATH.
- **`Path.write_text` emitted CRLF on Windows**, making every artifact hash platform-dependent.
  Fixed with `newline='\n'` at all five write sites.
- **`.gitattributes` scoped too narrowly** — a rebase re-checked-out the step scripts as CRLF, so the
  report cited script hashes no reviewer on Linux could reproduce. Fixed by extending the rule to
  `scripts/`.
- **The news dedupe short-circuited**, disabling the headline pass that catches syndicated copies.
  Fixed with independent passes.
- **`"yesterday"` was double-flagged** as both a type violation and an unreadable timestamp,
  inflating counts past the declared totals. Fixed by suppressing the second when the first fires.
- **Step 5 claimed `raw_layer_access: none` while reading the run envelope from `data/raw/`.** Fixed
  by stating precisely what is read; a false provenance claim is worse than the access it conceals.
- **Step 6 claimed byte-identical reruns** when its agent log carries a required `generated_at`.
  Fixed the claim, not the behaviour.
- **Gate 4's test could be satisfied by doing nothing** — it passed if the script existed *or* if a
  DEV-TODO marker remained. Fixed to compile all six.
- **Gate 5's test could be satisfied by doing nothing**, then — after the first fix — by the mere
  *existence* of a decision record, so the deny written on 2026-10-02 cleared it exactly as an
  approval would. Fixed twice; it now reads `approved_for_live_action` out of the record.

---

## Why this does not promote the recipe to VERIFIED

`SNICKERDOODLE.md` defines the lifecycle as:

```
DRAFT ──► SPECIFIED ──► RUNNABLE-SAMPLE ──► RUNNABLE-LIVE ──► VERIFIED
```

The recipe is at `RUNNABLE-SAMPLE`. Reaching `VERIFIED` requires passing through
`RUNNABLE-LIVE`, whose gate test is *"live run with a human clearing every gate"*, evidenced by
logged gate decisions.

Neither condition holds:

- **No live run exists.** Live mode is unimplemented; step 2 stops before any fetch.
- **Not every gate is cleared.** Gate 5 is recorded as `decision: deny`, with
  `approved_for_live_action: false`.

Setting `status: VERIFIED` today would assert a live run that never happened and a gate clearance
that was explicitly refused. The constitution is direct about this: *"The status is a claim; per P3,
each transition needs a logged evidence artifact. Editing the status field without the evidence is a
violation, not a promotion."*

This attestation is still worth recording. It is bound to v0.2.0, it documents what was actually
exercised, and its **Did not test** section is the honest boundary of that work — which is the point
of the format. What it attests to is a thoroughly tested *sample* recipe, not a verified live one.

### What VERIFIED would require, in order

1. **Implement live mode** in step 2: real fetchers reading credentials from the environment only.
2. **A second fixture set** covering 401/403/429/timeout/empty-200, with expected detections declared
   the way the current corpus declares its 18.
3. **Reopen gate 5** against the four preconditions in its decision record, and record an approval
   naming the approver — a decision, not a checkbox.
4. **A live run with every gate cleared**, logged. That earns `RUNNABLE-LIVE`.
5. **A fresh attestation bound to the recipe version that ran live**, since any edit to the recipe or
   its scripts voids this one.

Steps 1 and 2 are code. Step 3 is a judgment that has already been made once, and made *no*.

---

## Voided — 2026-11-05

This attestation no longer binds. Point 5 above states the rule it is being held to: any
edit to the recipe or its scripts voids it.

**What changed:** the recipe's Step Commands table was corrected at v0.2.1. It advertised
`--no-write` on verify-provenance, which that script does not implement, and omitted four
flags the scripts do implement (`--run-dir`, `--verified-dir`, `--input-dir`, `--run-id`).
The table is not documentation — `snickerdoodle run` uses it to decide what to pass
through — so the entry was a live defect, not a typo.

**No script was edited.** The six step scripts are byte-identical to the ones exercised in
the Tested table below, so every row there still describes behaviour that is still true.
What is no longer true is the binding: the attestation was taken against recipe v0.2.0,
and the recipe is now v0.2.1.

**What this costs:** a fresh attestation against v0.2.1, which is cheap — the Tested table
can be re-run as written. It is recorded rather than quietly re-pointed because an
attestation that follows its recipe across edits is not evidence of anything.

The record is kept in full. Nothing above this line was changed.

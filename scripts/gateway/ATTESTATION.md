@'
# Attestation -- Inference Gateway

- Component: `scripts/gateway/`, policy 0.3.0, tiers 0.4.0, prices 2026-09-17
- By: Simba · 2026-11-09
- Covers: the gateway as of the Sprint 9 packaging commit. Any edit to the
  code or its config after this date voids it.

## Tested

| Ran | Saw | Expected |
|---|---|---|
| `pytest scripts/gateway/tests -q` | 212 passed, 0.97s, no network | all pass |
| `baseline.py` -- 24 fixtures x 3 tiers x 3 repeats | 216 calls, 0 provider errors, $0.0147, cheap 92% / mid 98% / strong 92% correct | every tier answers; correctness measured per tier |
| `decide.py` -- six policies replayed, fitted on repeats 1-2, evaluated on repeat 3 | only "always cheap" cleared the thresholds: 31% cheaper, 31% faster, correctness unchanged | at least one candidate clears, or none does and we say so |
| `judge_run.py --samples 4` then `score.py` then `agreement.py` | Cohen's kappa 0.00; the judge called all 28 comparable pairs a tie while the human separated 27 of 32 | the judge agrees with a human well enough to use |
| Deliberate break: both tiers scripted to fail | `GatewayResult` with `error` set, no exception, 2 logbook rows, outcome `provider_error` on both | the caller gets a result, and the outage is in the record |
| Deliberate break: a 429 saying "request too large" | classified terminal, no retry | not retried -- waiting cannot shrink a prompt |
| Deliberate break: 200 concurrent appends to the logbook (Sprint 1) | 153 of 200 rows written, silently, on Windows | 200 rows |
| Deliberate break: a model priced at nothing | `UnknownModelPrice` raised before the adapter is touched | refused, not logged as free |
| `audit.py --freeze` after the merge normalised line endings | 2 files flagged as changed; parsed content verified identical to `2df2f37` before re-cutting | drift detected, and a re-freeze only after proving no label moved |

## Did not test

- **Any real Mycroft traffic.** No request corpus exists in this repository:
  203 of 217 sample payloads are placeholders. Every number here describes 24
  synthetic fixtures, 4 per task type against a target of 30.
- **Quality on `summarization` and `rag_answer`.** The judge built for them
  scored kappa 0.00 and was retired. They are routed on cost alone. This is
  the largest hole in the work and it is not closed.
- **Whether two disputed fixtures are model errors or key errors.**
  `contra-003` and `extract-004` account for every wrong answer in the
  baseline. No second reader has ruled.
- **A second provider.** One provider, one credential, every tier. An auth
  failure or a rate limit takes out the whole ladder at once, which is tested
  in simulation and never in life.
- **The retry rule under the shipped policy.** No check failed at all in the
  held-out repeat used for the decision, so escalation contributed nothing to
  it.
- **The provider's own usage console against the logged costs.** The one check
  this code cannot perform on itself.
- **Anything at volume.** The largest run was 216 calls. Nothing has been run
  concurrently against a live provider.
- **Behaviour on a non-Windows machine** beyond the test suite.

## Broke during testing, fixed

| What failed | Where | Fix |
|---|---|---|
| Concurrent appends silently lost 47 of 200 rows on Windows | `logbook.py` | threading lock plus an OS file lock on a sidecar |
| Per-attempt cost averaging understated a retried request by half | `report.py` | request/attempt split; the wrong average kept, labelled, and pinned by a test |
| `max_tokens=16` returned an empty paid-for answer | gate script | budget raised to 256 after reading the raw output |
| Reasoning returned inline passed every check | `adapters/groq.py` | `strip_reasoning()` plus a real answer check; gate script now exits 1 |
| A 1024-token budget exceeded a 1000-per-minute cap, refusing every strong call | `policy.json` | lowered to 896 and re-gated live |
| `verdict_with_quote` failed correct answers that quoted both statements | `prompts.py` | prompt narrowed to one continuous span |
| `cites_context` failed correct answers citing as 【0】 | `validators.py` | fullwidth brackets translated before matching |
| A daily log file let one run's requests be counted in another's summary | `bench/run.py` | timestamped files, summary scoped to its own request ids |
| The answer sheet applied unedited and reported success | `bench/label.py` | refuses to write when nothing differs; every row marked CHANGED or unchanged |
| `FINDINGS.md` and `RUN_LOG.md` replaced rather than appended, three times | process | recovered from history; appends now go through `Add-Content` |

## Judgment

The gateway measures what it claims to measure, and the decision it now
encodes -- send everything to the cheap tier -- rests on 216 recorded calls
with every figure traceable to a logged row. What it does not have is any
evidence from real traffic, or any quality measure at all for two of its six
task types. Treat it as a measured recommendation on a synthetic benchmark,
not as a validated production router.
'@ | Set-Content -Encoding utf8 scripts/gateway/ATTESTATION.md
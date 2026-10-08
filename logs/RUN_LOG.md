## 2026-10-01 -- Gateway Sprint 6: the scorer check

- **Recipe:** Adaptive Model Routing & Inference Gateway (Sprint 6 of 9).
- **Gate:** Blind human scoring of the judge's own pairs, by a named human,
  before any agreement figure was computed.
- **Cleared by:** Simba · 2026-10-01
- **Inputs:** 24 fixtures re-frozen 2026-10-01 (answer key corrected); policy
  0.2.0; tiers 0.4.0; prices 2026-09-17; GROQ_API_KEY.
- **Commands:** `label.py --template answers.json --ids ...`;
  `label.py --by "Simba" --from answers.json`; `audit.py --freeze`;
  `judge_run.py --samples 4` (32 comparisons, 128 calls, $0.01911);
  `score.py --by "Simba"` (32 scored); `agreement.py`;
  `python -m pytest scripts/gateway/tests -q` (168 passed).
- **Outputs:** `bench/score.py`, `bench/agreement.py`; `--samples` on
  `bench/judge_run.py`; BOM-tolerant sheet reading and an unchanged-sheet
  refusal in `bench/label.py`; `bench/scores/2026-10-01T061158-simba.json`;
  `bench/results/2026-10-01T061158-judge.json` and `-agreement.json`;
  `logs/gateway/runs/2026-10-01T061158-judge.jsonl`.
- **Result:** **Cohen's kappa 0.00.** The judge returned `tie` on all 28
  comparable pairs and no verdict on 4; the human picked a winner on 27 of 32
  (cheap 11, mid 16, tie 5). Raw agreement 18%, exactly chance. Per task type:
  rag_answer 27% raw / kappa 0.00; summarization 8% raw / kappa 0.00. Human
  order bias: 13 first-shown vs 14 second-shown, none detectable.
- **Answer key corrected first:** `sent-001` and `sent-004` changed from
  `negative` to `positive`, and acceptable values were written for all four
  extraction fixtures. Flagged in Sprint 3 review, confirmed in Sprint 5, fixed
  here before anything was measured against them.
- **Findings:** `scripts/gateway/FINDINGS.md` section 10. Section 9's
  conclusion about cheap and mid being indistinguishable is withdrawn.
- **Not verified:** whether a forced-choice judge (no TIE option) does better.
  That is the next experiment and has not been run.
- **Open issues:**
  - `bench/score.py` and `bench/agreement.py` have no unit tests yet; the kappa
    calculation in particular carries weight and needs them.
  - The human's notes suggest a possible preference for longer answers; mid
    writes longer answers. Confound to watch in Sprint 7.
  - Coverage is 8 open-ended fixtures against a target of 30 per task type.
  - `main` is behind `origin/main`.
  - GROQ_API_KEY still needs rotating; it has now been exposed four times.
  
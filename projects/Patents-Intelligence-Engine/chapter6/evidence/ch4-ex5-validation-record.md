# Chapter 4, Exercise 5 — Validation Record

**Artifacts validated:** `theses/agent-recipe-STM.md`, `theses/human-card-STM.md`

## Validation Checklist Results

| Check | Result | Reasoning |
|---|---|---|
| Correctness | Pass | Recipe math matches metrics already defined in the effort plan — nothing new invented. |
| Completeness | Pass | Card carries purpose, caveats, open questions; evidence summary explicitly blank. |
| Scope | Pass | No decision, evidence summary, or verified/real-signal label filled. |
| Reproducibility | Pass | Recipe's named inputs and steps are re-runnable once pending inputs exist. |
| Stop check | Pass | Recipe explicitly states it cannot run to completion yet — no faked output. |
| Failure-mode check | Pass | No false sense of a decision already made; honest incompleteness surfaced instead. |

**Verdict:** Passes. The genuinely useful output of this exercise was catching an unresolved gap in the Chapter 2 threshold-setting (what happens if Q3 lands between 35–37%) — worth resolving before Q3 actually reports.

**AI Use Disclosure:** The AI drafted the recipe spec and the card scaffold, correctly leaving the decision block, evidence summary, and any verification/signal labels empty. The AI could not determine the decision itself, whether the caveats are acceptable given the user's actual risk tolerance, or what should happen if Q3 lands in the unaddressed middle range — all of which remain open human decisions.

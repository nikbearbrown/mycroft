# Limitations — what this does NOT prove

This project checks one thing: **does AI-generated code faithfully implement the rule it was
given?** That is *translation fidelity*. It is deliberately silent on everything else. The
honest boundaries below matter as much as the capabilities.

## The core limitation, with a concrete example

**It verifies fidelity to the rule — not whether the rule should exist.** A rule can be
translated perfectly, pass every check, get approved as "Trustworthy" — and still be a
terrible, even unlawful, policy.

### Worked example: passes cleanly, still discriminatory
Rule: **"Approve the loan only if the applicant's ZIP code is one of: [an approved list]."**

Walk it through the pipeline:
1. The human writes an answer key: applicants in the listed ZIPs → approve, others → deny.
2. The answer key is frozen and hashed.
3. The AI writes `check_applicant` that returns "approve" iff the ZIP is in the list.
4. **Validator:** runs the code — output matches the answer key on every case. ✓
5. **Reasoner:** re-reads the rule — a ZIP-list rule is unambiguous, so it agrees. ✓
6. Verdict: **Trustworthy.** A human approves it.

The code is a *flawless* translation of the rule. But ZIP code is a well-known **proxy for
race and income** — this is redlining, and it would be illegal in real lending. The pipeline
has **no opinion on that** and never will, because fairness is not what it measures. A faithful
translation of a discriminatory rule sails through **cleanly**. That gap is the single most
important thing to state out loud when presenting this.

## Other limitations

- **It only catches bugs your test cases exercise.** If no example hits the boundary (or the
  zero-debt branch, or an income of 0), that bug slips through. More/adversarial cases help,
  but coverage is never complete.
- **Both LLM checks are non-deterministic.** A single run is an anecdote — the same rule can
  pass one run and fail the next. Use multiple runs (`app/eval.py`) for a real failure rate.
- **The reasoner is itself a fallible LLM.** It's a strong *second opinion*, not ground truth.
  On genuinely ambiguous rules ("recent," "high income") it must guess a threshold too, so it
  can disagree with your intent for reasons that aren't the code's fault — which shows up as
  "answer key looks wrong / rule ambiguous," not a clean catch.
- **Correlated blind spots remain.** Different models reduce, but don't eliminate, the chance
  that the code, the reasoner, and your answer key all share the same wrong assumption.
- **Tamper-evidence is not tamper-enforcement.** The frozen hash lets you *detect* a changed
  answer key; the run path does not yet *block* a tampered run automatically.
- **Not production.** No real applicant data, no deployment path, no monitoring, no versioning.
  A real system would add fairness review, adversarial testing, and legal sign-off on top.

## One-line honesty statement for the demo
*"This proves the code matches the rule — not that the rule is fair, and not that the code is
correct on cases I didn't test. A discriminatory-but-faithful rule would pass it cleanly."*

# Design Decisions

Future-you-facing. The load-bearing choices behind this project and the shortcuts that were
**considered and deliberately rejected**. If you're tempted to undo one of these to save time,
read the reason first — most of them are the thesis, not conveniences.

---

## Decisions we made (and the alternative we rejected)

### 1. Lock the answer key *before* code generation
The human commits the correct answers, they're frozen and hashed, and only then may the AI
generate code.
**Rejected:** letting answers be edited any time. **Why:** if you can adjust answers after
seeing the code, "the checks passed" proves nothing. Commit-first is what makes the whole test
honest — it's the core of the thesis, not a feature.

### 2. Two separate checkers — never merged
The **Validator** executes the code; the **Reasoner** re-reads the rule and never sees the code.
**Rejected:** one checker, or a single agent that both writes and judges. **Why:** a checker
that sees the code can be anchored by a convincing-looking bug; if one model both wrote and
judged, it could bless its own mistake. Independence is the point — where they disagree is the
diagnosis.

### 3. Generator and reasoner run on *different* models
Generator = Claude Sonnet 4.5; Reasoner = Claude Opus 4.8.
**Rejected:** the same model for both. **Why:** the same model shares the same blind spots, so
agreement would mean less. Different models make agreement meaningful.

### 4. The guardrail rejects, never repairs
Malformed / non-parsing AI output is recorded as `"unrunnable"` — it is not auto-fixed.
**Rejected:** silently fixing the code so it runs. **Why:** the moment we repair the AI's
output, we're testing ourselves, not the AI. A rejection is an honest outcome.

### 5. The generator is given the data schema (field names + types) — but not the answers
It's told `days_since_late_payment (number)`, not the values or expected outcomes.
**Rejected:** making the AI guess field names. **Why:** guessing caused failures for *schema*
reasons ("couldn't guess my columns") that drowned out real *logic* errors. A real developer
always knows the schema; withholding it was an unfair test. The answers are never in the prompt.

### 6. Every run regenerates code fresh — no caching, no reuse
**Rejected:** reusing a previous run's generated code. **Why:** reuse is exactly how you'd
accidentally cherry-pick a favorable result. Each run is an independent roll.

---

## Rejected shortcuts — tripwires (do NOT undo these)

- **Don't merge the Validator and Reasoner** to save time — that's a thesis violation, not a
  simplification (see #2).
- **Don't let a re-run reuse prior generated code** — this is how you'd cherry-pick (see #6).
- **Don't auto-repair AI code in the guardrail** — reject only (see #4).
- **Don't leak the answer key or thresholds into the generator prompt** — it may see the rule
  and the field schema, never the expected outcomes (see #5).
- **Don't feed one checker's output into the other** — their independence is the whole value.

---

## Deliberately NOT built

### Auto-retry on transient failure — dropped
The spec called for "retry once, then halt." We chose not to build it.
**Why:** this is an attended tool — you run it and watch it, so a network blip just means you
re-run by hand. Retry adds no thesis value, and done carelessly (retry many times, or on any
failure) it risks laundering a *systematic* failure into a "transient" one — which is the
cherry-picking the thesis forbids. If this ever became an unattended/automated system, retry
would need to come back.

---

## Accepted limitations (conscious trade-offs for a proof-of-concept)

- **The frozen hash is tamper-*evident*, not tamper-*enforced*.** It proves a change happened;
  the run path does not yet recompute-and-block on mismatch. Acceptable for a POC; would be
  enforced in a real system.
- **Fidelity, not fairness.** This checks whether code matches the rule — never whether the rule
  is fair or legal. A faithful translation of a discriminatory rule passes cleanly. This is a
  deliberate scope boundary; see [`LIMITATIONS.md`](LIMITATIONS.md).

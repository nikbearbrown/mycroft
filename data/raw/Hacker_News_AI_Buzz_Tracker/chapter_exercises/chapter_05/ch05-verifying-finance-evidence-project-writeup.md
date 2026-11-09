# Chapter 5 Project: Verifying Finance Evidence (META)

Project: Your Own Mycroft. Ticker: META. Builds on agent-recipe.md, human-card.md, sources-of-truth.md, and the /evidence contracts from Chapter 3–4.

## Exercise 1 — When to Use AI

AI assistance was appropriate for, and used on, these tasks this chapter:

- Running the mechanical adequacy checks (completeness, freshness, control-total tie, mapping/period consistency) across every metric on human-card.md against the /evidence contracts. This works because each check is a rule applied to data I already sourced and can re-check myself.
- Classifying each metric's warranted-verb level (can say / can suggest / cannot claim / needs review). This works because the classification is against evidence I supplied and confirmed, not against the model's own judgment of the business.
- Flagging where the card's language could slide into causal overreach — specifically, the risk of reading FoA operating income growth and AI capex as cause-and-effect rather than two reported trends. This works because it's pattern-spotting in text I can independently re-read.

The tell held here too: I could evaluate every row in `evidence-audit.md` against the underlying /evidence contract myself, which is why I trust the audit's mechanical columns.

## Exercise 2 — When NOT to Use AI

These stayed mine, and the audit left them blank on purpose:

- Whether the forward-P/E gap is *material* enough to keep the decision at Hold/Watch rather than moving forward on the operating evidence alone. Materiality depends on how much weight I put on valuation versus fundamentals, which the audit can't set for me.
- Whether the regulatory exposure's "up to hundreds of billions" ceiling changes my risk view. That's a values call about how much weight a maximum-theoretical figure should carry versus an expected outcome — the audit can surface the number, not weigh it.
- There is no options-signal judgment to make on this desk at all, since no options-chain provider is on file — the audit confirms that gap stays unresolved rather than getting silently filled in with a plausible-sounding provider or number.

The tell: I'd have crossed the line if I let the audit's "7 of 9 rows are can-say" tally stand in for "the evidence is sufficient" — sufficiency is still mine to decide.

## Exercise 3 — LLM Exercise

Built `evidence-audit.md` in the desk repo: one row per metric on human-card.md, columns for source, completeness, freshness, control-total tie, mapping/period consistency, warranted-verb level, and an "adequate for decision" column left blank. Added a signals section noting none exist to audit (no options-chain provider on file), and a causal-claims section flagging the one place overreach could creep in (capex vs. FoA income).

## Exercise 4 — CLI Exercise

The audit was built read-only against `agent-recipe.md`, `human-card.md`, `/evidence/*.md`, and `sources-of-truth.md` — no live fetch, no decision made, no signal called real, matching the desk's CLAUDE.md constraint. It stopped short of filling any adequate/material column, and it did not touch the forward-P/E gap beyond flagging it as "cannot claim" (wrong source type — trailing, not forward — per the existing /evidence contract's own correction note).

## Exercise 5 — AI Validation Exercise

Checked `evidence-audit.md` against the chapter's validation checklist:

- **Correctness.** Pass. Each row's completeness/freshness/control-total read matches what its /evidence contract actually states.
- **Completeness.** Pass. Every metric on human-card.md got an audit row; the audit also explicitly notes the options-signal section has nothing to check, rather than skipping it silently.
- **Scope.** Pass. Nothing was marked adequate, material, or real; every judgment column is blank.
- **Signal vs. noise.** N/A on this desk — no options-chain provider is on file, so there's no expiration window or term structure to screen. The audit states this explicitly rather than leaving a blank that could be misread as "checked, nothing found."
- **Causal check.** Pass. The one place a causal story could form (capex → income growth) is flagged as unsupported by the current evidence, with a NEEDS HUMAN tag for if the card's language ever tightens into a causal claim.
- **Failure-mode check.** Pass. No confident "adequate" stopped further checking; the forward-P/E row stays "cannot claim" rather than getting rounded up to "can suggest" just because a number (17) exists in the draft.

AI Use Disclosure: The AI produced the mechanical adequacy audit and warranted-verb classification across all nine evidence-audit metrics, which I used as a pre-screen before judging the card myself. It could not determine whether the forward-P/E gap or the regulatory ceiling figure are material enough to change the Hold/Watch decision, and it could not evaluate any options signal, since none exists on this desk.

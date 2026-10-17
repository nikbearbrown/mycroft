# Chapter 4 Project: Two Customers (META)

Project: Your Own Mycroft. Ticker: META. Builds on sources-of-truth.md and the /evidence contracts from Chapter 3.

## Exercise 1

AI assistance is appropriate for these tasks this chapter:

- Drafting the agent recipe's deterministic spec, which sources to pull and in what order, against the sources I already fixed in Chapter 3. This works because it is specification against a list I supply, and I check each step against sources-of-truth.md.
- Translating the confirmed evidence figures into draft caveats, listing what the recipe did not check. This works because it is enumeration over the recipe's own stated scope, which I confirm.
- Drafting the human card's fixed sections, purpose, caveat list, open questions, as a scaffold. This works because the decision block and evidence summary stay mine to fill.

The tell is the same as before: I am using AI well when I can evaluate the output against independent criteria, in this case whether the recipe actually stops before interpreting.

## Exercise 2

These tasks require my own judgment:

- Writing the decision itself. The call encodes my risk tolerance and horizon and is the one thing a generated card cannot hold without becoming the fluent-memo failure this chapter describes.
- Deciding whether the caveats are acceptable for this decision, for instance whether missing options data actually matters given I am not trading options right now.
- Judging whether any forward-looking figure, like the Reality Labs 2026 guidance, is trustworthy enough to weigh, since that requires judging management's credibility, not just reading the sentence.

The tell is that I have crossed the line when AI output becomes my reason to act rather than a tool for reaching my own decision.

## Exercise 3

I built two files in the desk repo: `agent-recipe.md`, which lists the sources, the exact figures to pull, the output schema, and the stop conditions, ending in an explicit STOP line before any interpretation; and `human-card.md`, which carries the purpose, a blank evidence summary for me to fill, a caveat list, open questions, and an empty decision block.

## Exercise 4

The recipe binds only to sources already fixed in sources-of-truth.md and the /evidence contracts, adds no new sources, and does not touch options data since I have no options-chain access. The human card's decision block was left empty by design; filling it is my next step, not something completed this session.

## Exercise 5

I checked both files against the chapter's validation checklist.

Correctness. Pass. The recipe's steps pull exactly the figures already confirmed in the /evidence contracts, and cite the same sources.
Completeness. Pass. The human card carries purpose, caveats, and open questions, and the evidence summary is explicitly left for me to fill.
Scope. Pass. Neither file fills the decision block or marks anything verified beyond what was already confirmed in Chapter 3; the forward-P/E gap and missing options provider are flagged rather than papered over.
Reproducibility. Pass. Someone else could rerun the recipe against the same named filing and get the same figures, since every input names a specific accession and period.
Stop check. Pass. The recipe ends in an explicit STOP line before any interpretation, and does not draft a conclusion.
Failure-mode check. Pass. No signal is called real, since no options data is present at all, and the card's decision block stays visibly empty rather than implying a call has been made.

AI Use Disclosure. The AI produced the recipe spec and the human card scaffold, including the caveat list and open questions, which I used as a structure to fill in and check against my own sources. It could not determine the decision itself, and it could not determine whether the missing options data or the flagged forward-P/E gap are acceptable caveats for the call I am about to make, since that weighing is mine.

# Chapter 1 Project: The Fluency Trap (META)

Project: Your Own Mycroft. Ticker: META. The desk repo is in `../your-own-mycroft/`.

## Exercise 1

In this chapter's work, AI assistance is appropriate for these tasks:

- Splitting my META thesis into its individual claims so that none of them slip by unexamined. This works because it is mechanical decomposition of text I wrote myself, and I can confirm that nothing was dropped or invented.
- Computing the mechanical numbers off a META options chain that I supply, such as the put to call ratio and the slope between the near term and the longer term expirations. This works because it is arithmetic and reformatting against data I paste in, and I can check the result against the chain.
- Summarizing a section of META's 10-K or 10-Q, or an earnings call transcript, into a list of candidate claims to check. This works because it is summarizing and extraction, and I verify each line against the filing.

The tell is that I am using AI appropriately when I can evaluate the output, because I have independent criteria, a filing line or the actual options data, to judge whether it is correct, complete, and fit for purpose.

## Exercise 2

In this chapter's work, these tasks require my own judgment, and handing them to AI is not appropriate. The reason is not that AI cannot produce output, but that its output here cannot be trusted without the same expertise and the same accountability it would take to do the task myself.

- Deciding whether the thesis is true, or whether to buy META. The model has no access to the source filings, no stake in the outcome, and real money rides on it. A confident "strong buy, target two hundred dollars" is exactly the variance note with a fabricated driver from this chapter, only now it is in a brokerage app.
- Judging whether a META options signal is real institutional positioning or just short dated retail noise. That distinction needs the actual term structure data and market context that the model did not ground itself in, and it will narrate a confident story either way.
- The buy, hold, or sell decision itself. It carries accountability and my capital, and a generated recommendation cannot defend itself when the position is down twenty percent.

The tell is that I have crossed the line when I am using AI output as my reason to trade rather than as a tool for reaching my own decision. If I could not explain the trade without the AI, then the AI did the work that should have been mine.

## Exercise 3

I ran the claim interrogation prompt on my META thesis, corrected the tags, and then checked the factual claims against Meta's reported full year 2025 results before marking anything verified. The result is saved as `../your-own-mycroft/theses/META.md`, with sources listed at the bottom of that file. The factual claims about cash flow, engagement growth, heavy AI spending, the Reality Labs loss, and the disclosed regulatory matters are now verified and sourced. The forward looking claims, such as whether AI will strengthen ad targeting, stay tagged inferred or taste, because no source can confirm a prediction in advance. Since I am new to investing, the filing figures were pulled on my behalf for this exercise; the file notes that in normal use I would open them myself.

The charter, `../your-own-mycroft/CANNOT-KNOW.md`, records what no model can know about me. It is honest about my starting point, that I am a beginner with no investing experience doing this as a learning exercise and have committed no real money, and it sets my risk tolerance as low and my sources of truth as META's filings and the actual options chain rather than tweets, forum posts, or a fluent summary.

## Exercise 4

I set up the desk repository in `../your-own-mycroft/`. It has four folders, theses, evidence, signals, and book, a README that describes the desk using only facts from the two files above, and a CLAUDE.md carrying the rule that the assistant never marks a claim verified, never labels a signal real, and never recommends, sizes, or executes a trade. The thesis audit sits in theses and the charter sits at the repository root. I did not let the README add an upbeat summary or any claim that was not already in my files, and nothing was deleted.

## Exercise 5

I evaluated the claim audit table from Exercise 3 against the chapter's checklist.

- Correctness. Pass. Each factual claim tagged verified is now tied to a specific figure from Meta's full year 2025 results, with the sources listed in the file. The claims left as inferred or taste are forward looking or subjective, so leaving them unverified is correct rather than a gap.
- Completeness. Pass. The audit captures the overall conclusion, the cash flow claim, the engagement claim, the heavy AI investment claim, the three forward looking AI benefit claims, the high expectations valuation claim, the four risk claims, and the metaverse cost claim. No claim from the thesis was left out.
- Scope. Pass. The audit added no rating, no price target, no source of its own, and no buy or sell opinion.
- Signal versus noise. Not applicable here. My thesis makes no options market claim, so there is no signal claim to test against the actual term structure yet.
- Owner test. Pass. For each factual claim I can now point to the figure that settles it, from Meta's full year 2025 revenue, cash flow, capital expenditure, segment results, and disclosed legal matters. The remaining open question is not a missing source but a judgment, namely how to weigh these facts.
- Failure mode check. Pass. No confident sentence made me stop checking, there is no verified tag without ground truth, and there is no price target presented as a fact. The fluent last sentence of the thesis is flagged as taste, since it is the judgment I own.

All items pass, so I filed the table.

AI Use Disclosure. The AI produced a first draft of the claim split and proposed tags from my thesis, then pulled the full year 2025 filing figures on my behalf to ground the factual claims, and I used all of this as the prepared surface for my audit. The things the AI could not settle were judgments, namely whether a forward price to earnings ratio around 17 counts as high expectations, how much weight each risk deserves, and whether I could defend a trade, all of which depend on my horizon and risk tolerance rather than on any figure.

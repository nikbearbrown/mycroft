# Chapter 3 Project: The Verified Finance Data Contract (META)

Project: Your Own Mycroft. Ticker: META. Builds on the effort plan in `../your-own-mycroft/effort-plan.md`.

## Exercise 1

AI assistance is appropriate for these tasks this chapter:

- Drafting the empty field skeleton of a data contract, source, period, entity, version, owner, freshness, retrieval timestamp, for each metric from my effort plan. This works because it is structured templating against a list I supply, and I check the fields against the chapter's own list before using them.
- Sorting my candidate sources into source of truth, context only, or not a source, as a first pass I then correct. This works because the categories are fixed by the chapter and I am the one who confirms each placement.
- Formatting the finished contract stubs into consistent files under an evidence folder. This works because it is layout, not content, and every cell stays blank until I fill it myself.

The tell is the same as before: I am using AI well when I can evaluate the output against independent criteria, in this case the chapter's own field list and tier definitions.

## Exercise 2

These tasks require my own judgment:

- Deciding whether a specific vendor or feed actually counts as a source of truth. The model has no standing to rank provenance, and letting it decide is exactly the failure mode this chapter is about.
- Marking any cell "Verified." Verification means I opened the filing or the chain data myself and confirmed the number is there, and no model output can stand in for that act.
- Supplying an actual accession number, dollar figure, or timestamp into a contract cell. The model does not have the filing open, so any value it offers is a guess dressed up as data.

The tell is that I have crossed the line when I start treating a populated cell as settled because it looks complete, rather than because I checked it.

## Exercise 3

I built `sources-of-truth.md`, a three tier list ranking SEC EDGAR filings as the source of truth for company financials, leaving the options-chain provider line explicitly blank until I name the actual vendor I use, and placing analyst notes and news in context only and social media and AI paragraphs in not a source.

## Exercise 4

For each decision-moving metric in the effort plan, I created an empty contract stub under `../your-own-mycroft/evidence/`: ad price and impressions trend, operating margin and free cash flow against capital expenditures, the forward price to earnings ratio, regulatory and legal exposure, the Reality Labs loss trajectory, and disclosure of new revenue opportunities. Every stub has the same eight fields and every cell is blank, including Verified. Nothing was populated because I have not yet opened the underlying filings for this chapter's session.

## Exercise 5

I checked the sources list and one stub against the chapter's validation checklist.

Correctness. Pass. The only named source of truth is SEC EDGAR, which is genuinely authoritative, and the options-chain provider tier is left blank rather than filled with a guess.
Completeness. Pass. All six decision-moving metrics from the effort plan have a stub, and each stub carries all eight contract fields.
Scope. Pass. No cell contains a value, an accession number, or a verified mark; the AI produced only the tier structure and the empty template.
Provenance. Cannot determine yet. I cannot name the exact filing and line for any metric until I open the actual 10-K and 10-Q and fill the cells myself, which is the next session's work.
Source-tiering. Pass. Tweets, news, and AI paragraphs are placed in context only or not a source, never in source of truth.
Failure-mode check. Pass. Nothing in the sources list or the stubs reads as verified when it is not; the blank cells are visibly blank rather than quietly filled.

AI Use Disclosure. The AI produced the three-tier source ranking and six empty data-contract stubs from the metrics I listed in my effort plan. It could not determine whether my actual options-chain vendor qualifies as a source of truth, since I have not yet named it, and it could not determine whether any given number ties to its filing, since verification requires me to open the source myself.

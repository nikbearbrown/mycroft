## Agent Recipe — META
 
Gathers and computes only. Binds to sources-of-truth.md and the /evidence data contracts. Stops before any interpretation.
 
## Inputs
 
- Meta Platforms Form 10-K, fiscal year 2025. Entity: Meta Platforms Inc, consolidated (Family of Apps and Reality Labs segments where noted). Accession: sec.gov/Archives/edgar/data/0001326801/000162828026003942/meta-20251231.htm.
- Meta Reports Fourth Quarter and Full Year 2025 Results, press release / investor relations. Period: full year 2025.
- Forward price to earnings reference. Resolved — stockanalysis.com/stocks/meta/statistics/, which explicitly reports a "forward PE ratio" as a distinct labeled field (unlike macrotrends.net, which only reports trailing P/E despite the URL naming a general "pe-ratio" page). Cross-checked against GuruFocus's forward-PE field for consistency. As of July 10, 2026: forward P/E 19.37 (source: stockanalysis.com). See evidence/forward-price-to-earnings.md for the full spot-check and volatility caveat.
- Options-chain provider: none named. No brokerage or market-data account exists for this desk, so no options input is in scope for this run.

## Steps

1. Pull operating cash flow, free cash flow, and capital expenditures (including finance-lease principal payments) for full year 2025 from the 10-K MD&A.
2. Pull Family of Apps operating income and Reality Labs operating loss for full year 2025 from the segment reporting note.
3. Pull average price per ad and ad impressions year-over-year change for full year 2025 from the 10-K or press release.
4. Pull the quantified legal exposure figures and the aggregate exposure statement from Item 3, Legal Proceedings, and the risk disclosure language from Item 1A.
5. Pull management's stated 2026 Reality Labs guidance from Item 1A Risk Factors.
6. Check each future 10-Q, as it is filed, for a disclosed revenue line tied to AI products or business messaging, distinct from general advertising revenue.
7. No options-based computation runs, since no options-chain input is in scope (see Inputs).

## Output schema

A findings table with required fields: `metric`, `value`, `period`, `entity`, `source_accession_or_url`, `retrieval_timestamp`, `owner`.

## Stop conditions

- Halt if the 10-K accession link does not resolve or the filing period does not match fiscal year 2025.
- Halt if a figure pulled from the press release disagrees with the same figure in the 10-K without an explanation (e.g., GAAP vs. non-GAAP definition).
- Halt and flag rather than proceed if a forward-P/E source cannot be confirmed as reporting forward, not trailing, earnings.
- Halt and do not fabricate an options input if no options-chain provider is on file.
- Halt if a "new revenue opportunity" claim cannot be tied to a specific 10-Q line or explicit management statement.

STOP — hand to human. Everything past this line is interpretation, weighting, and decision, and belongs on the human card, not in this recipe.
